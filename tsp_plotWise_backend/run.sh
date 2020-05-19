#!/bin/bash
docker run -d --network myapp_net --name tsp_plotwise_backend -p 8001:8001 repo/tsp-plotwise-backend:1.0.0 /bin/bash
