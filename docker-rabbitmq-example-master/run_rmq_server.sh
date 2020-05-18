docker network create myapp_net
docker run -d --network myapp_net --hostname rabbitmqhost \
   --name rabbitmq -p 15672:15672 -p 5672:5672 repo/rabbitmq-example-server:latest
