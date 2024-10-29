# FLMNGR

### Requisites:

* Conda

### Configuration

Create conda environment:
```
conda create -n flmngr
```

Activate conda environment:
```
conda activate flmngr
```

Install requirements:
```
pip install -r requirements.txt
```

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

### Test server/client task initializers

The task initializers, located inside `utils` directory, uppon execution,
create a Flower child process that reports message to the task initializer
using a UDP socket (client is the task reporter and server is the 
task listener).

Here are the commands to run the server in one terminal, followed by
two clients in other terminals:
```
python -m utils.server_side_task
```

```
python -m utils.client_side_task
```

```
python -m utils.client_side_task
```

### Test Cloud ML service

Cloud ML is a component that receives messages through a RabbitMQ broker
for RPC function execution. This broker logic is not yet implemented. 
The responsability of this service is to manage server  tasks being started
and finished. 

```
python3 -m cloud_ml.test_cloud_ml_logic
```

### Documentation 

```
cd docs
sphinx-build -M html source build
make html
```
