
check_active() {
	#echo ""
	#ps aux | grep "$1"
	if [[ $(ps aux | grep "$1" | wc -l) -eq 1 ]]; then
		echo "python service $1 inactive"
	fi 
}

check_active "event_reader"
check_active "cloud_gateway.http_gateway"
check_active "cloud_task_manager.service_cloud_ml"
check_active "cloud_task_manager.host_tasks"
check_active "user_manager.service_user_manager"
check_active "client_gateway.http_gateway"
check_active "client_gateway.amqp_gateway"
check_active "client_task_manager.service_client_ml"

