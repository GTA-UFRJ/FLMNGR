#!/bin/bash 

echo "Start second Flower client, which will trigger FL to starts"
python -u -m cloud_task_manager.tasks.task_4fe5.client cli
echo $! >>pids
