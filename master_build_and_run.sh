#!/bin/bash

cd ./docker-rabbitmq-example-master
sh ./build_rmq_server.sh
sh ./run_rmq_server.sh

cd ../flask-app
sh ./build.sh
sh ./run.sh

cd ../tsp_plotWise_backend
sh ./build.sh
sh ./run.sh

