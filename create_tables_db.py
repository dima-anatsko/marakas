import psycopg2


connection = psycopg2.connect(user="postgres",
                              password="postgres",
                              host="127.0.0.1",
                              port="5432",
                              database="marakas")
cursor = connection.cursor()
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
connection.commit()
cursor.close()
connection.close()
