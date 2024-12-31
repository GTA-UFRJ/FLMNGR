
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
docker stop broker-rabbit
docker rm broker-rabbit
docker run -d --hostname broker --name broker-rabbit -p 5672:5672 rabbitmq:3
cd ../cloud_task_manager
python -m service_cloud_ml
```
 """
    Call endpoint function in another microservice
    
    :param func_name: function name. Usually starts with rpc_exec_... for preventing confusion
    :type func_name: str

    :param request: JSON request with function parameters following JSON schema
    :type request: dict

    :return: JSON response with status and return fields or status and exception fields
    :rtype: dict 

    :raises: pika.exceptions.AMQPConnectionError
    """
    while True: 
        try:
            rpc_client = RpcClient(func_name)
            response = rpc_client.call(request)
            rpc_client.close()
            return response
        except Exception as e:
            print(f"Failed: {e}. Retry after 3 seconds...")
            time.sleep(3)

In other terminal start download server:
```
python host_tasks.py $(pwd)
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