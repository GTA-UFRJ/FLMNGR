echo "Start cloud gateway"
python -u -m cloud_gateway.http_gateway > http_gateway.log 2>&1 &
echo $! >>  pids
sleep 1

echo "Start cloud task manager"
python -u -m cloud_task_manager.service_cloud_ml >service_cloud_ml.log 2>&1 &
echo $! >>  pids
sleep 1

echo "Start download server"
python -u -m cloud_task_manager.host_tasks $(pwd)/cloud_task_manager &
echo $! >>  pids
sleep 1

echo "Start user manager"
python -u -m user_manager.service_user_manager > service_user_manager.log 2>&1 &
echo $! >>  pids
sleep 1


