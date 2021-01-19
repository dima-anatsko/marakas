import csv
import click

import psycopg2


SETTING_DB = {
    'user': 'postgres',
    'password': 'postgres',
    'host': '127.0.0.1',
    'port': '5432',
    'database': 'marakas'
}


def create_database(cursor):
    create_table_products = '''CREATE TABLE products
        (id            SERIAL           PRIMARY KEY,
         title         VARCHAR(255)     NOT NULL,
         asin          VARCHAR(50)      NOT NULL UNIQUE); '''
    cursor.execute(create_table_products)
    create_table_reviews = '''CREATE TABLE reviews
        (id            SERIAL       PRIMARY KEY,
         product_id    INTEGER,
         title         VARCHAR(255) NOT NULL,
         review        TEXT         NOT NULL,
         FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE);'''
    cursor.execute(create_table_reviews)


def insert_products(file, cursor):
    insert_query = 'INSERT INTO products (title, asin) VALUES (%s, %s)'
    reader = csv.DictReader(file)
    for row in reader:
        cursor.execute(insert_query, (row['Title'], row['Asin']))
    return f'The data is inserted from the file:{file.name} into table products'


def insert_reviews(file, cursor):
    insert_query = '''INSERT INTO reviews (product_id, title, review) 
                               VALUES (%s, %s, %s)'''
    reader = csv.DictReader(file)
    product_id_query = 'SELECT id FROM products WHERE asin = %s'
    for row in reader:
        cursor.execute(product_id_query, (row['Asin'],))
        product_id = cursor.fetchone()
        cursor.execute(insert_query,
                       (product_id[0], row['Title'], row['Review']))
    return f'The data is inserted from the file:{file.name} into table reviews'


def wrong_option(*args, **kwargs):
    return 'Wrong option'


@click.command()
@click.argument('file', type=click.File('r'))
@click.option('-p', '--products', 'table_name', flag_value='products',
              help='Set this option if you import in table "products"')
@click.option('-r', '--reviews', 'table_name', flag_value='reviews',
              help='Set this option if you import in table "reviews"')
@click.option('-c/-n', '--create/--no-create', 'create_db', default=False,
              help="Choice '-c' if you want to create tables in the database")
def cli(table_name, file, create_db):
    """
    Script for importing data from a csv file to a database

    :param table_name: this parameter points which table to import to data
    :param file: this parameter points path to the file
    :param create_db: this parameter points path to the file
    :return: was the operation successful
    """
    choice_table = {'products': insert_products, 'reviews': insert_reviews}
    connection = psycopg2.connect(**SETTING_DB)
    cursor = connection.cursor()
    if create_db:
        create_database(cursor)
        connection.commit()
        click.echo('The database was created successfully')
    report = choice_table.get(table_name, wrong_option)(file, cursor)
    connection.commit()
    cursor.close()
    connection.close()
    click.echo(report)


if __name__ == "__main__":
    cli()
