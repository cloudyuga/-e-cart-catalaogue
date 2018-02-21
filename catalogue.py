from flask import Flask, Response, jsonify, request
from pymongo import MongoClient
from middleware import setup_metrics
from jaeger_client import Config
from flask_opentracing import FlaskTracers
import os
import logging
import json
import jwt
import prometheus_client

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
setup_metrics(app)

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

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
   
@app.route('/metrics')
def metrics():
    return Response(prometheus_client.generate_latest(), mimetype=CONTENT_TYPE_LATEST)

def initialize_tracer():
  config = Config(
      config={
          'sampler': {'type': 'const', 'param': 1}
      },
      service_name='catalogue')
  return config.initialize_tracer()

flask_tracer = FlaskTracer(initialize_tracer, True, app)

app.run(port=5001, debug=True, host='0.0.0.0')
