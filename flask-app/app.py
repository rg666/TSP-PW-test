from __future__ import print_function, unicode_literals
#Personal GUnicorn
import multiprocessing
import gunicorn.app.base
import os
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from random import randint
import pika
import uuid
import json
from flask import Flask, request, Response

RMQ_HOST = str(os.environ.get("RMQ_HOST", None))
RMQ_USER = str(os.environ.get("RMQ_USER", None))
RMQ_PASSWORD = str(os.environ.get("RMQ_PASSWORD", None))


app = Flask(__name__)

class TSPRpcClient(object):
    def __init__(self):
        
        credentials = pika.PlainCredentials(username=RMQ_USER, password=RMQ_PASSWORD) 
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host = RMQ_HOST,credentials=credentials))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

def newlatlong():
   return randint(0,100),randint(0, 100)

def create_random_data_model(numberofpoints):
    data = {}
    #Random lat-lon generation
    points = (newlatlong() for x in range(numberofpoints))
    #generator to list type
    points = list(points)
    generated_lat_longs = ('Randomly generated lat-longs:   [%s]' % ', '.join(map(str, points)))
    # Locations in block units
    data['locations'] = points
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data, generated_lat_longs

def create_data_model(list_points):
    data = {}
    points = list(list_points)
    # Locations in block units
    data['locations'] = points
    data['num_vehicles'] = 1
    data['depot'] = 0
    print(data)
    return data

def main_random_tsp(num_of_points):
    flask_response = ''
    # Instantiate the data problem.
    data, generated_lat_longs = create_random_data_model(num_of_points)
    in_msg = json.dumps(data)
    tsp_rpc = TSPRpcClient()
    rpc_response = str(tsp_rpc.call(in_msg))
    flask_response = generated_lat_longs + '  ' + rpc_response
    print(flask_response)
    return flask_response

def main_generate_tsp(list_points):
    flask_response = ''
    data = create_data_model(list_points)
    in_msg = json.dumps(data)
    tsp_rpc = TSPRpcClient()
    rpc_response = str(tsp_rpc.call(in_msg))
    flask_response = rpc_response
    print(flask_response)
    return flask_response


@app.route('/',methods=['GET'])
def hello():
    return "Hello there! Please refer tests documentation to use the API.", 200

@app.route('/randomtsproute',methods=['GET'])
def randomTSP():
    num_of_points = int(request.args.get('numofpoints'))
    if not isinstance(num_of_points, int):
        return Response("Please check your input format", status = 400)
    flask_response = main_random_tsp(num_of_points)
    resp = Response(flask_response,status = 200)
    return resp

@app.route('/generatetsproute',methods=['GET'])
def generateTSP():
    int_points_list = []
    pointslist = str(request.args.get('pointslist')).split(';')
    #Convert the string input list to int list
    try:
        for i in pointslist:
            i = i.replace('(','').replace(')','')
            results = [int(j) for j in i.split(',')]
            int_points_list.append(results)
    except:
        return Response("Please check your input format", status = 400)       
    flask_response = main_generate_tsp(int_points_list)  
    resp = Response(flask_response,status = 200)
    return resp

############################################     FLASK APP RUN OVER GUNICORN     #######################################################
def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    options = {
        'bind': '%s:%s' % ('0.0.0.0', '8000'),
        'workers': number_of_workers(),
        'timeout' : 120 # 2 minutes timeout
    }
    # Modification 3: pass Flask app instead of handler_app
    StandaloneApplication(app, options).run()
