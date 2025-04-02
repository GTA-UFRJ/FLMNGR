#!/bin/bash -e

## PREPARATION

echo $(pwd)
LOG_TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
mkdir -p logs_${LOG_TIMESTAMP}

cp experiments/kill_processes.py logs_${LOG_TIMESTAMP}

echo "Start server broker"
sudo docker stop server-broker-rabbit
sudo docker rm server-broker-rabbit
sudo docker run --hostname broker --name server-broker-rabbit -p 9000:5672 rabbitmq:3 > logs_${LOG_TIMESTAMP}/cloud_broker.log 2>&1 &
sleep 5

echo "Start client broker"
sudo docker stop client-broker-rabbit
sudo docker rm client-broker-rabbit
sudo docker run --hostname broker --name client-broker-rabbit -p 8000:5672 rabbitmq:3 > logs_${LOG_TIMESTAMP}/client_broker.log 2>&1 &
echo "Wait 30 seconds to ensure safe startup"
sleep 30

echo "Start event reader"
python -u -m event_reader > logs_${LOG_TIMESTAMP}/event_reader.log 2>&1 &
echo $! >>  logs_${LOG_TIMESTAMP}/pids
sleep 1

## CLOUD SIDE

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

echo "Create tasks E and C and run tasks E and C"
cp -r cloud_task_manager/tasks/task_4fe5 cloud_task_manager/tasks/task_E
sed -i 's/8080/8081/g' cloud_task_manager/tasks/task_E/client.py
sed -i 's/8080/8081/g' cloud_task_manager/tasks/task_E/server.py
cp -r cloud_task_manager/tasks/task_4fe5 cloud_task_manager/tasks/task_C
python -u -m experiments.exp2_tasks_prep
sleep 10

## CLIENT SIDE

echo "Start client gateway"
python -u -m client_gateway.amqp_gateway > logs_${LOG_TIMESTAMP}/amqp_gateway.log 2>&1 &
echo $! >>  logs_${LOG_TIMESTAMP}/pids
sleep 1

echo "Start client tasks manager" 
rm -rf client_task_manager/tasks/*
rm -rf client_task_manager/client_info/*
python -u -m client_task_manager.service_client_ml > logs_${LOG_TIMESTAMP}/service_client_ml.log 2>&1 &
echo $! >>  logs_${LOG_TIMESTAMP}/pids
sleep 30

## FINALIZATION

cd logs_${LOG_TIMESTAMP}
python kill_processes.py
sleep 5

cd ..
cp events.json logs_${LOG_TIMESTAMP}
cp events.json experiments
rm -r cloud_task_manager/tasks/task_E
rm -r cloud_task_manager/tasks/task_C

cd experiments
echo "---- RESULTS ----" >> exp2_raw_times
python exp2_process_results.py >> exp2_raw_times

echo "Completed! Results are presented in experiments/exp2_raw_times"