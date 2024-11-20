
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

In two other terminals, run two Flower clients after waiting the server to start
```
python -m tasks.task_4fe5.client cli
```

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

### How to develop Flower tasks compatible with FTDL?

The following requisites must be met:

* Client and server main files which will be executed must have paths: 
`tasks/task_[id]/client.py` and  `tasks/task_[id]/server.py`

* The path to the tasks files dir (p.e. `tasks/task_[id]`) must be added to 
the Python system path for imports. This can be achieved by adding the 
following code snippet at the begining of `client.py` and `server.py` files:

```python
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
```

* The first CLI argument after the file name, stored at `sys.argv[1]` is the
working directory of the component from where the client/server were called.
It must also be added to the Python system path, as follows: 

```python
sys.path.append(sys.argv[1])
```

* Import `TaskReporter` from FTDL for reporting information and errors at
both client and server:

```python
from task_daemon_lib.task_reporter import TaskReporter
task_reporter = TaskReporter()
```

* The main loop of both client and server must be inside a `try` block. 
Uppon an unhandled exception is raised, an error must be reported to
FTDL daemon who started the task.

```python
try:
    start_client(
        server_address="127.0.0.1:8080",
        client=FlowerClient().to_client(),
    )
except Exception as e:
    task_reporter.send_error(e)
```

### Test Cloud Task Manager service

Cloud Task Manager is a component that receives messages through a RabbitMQ
broker for RPC function execution. This broker logic is not yet implemented. 
The responsability of this service is to manage server  tasks being started
and finished. 

```
python -m test_cloud_ml_logic
```