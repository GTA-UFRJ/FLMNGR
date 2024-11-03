
# Cloud Task Manager

This microservice is responsible for:
* Implementing CRUD operations over all tasks, running or not
* Mantaining client and server codes for inference, training, and aggregation for all tasks
* Starting and stopping Flower aggreagtion services at the server by demand 

### Test Flower task

In one terminal, run the Flower server
```
python -m tasks.task_4fe5.server cli
```

In other terminal, run the Flower client after waiting the server to start
```
python -m tasks.task_4fe5.client cli
```

In a third terminal, run the second Flower client
```
python -m tasks.task_4fe5.client cli
```

### Flower Tasks Daemon Library (FTDL)

This is a library for starting a Flower task as a child process. It also receives information from this task for logging and for finishing the task.

The task initializers uppon execution, create a Flower child process that reports message to the task initializer using a UDP socket (client is the task reporter and server is the task listener).

Here are the commands to run the server in one terminal, followed by
two clients in other terminals:
```
python -m task_daemon_lib.server_side_task
```

```
python -m task_daemon_lib.client_side_task
```

```
python -m task_daemon_lib.client_side_task
```

### Test Cloud Task Manager service

Cloud Task Manager is a component that receives messages through a RabbitMQ
broker for RPC function execution. This broker logic is not yet implemented. 
The responsability of this service is to manage server  tasks being started
and finished. 

```
python -m test_cloud_ml_logic
```