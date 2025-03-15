#!/bin/bash -e

## PREPARATION

echo $(pwd)
LOG_TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
mkdir -p logs_${LOG_TIMESTAMP}

cp experiments/kill_processes.py logs_${LOG_TIMESTAMP}

echo "[1] Start server broker"
sudo docker stop server-broker-rabbit
sudo docker rm server-broker-rabbit
sudo docker run --hostname broker --rm --name server-broker-rabbit -p 9000:5672 rabbitmq:3 > logs_${LOG_TIMESTAMP}/cloud_broker.log 2>&1 &
sleep 5

echo "[2] Start client broker"
sudo docker stop client-broker-rabbit
sudo docker rm client-broker-rabbit
sudo docker run --hostname broker --rm --name client-broker-rabbit -p 8000:5672 rabbitmq:3 > logs_${LOG_TIMESTAMP}/client_broker.log 2>&1 &
echo "Wait 30 seconds to ensure safe startup"
sleep 30

echo "Start event reader"
python3 -u -m event_reader > logs_${LOG_TIMESTAMP}/event_reader.log 2>&1 &
EVENT_READER_PID=$!
sleep 1

## CLOUD SIDE

echo "[3] Start cloud gateway"
python3 -u -m cloud_gateway.http_gateway > logs_${LOG_TIMESTAMP}/http_gateway.log 2>&1 &
echo $! >>  pids
sleep 1

echo "[4] Start cloud task manager"
rm cloud_task_manager/db/tasks.db
python3 -u -m cloud_task_manager.service_cloud_ml > logs_${LOG_TIMESTAMP}/service_cloud_ml.log 2>&1 &
echo $! >>  pids
sleep 1

echo "[5] Start download server"
python3 -u -m cloud_task_manager.host_tasks $(pwd)/cloud_task_manager &
echo $! >>  pids
sleep 1

echo "[6] Start user manager"
rm user_manager/db/users.db
python3 -u -m user_manager.service_user_manager > logs_${LOG_TIMESTAMP}/service_user_manager.log 2>&1 &
echo $! >>  pids
sleep 1

echo "[7] Create and run task at the server"
python3 -u -m cloud_task_manager.create_and_run_server_task
sleep 5

## CLIENT SIDE

echo "[8] Start client gateway"
python3 -u -m client_gateway.amqp_gateway > logs_${LOG_TIMESTAMP}/amqp_gateway.log 2>&1 &
echo $! >>  pids
sleep 1

echo "[9] Start client tasks manager" 
rm -rf client_task_manager/tasks/*
rm -rf client_task_manager/client_info/*
python3 -u -m client_task_manager.service_client_ml > logs_${LOG_TIMESTAMP}/service_client_ml.log 2>&1 &
echo $! >>  pids
sleep 10

echo "[10] Start second Flower client, which will trigger FL to starts"
python3 -u -m cloud_task_manager.tasks.task_4fe5.client cli
echo $! >>  pids
echo "Wait 2 minutes before gracefull termination" 
sleep 120

## FINALIZATION

python3 experiments/kill_processes.py
rm pids
sleep 5

kill $EVENT_READER_PID
sleep 5

cp events.json logs_${LOG_TIMESTAMP}
cp events.json experiments

cd experiments
echo "---- RESULTS ----" >> exp1_raw_times
python3 exp1_process_results.py >> exp1_raw_times

echo "Completed! Results are presented in experiments/exp1_raw_times"