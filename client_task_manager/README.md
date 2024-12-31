
# Client Task Manager

This microservice is responsible for:
* Periodically providing local client statistics for the cloud
* Periodically requesting available compatible tasks to the cloud
* Downloading client codes for training received tasks
* Starting and stopping Flower training services at the client in real time
* Logging Flower process information and errors (NOT YET IMPLEMENTED)

### Test Client Task Manager service

For testing the service with RabbitMQ broker, run:

```
docker stop client_broker-rabbit
docker rm client_broker-rabbit
docker run -d --hostname broker --name client_broker-rabbit -p 8000:5672 rabbitmq:3
python -m cloud_task_manager.service_cloud_ml
```

In other terminal start download server:
```
python -m cloud_task_manager.host_tasks.py $(pwd)/cloud_task_manager
```

In other terminal:
```
python -m cloud_task_manager.create_and_run_server_task
python -m user_manager.service_user_manager
```

In other terminal:
```
python -m client_task_manager.service_client_ml
```

In other terminal:
```
python -m cloud_task_manager.tasks.task_4fe5.client cli
```