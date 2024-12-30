
# Client Task Manager

This microservice is responsible for:
* Periodically providing local client statistics for the cloud
* Periodically requesting available compatible tasks to the cloud
* Downloading client codes for training received tasks
* Starting and stopping Flower training services at the client in real time
* Logging Flower process information and errors (NOT YET IMPLEMENTED)

For more information about Flower Tasks Daemon Library (FTDL), read Cloud Task Manager README file

### Test Client Task Manager service

For testing the service with RabbitMQ broker, run:

```
docker stop server-broker-rabbit
docker rm server-broker-rabbit
docker run -d --hostname broker --name server-broker-rabbit -p 9000:5672 rabbitmq:3
docker stop client-broker-rabbit
docker rm client-broker-rabbit
docker run -d --hostname broker --name client-broker-rabbit -p 8000:5672 rabbitmq:3
python -m cloud_task_manager.service_cloud_ml
```

In other terminal start client gateway:
```
python client_gateway.amqp_gateway
```

In other terminal start cloud gateway:
```
python cloud_gateway.http_gateway
```

In other terminal start download server:
```
python cloud_task_manager.host_tasks.py $(pwd)
```

In other terminal:
```
python -m cloud_task_manager.create_and_run_server_task
```

In other terminal:
```
python -m client_task_manager.service_client_ml
```

In other terminal:
```
python -m cloud_task_manager.tasks.task_4fe5.client cli
```