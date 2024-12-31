
# Cloud Task Manager

This microservice is responsible for:
* Implementing CRUD operations over all tasks, running or not
* Mantaining client and server codes for inference, training, and aggregation for all tasks
* Starting and stopping Flower aggreagtion services at the server by demand 
* Logging Flower process information and errors (NOT YET IMPLEMENTED)

### Test Flower task

In one terminal, run the Flower server
```
python -m cloud_task_manager.tasks.task_4fe5.server cli
```

In two other terminals, run two Flower clients after waiting the server to start
```
python -m cloud_task_manager.tasks.task_4fe5.client cli
```

```
python -m cloud_task_manager.tasks.task_4fe5.client cli
```

### Test Cloud Task Manager service

For testing the service with RabbitMQ broker, run:

```shell
docker stop broker-rabbit
docker rm broker-rabbit
docker run -d --hostname broker --name broker-rabbit -p 9000:5672 rabbitmq:3
python -m cloud_task_manager.test_cloud_ml_logic
```