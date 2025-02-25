#!/bin/bash -e

## PREPARATION
while true; do
	echo $(pwd)
	LOG_TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
	mkdir -p logs_${LOG_TIMESTAMP}

	cp experiments/kill_processes.py logs_${LOG_TIMESTAMP}

	#echo "Start server broker"
	#sudo docker run --hostname broker --rm --name server-broker-rabbit -p 9000:5672 rabbitmq:3 > logs_${LOG_TIMESTAMP}/cloud_broker.log 2>&1 &
	#sleep 5

	#echo "Start client broker"
	#sudo docker run --hostname broker --rm --name client-broker-rabbit -p 8000:5672 rabbitmq:3 > logs_${LOG_TIMESTAMP}/client_broker.log 2>&1 &
	#sleep 15

	## CLOUD SIDE

	echo "Start cloud gateway"
	python -u -m cloud_gateway.http_gateway > logs_${LOG_TIMESTAMP}/http_gateway.log 2>&1 &
	echo $! >>  pids
	sleep 1

	echo "Start cloud task manager"
	python -u -m cloud_task_manager.service_cloud_ml > logs_${LOG_TIMESTAMP}/service_cloud_ml.log 2>&1 &
	echo $! >>  pids
	sleep 1

	echo "Start download server"
	python -u -m cloud_task_manager.host_tasks $(pwd)/cloud_task_manager &
	echo $! >>  pids
	sleep 1

	echo "Start user manager"
	python -u -m user_manager.service_user_manager > logs_${LOG_TIMESTAMP}/service_user_manager.log 2>&1 &
	echo $! >>  pids
	sleep 1

	echo "Create and run task at the server"
	python -u -m cloud_task_manager.create_and_run_server_task
	sleep 5

	## CLIENT SIDE

	echo "Start client gateway"
	python -u -m client_gateway.amqp_gateway > logs_${LOG_TIMESTAMP}/amqp_gateway.log 2>&1 &
	echo $! >>  pids
	sleep 1

	echo "Start client tasks manager" 
	python -u -m client_task_manager.service_client_ml > logs_${LOG_TIMESTAMP}/service_client_ml.log 2>&1 &
	echo $! >>  pids
	sleep 10

	echo "Start second Flower client, which will trigger FL to starts"
	python -u -m cloud_task_manager.tasks.task_4fe5.client cli
	echo $! >>  pids
	sleep 20

	## FINALIZATION

	rm cloud_task_manager/db/tasks.db

	rm -rf client_task_manager/tasks/*
	rm -rf client_task_manager/client_info/*

	rm user_manager/db/users.db

	python3 experiments/kill_processes.py
	rm pids
	sleep 5
	
	#echo "Start event reader"
	#python -u -m event_reader > logs_${LOG_TIMESTAMP}/event_reader.log 2>&1 &
	#EVENT_READER_PID=$!
	#sleep 1

	#kill $EVENT_READER_PID
	#sleep 5

	#sudo docker stop server-broker-rabbit
	#sudo docker stop client-broker-rabbit

done
