#!/usr/bin/env python
from __future__ import print_function
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from random import randint
import pika
import uuid
import json
import os

RMQ_HOST = str(os.environ.get("RMQ_HOST", None))
RMQ_USER = str(os.environ.get("RMQ_USER", None))
RMQ_PASSWORD = str(os.environ.get("RMQ_PASSWORD", None))

credentials = pika.PlainCredentials(username = RMQ_USER, password = RMQ_PASSWORD)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RMQ_HOST,credentials=credentials))

channel = connection.channel()
channel.queue_declare(queue='rpc_queue')

def compute_euclidean_distance_matrix(locations):
    #Creates callback to return distance between points.
    distances = {}
    for from_counter, from_node in enumerate(locations):
        distances[from_counter] = {}
        for to_counter, to_node in enumerate(locations):
            if from_counter == to_counter:
                distances[from_counter][to_counter] = 0
            else:
                # Euclidean distance
                distances[from_counter][to_counter] = (int(
                    math.hypot((int(from_node[0]) - int(to_node[0])),
                               (int(from_node[1]) - int(to_node[1])))))
    return distances


def get_solution(manager, routing, solution):
    #Returns solution
    index = routing.Start(0)
    plan_output = 'Optimal Route:     '
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += ' {} ->'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}     '.format(manager.IndexToNode(index))
    return plan_output

def calculate_tsp(data):
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['locations']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    distance_matrix = compute_euclidean_distance_matrix(data['locations'])

    def distance_callback(from_index, to_index):
        #Returns the distance between the two nodes.
        #Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        out = get_solution(manager, routing, solution)      
    
    return out
def main():
    def on_request(ch, method, props, body):
        n = body
        data = json.loads(body)
        response = calculate_tsp(data)
        ch.basic_publish(exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id = \
                                                            props.correlation_id),
                        body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
    print(" [x] Awaiting RPC requests")
    channel.start_consuming()
    
if __name__ == '__main__':
    main()