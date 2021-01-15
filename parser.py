import csv

import psycopg2

connection = psycopg2.connect(user="postgres",
                              password="postgres",
                              host="127.0.0.1",
                              port="5432",
                              database="marakas")
cursor = connection.cursor()
insert_products = 'INSERT INTO products (title, asin) VALUES (%s, %s)'
with open(f'./products.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        cursor.execute(insert_products, (row['Title'], row['Asin']))
    connection.commit()
insert_reviews = '''INSERT INTO reviews (product_id, title, review) 
                           VALUES (%s, %s, %s)'''
with open(f'./reviews.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        product_id_query = 'SELECT id FROM products WHERE asin = %s'
        cursor.execute(product_id_query, (row['Asin'],))
        product_id = cursor.fetchone()
        cursor.execute(insert_reviews,
                       (product_id[0], row['Title'], row['Review']))
    connection.commit()
cursor.close()
connection.close()
