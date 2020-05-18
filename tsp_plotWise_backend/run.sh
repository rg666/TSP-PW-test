#!/bin/bash
docker run -d --network myapp_net --name tsp_plotwise_backend repo/tsp-plotwise-backend:1.0.0 /bin/bash
