from flask import Flask, Response, jsonify, request
from pymongo import MongoClient
from middleware import setup_metrics
from jaeger_client import Config
from flask_opentracing import FlaskTracer
import os
import logging
import json
import jwt
import prometheus_client
import time
import opentracing

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
setup_metrics(app)

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

client = MongoClient('cataloguedb', 27017)
db = client.productDb

def initialize_tracer():
  config = Config(
      config={
          'sampler': {'type': 'const', 'param': 1}
      },
      service_name='catalogue-with-time-delay')
  return config.initialize_tracer()

#flask_tracer = FlaskTracer(initialize_tracer, True, app)
tracer = FlaskTracer(initialize_tracer)

@app.route('/', methods=['POST'])
@tracer.trace()
def catalogue():
   parent_span = tracer.get_span()
   with opentracing.tracer.start_span('Sleep', child_of=parent_span) as span:
      time.sleep(5)
   logger.info('Entered Catalogue service to list the products')
   try:
    logger.info("Authenticating token")
    with opentracing.tracer.start_span('Token Authentication', child_of=parent_span) as span:
       token = request.headers['access-token']
       jwt.decode(token, app.config['SECRET_KEY'])
       logger.info("Token authentication successful")
    try:
       with opentracing.tracer.start_span('Fetching Products', child_of=parent_span) as span:
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
@tracer.trace()
def price():
   parent_span = tracer.get_span()
   with opentracing.tracer.start_span('Loading Data From Request', child_of=parent_span) as span:
      logger.info("Entered the Catalogue service to fetch price of products")
      data = json.loads(request.data)
      productId = data['productId']
   try:
      with opentracing.tracer.start_span('Fetching Product Price', child_of=parent_span) as span:
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


app.run(port=5001, debug=True, host='0.0.0.0')
