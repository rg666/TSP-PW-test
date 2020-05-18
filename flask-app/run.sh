#!/bin/bash
docker run -d --network myapp_net --name flask-app -p 8000:8000 repo/flask-app:1.0.0 /bin/bash
