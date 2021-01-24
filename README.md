## Python developer test task (Flask)

**Task**:

You need to write a web application in which:
   1. Parse two 2 files (Products.csv (columns: Title,Asin), Reviews.csv ( columns: Asin,Title,Review)), save data to the database (to use Postgresql, one-to-many or many-to-many relationships to choose from). Parsing and saving to the database can be implemented using the console command.
   2. Based on Flask, create an endpoint (GET) API that will return data in json format with the following content:
        by product id, give information about this product (ASIN, Title) and Reviews of this product with pagination.
        It is advisable to create caching for GET endpoint.
   3. Create a second endpoint API (PUT), which will write a new Review for the product to the database (by id).

**Project description**

The project is written in python 3.9  
To start the project, copy:

`git clone https://github.com/dima-anatsko/marakas.git`

Go to your virtual environment and install the requirements:

`pip install -r requirements.txt`

You need to create a database structure and fill it with data.  
To do this, use the utility parser.py  
Help for the parser:  `python parser.py --help`  
Creating a database and importing products:

`python parser.py -c -p products.csv`

Then we import the reviews:

`python parser.py -r ./reviews.csv`

    Note: You can't import reviews for products that aren't in the database

To start the server on Flask, input in the command line:

`python app.py`

Examples of queries:

`curl GET 'http://127.0.0.1:5000/marakas/api/v1.0/products/9?page=1&offset=1'`
  
* 9 - this is the product id
* page - overview page
* offset - number of reviews on page

In response, you will receive a product with a list of reviews.

To add a new review, you need to send the following request:

        curl PUT 'http://127.0.0.1:5000/marakas/api/v1.0/products/2'
        --header 'Content-Type: application/json'
        --data-raw '{
            "title": "amazing toys",
            "review": "Most inconsiderate, I must say."
        }'

To get a list of all products, send the following request:

`curl GET 'http://127.0.0.1:5000/marakas/api/v1.0/products/'`
