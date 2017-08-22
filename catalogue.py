from flask import Flask, Response, jsonify, request
import os
import logging
import json
from pymongo import MongoClient
import jwt

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

client = MongoClient('cataloguedb', 27017)
db = client.productDb

@app.route('/', methods=['POST'])
def catalogue():
   logger.info('Entered Catalogue service to list the products')
   try:
    logger.info("Authenticating token")
    token = request.headers['access-token']
    jwt.decode(token, app.config['SECRET_KEY'])
    logger.info("Token authentication successful")
    try:
       db.product.drop()
       product = {'_id': 1, 'name': 'nike', 'category': 'shoe', 'price': 11, 'location': '/static/shoe.jpg'}
       logger.debug("Product: {}".format(product))
       db.product.insert(product)
       logger.info("Inserted successfully")
       product = {'_id': 2, 'name': 'iphone', 'category': 'mobile', 'price': 100, 'location': '/static/mobile.jpg'}
       db.product.insert(product)
       logger.info("Inserted Successfully")
       product = {'_id': 3, 'name': 'titan', 'category': 'watch', 'price': 50, 'location': '/static/watch.jpeg'}
       db.product.insert(product)   
       product = {'_id': 4, 'name': 'philips', 'category': 'speaker', 'price': 75, 'location': '/static/speaker.jpeg'}
       db.product.insert(product)
       product = {'_id': 5, 'name': 'adidas', 'category': 'tshirt', 'price': 60, 'location': '/static/tshirt.jpeg'}
       db.product.insert(product)
       product = {'_id': 6, 'name': 'sony', 'category': 'tv', 'price': 1000, 'location': '/static/tv.jpg'}
       db.product.insert(product)
       product = {'_id': 7, 'name': 'seagate', 'category': 'harddisk', 'price': 200, 'location': '/static/harddisk.jpg'}
       db.product.insert(product)
       product = {'_id': 8, 'name': 'journal', 'category': 'book', 'price': 30, 'location': '/static/journal.jpg'}
       db.product.insert(product)  
       products = list(db.product.find())
       logger.info("Fetched products {}".format(products))
       return jsonify({'productDetails': products}), 200
    except:
        logger.warning("Failed to execute query. Leaving Catalogue service")
        response = Response(status=500)
        return response

   except:
      logger.warning("Token authentication failed. Leavng Catalogue")    
      response = Response(status=500)
      return response

@app.route('/price', methods=['POST'])
def price():
   logger.info("Entered the Catalogue service to fetch price of products")
   data = json.loads(request.data)
   productId = data['productId']
   try:
      product = db.product.find_one({'_id': productId})
      price = product['price']
      return jsonify({"price": price}), 200
   except:
      logger.warning("Execution failed")
      response.status = 500
      return response

app.run(port=5001, debug=True, host='0.0.0.0')
