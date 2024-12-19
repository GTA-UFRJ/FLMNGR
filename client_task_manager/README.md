
# Cloud Task Manager

This microservice is responsible for:
* Periodically providing local client statistics for the cloud
* Periodically requesting available compatible tasks to the cloud
* Downloading client codes for training received tasks
* Starting and stopping Flower training services at the client in real time
* Logging Flower process information and errors (NOT YET IMPLEMENTED)

For more information about Flower Tasks Daemon Library (FTDL), read Cloud Task Manager README file

### Test Stub Client Task Manager service

Client Task Manager is a component that receives messages through a RabbitMQ
broker for RPC function execution. This broker logic is not yet implemented. 
The responsability of this service is to manage client tasks being started
and finished. 

```
python -m test_client_ml_logic
```

### Test Client Task Manager service

For testing the service with RabbitMQ broker, run:

```
docker stop broker-rabbit
docker rm broker-rabbit
docker run -d --hostname broker --name broker-rabbit -p 5672:5672 rabbitmq:3
cd ../user_manager
python -m service_user_manager
```

In other terminal:
```
cd cloud_task_manager
python -m service_cloud_ml
```

In other terminal:
```
cd cloud_task_manager
python host_tasks.py $(pwd)
python -m create_and_run_server_task
```

In other terminal:
```
cd client_task_manager
python -m service_client_ml
```

In other terminal:
```
cd client_task_manager
python -m tasks.task_4fe5.client cli
```