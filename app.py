import psycopg2
from flask import Flask, jsonify, request
from flask_caching import Cache
import parser


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
connection = psycopg2.connect(**parser.SETTING_DB)
cursor = connection.cursor()

PRODUCT_VIEWS_QUERY = """
SELECT products.id, products.title, asin, reviews.title, review
FROM products
LEFT JOIN reviews ON products.id = reviews.product_id
WHERE products.id = %s
ORDER BY reviews.title"""

PRODUCTS_QUERY = "SELECT id, title, asin FROM products"

INSERT_REVIEW = """INSERT INTO reviews (product_id, title, review) 
VALUES (%s, %s, %s);"""

GET_ID_PRODUCT = "SELECT id FROM products WHERE id = %s"


def make_cache_key():
    return request.url


@cache.cached(timeout=60, key_prefix=make_cache_key)
def get_data(product_id, page, offset):
    cursor.execute(PRODUCT_VIEWS_QUERY, (product_id,))
    product_reviews = cursor.fetchall()
    if product_reviews:
        product = dict(zip(('id', 'product_title', 'asin'), product_reviews[0]))
        reviews = []
        for data in product_reviews:
            if review := get_review(*data):
                reviews.append(review)
        count_reviews = len(reviews)
        response = create_links(count_reviews, page, offset)
        start = (page - 1) * offset
        reviews_pagination = reviews[start: start + offset]
        response.update({'product': product, 'reviews': reviews_pagination})
        return response
    return None


def get_review(*args):
    if args[3:5] == (None, None):
        return None
    return dict(zip(('review_title', 'review'), args[3:5]))


def create_links(count_reviews, page, offset):
    count_page = count_reviews // offset + int((count_reviews % offset) and 1)
    response = {'count_page': count_page}
    host = request.host_url[:-1]
    path = request.path
    links = {'self': f'{host}{request.full_path}'}
    if page > 1:
        links['first'] = f'{host}{path}?page=1&offset={offset}'
        links['prev'] = f'{host}{path}?page={page - 1}&offset={offset}'
    if page < count_page:
        links['last'] = f'{host}{path}?page={count_page}&offset={offset}'
        links['next'] = f'{host}{path}?page={page + 1}&offset={offset}'
    response.update({'links': links})
    return response


@app.route('/marakas/api/v1.0/products/', methods=['GET'])
def get_products():
    cursor.execute(PRODUCTS_QUERY)
    products = cursor.fetchall()
    response = []
    for product_id, title, asin in products:
        response.append({'id': product_id, 'title': title, 'asin': asin})
    return jsonify({'products': response})


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
    if not validate_product(product_id):
        return jsonify({'error': 'no product with this id'}), 400
    if not request.json or not validate_data(request.json):
        return jsonify({'error': 'bad request'}), 400
    review = (product_id,
              request.json['title'],
              request.json['review'])
    cursor.execute(INSERT_REVIEW, review)
    connection.commit()
    return jsonify({'review': review}), 201


def validate_product(product_id):
    cursor.execute(GET_ID_PRODUCT, (product_id,))
    product = cursor.fetchone()
    return True if product else False


def validate_data(data):
    if data.get('title') and data.get('review'):
        return True
    return False


if __name__ == '__main__':
    app.run(debug=True)
