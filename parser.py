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
              default=True)
@click.option('-r', '--reviews', 'table_name', flag_value='reviews')
def main(table_name, file):
    choice_table = {'products': insert_products, 'reviews': insert_reviews}
    connection = psycopg2.connect(**SETTING_DB)
    cursor = connection.cursor()
    report = choice_table.get(table_name, wrong_option)(file, cursor)
    connection.commit()
    cursor.close()
    connection.close()
    click.echo(report)


if __name__ == "__main__":
    main()
