#!/bin/bash
docker stop tsp_plotwise_backend flask-app rabbitmq
docker rm tsp_plotwise_backend flask-app rabbitmq
docker rmi repo/rabbitmq-example-server:latest repo/flask-app:1.0.0 repo/tsp-plotwise-backend:1.0.0


