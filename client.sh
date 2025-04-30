#!/bin/bash
sudo docker stop client-broker-rabbit
sudo docker rm client-broker-rabbit
sudo docker run -d --hostname broker --rm --name client-broker-rabbit -p 8000:5672 rabbitmq:3
python3 -u -m client_gateway.amqp_gateway &
sleep 3 
python3 -u -m client_task_manager.service_client_ml
