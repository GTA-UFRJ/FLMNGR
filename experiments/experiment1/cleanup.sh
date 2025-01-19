
rm cloud_task_manager/db/tasks.db

rm -rf client_task_manager/tasks/*
rm -rf client_task_manager/client_info/*

rm user_manager/db/users.db

python3 experiments/kill_processes.py
rm pids
