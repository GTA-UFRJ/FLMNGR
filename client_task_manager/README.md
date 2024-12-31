
# Client Task Manager

This microservice is responsible for:
* Periodically providing local client statistics for the cloud
* Periodically requesting available compatible tasks to the cloud
* Downloading client codes for training received tasks
* Starting and stopping Flower training services at the client in real time
* Logging Flower process information and errors (NOT YET IMPLEMENTED)

### Test Client Task Manager service

For testing the service with RabbitMQ broker, run in different terminals:

```shell
docker stop server-broker-rabbit
docker rm server-broker-rabbit
docker run -d --hostname broker --name server-broker-rabbit -p 9000:5672 rabbitmq:3
python -m cloud_task_manager.service_cloud_ml
```

```shell
python -m cloud_task_manager.create_and_run_server_task
python -m cloud_task_manager.host_tasks $(pwd)/cloud_task_manager
```

```shell
python -m cloud_gateway.http_gateway
```

```shell
docker stop client-broker-rabbit
docker rm client-broker-rabbit
docker run -d --hostname broker --name client-broker-rabbit -p 8000:5672 rabbitmq:3
python -m user_manager.service_user_manager
```

```shell
python -m client_gateway.amqp_gateway
```

```shell
python -m client_task_manager.service_client_ml
```

```shell
python -m cloud_task_manager.tasks.task_4fe5.client cli
```