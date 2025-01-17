#!/bin/bash

# removing brokereersz
sudo docker stop client-broker-rabbit
sudo docker stop server-broker-rabbit
sudo docker rm client-broker-rabbit
sudo docker rm server-broker-rabbit

# Killing active python processes
python3 experiments/kill_processes.py pids

# Removing files 
rm cloud_task_manager/db/tasks.db
rm user_manager/db/users.db
rm -rf client_task_manager/tasks/*
rm -rf client_task_manager/client_info/*

rm pids
