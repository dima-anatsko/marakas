from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:postgres@localhost:5432/marakas'  # noqa
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    asin = db.Column(db.String(50), unique=True, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Product {self.id}>'


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    review = db.Column(db.Text, nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),
                           nullable=False)
    product = db.relationship('Product',
                              backref=db.backref('reviews', lazy=True))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Review {self.id}>'


def make_cache_key():
    return request.url


@cache.cached(timeout=60, key_prefix=make_cache_key)
def get_data(product_id, page, offset):
    product = Product.query.get(product_id)
    reviews_paginate = Review.query.filter_by(
        product_id=product_id
    ).paginate(page=page, per_page=offset)
    if product:
        reviews = [review.as_dict() for review in reviews_paginate.items]
        response = {'product': product.as_dict(), 'reviews': reviews}
        if reviews:
            links = create_links(reviews_paginate)
            response.update(links)
        return response
    return None


def create_links(reviews):
    offset = reviews.per_page
    response = {'total_pages': reviews.pages}
    host = request.host_url[:-1]
    path = request.path
    links = {'self': f'{host}{request.full_path}'}
    if reviews.has_prev:
        links['first'] = f'{host}{path}?page=1&offset={offset}'
        links['prev'] = f'{host}{path}?page={reviews.prev_num}&offset={offset}'
    if reviews.has_next:
        links['last'] = f'{host}{path}?page={reviews.pages}&offset={offset}'
        links['next'] = f'{host}{path}?page={reviews.next_num}&offset={offset}'
    response.update({'links': links})
    return response


@app.route('/marakas/api/v1.0/products/', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_list = [product.as_dict() for product in products]
    return jsonify({'products': products_list})


@app.route('/marakas/api/v1.0/products/<int:product_id>', methods=['GET'])
def index(product_id):
    page = request.args.get('page', default=1, type=int)
    offset = request.args.get('offset', default=1, type=int)
    data = get_data(product_id, page, offset)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Not found'}), 404


@app.route('/marakas/api/v1.0/products/<int:product_id>', methods=['PUT'])
def create_review(product_id):
    if not Product.query.get(product_id):
        return jsonify({'error': 'no product with this id'}), 400
    if not request.json or not validate_data(request.json):
        return jsonify({'error': 'bad request'}), 400
    review = Review(title=request.json['title'],
                    review=request.json['review'],
                    product_id=product_id)
    db.session.add(review)
    db.session.commit()
    return jsonify({'review': review.as_dict()}), 201


def validate_data(data):
    if data.get('title') and data.get('review'):
        return True
    return False


if __name__ == '__main__':
    app.run(debug=True)
