#!/bin/bash -e

echo $(pwd)
LOG_TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
mkdir -p logs_${LOG_TIMESTAMP}

cp experiments/kill_processes.py logs_${LOG_TIMESTAMP}

echo "Start server broker"
docker stop server-broker-rabbit
docker rm server-broker-rabbit
docker run --hostname broker --name server-broker-rabbit -p 9000:5672 rabbitmq:3 > logs_${LOG_TIMESTAMP}/cloud_broker.log 2>&1 &
sleep 5

echo "Start cloud gateway"
python -u -m cloud_gateway.http_gateway > logs_${LOG_TIMESTAMP}/http_gateway.log 2>&1 &
echo $! >>  logs_${LOG_TIMESTAMP}/pids
sleep 1

echo "Start cloud task manager"
rm cloud_task_manager/db/tasks.db
python -u -m cloud_task_manager.service_cloud_ml > logs_${LOG_TIMESTAMP}/service_cloud_ml.log 2>&1 &
echo $! >>  logs_${LOG_TIMESTAMP}/pids
sleep 1

echo "Start download server"
python -u -m cloud_task_manager.host_tasks $(pwd)/cloud_task_manager &
echo $! >>  logs_${LOG_TIMESTAMP}/pids
sleep 1

echo "Start user manager"
rm user_manager/db/users.db
python -u -m user_manager.service_user_manager > logs_${LOG_TIMESTAMP}/service_user_manager.log 2>&1 &
echo $! >>  logs_${LOG_TIMESTAMP}/pids
sleep 1

echo "Create and run task at the server"
python -u -m cloud_task_manager.create_and_run_server_task
sleep 5

echo "Start client broker"
docker stop client-broker-rabbit
docker rm client-broker-rabbit
docker run --hostname broker --name client-broker-rabbit -p 8000:5672 rabbitmq:3 > logs_${LOG_TIMESTAMP}/client_broker.log 2>&1 &
sleep 5

echo "Start client gateway"
python -u -m client_gateway.amqp_gateway > logs_${LOG_TIMESTAMP}/amqp_gateway.log 2>&1 &
echo $! >>  logs_${LOG_TIMESTAMP}/pids
sleep 1

echo "Start client tasks manager" 
rm -rf client_task_manager/tasks/*
rm -rf client_task_manager/client_info/*
python -u -m client_task_manager.service_client_ml > logs_${LOG_TIMESTAMP}/service_client_ml.log 2>&1 &
echo $! >>  logs_${LOG_TIMESTAMP}/pids
sleep 1

echo "Start second Flower client, which will trigger FL to starts"
python -u -m cloud_task_manager.tasks.task_4fe5.client cli 
echo $! >>  logs_${LOG_TIMESTAMP}/pids

cd logs_${LOG_TIMESTAMP}
python kill_processes.py