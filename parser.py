import csv
import click

from app import db, Product, Review


def insert_products(file):
    reader = csv.DictReader(file)
    products = [Product(title=row['Title'], asin=row['Asin']) for row in reader]
    db.session.add_all(products)
    return f'The data is inserted from the file:{file.name} into table products'


def insert_reviews(file):
    reader = csv.DictReader(file)
    for row in reader:
        product = Product.query.filter_by(asin=row['Asin']).first()
        if product:
            review = Review(title=row['Title'],
                            review=row['Review'],
                            product=product)
            db.session.add(review)
    return f'The data is inserted from the file:{file.name} into table reviews'


def wrong_option(*args, **kwargs):
    return 'Wrong option'


@click.command()
@click.argument('file', type=click.File('r'))
@click.option('-p', '--products', 'table_name', flag_value='products',
              help='Set this option if you import in table "products"')
@click.option('-r', '--reviews', 'table_name', flag_value='reviews',
              help='Set this option if you import in table "reviews"')
def cli(table_name, file):
    """
    Script for importing data from a csv file to a database

    :param table_name: this parameter points which table to import to data
    :param file: this parameter points path to the file
    :return: was the operation successful
    """
    choice_table = {'products': insert_products, 'reviews': insert_reviews}
    db.create_all()
    report = choice_table.get(table_name, wrong_option)(file)
    db.session.commit()
    click.echo(report)


if __name__ == "__main__":
    cli()
