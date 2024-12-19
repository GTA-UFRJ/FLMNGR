# Cloud domain

The cloud domain contains the following control elements

```{http:post} /api/v1/rpc_exec_create_task
Creates a task 
The post request must follow the JSON schema bellow: 
```

```{jsonschema} ../../../cloud_task_manager/schemas/rpc_exec_create_task.json
```

```{http:post} /api/v1/rpc_exec_start_server_task

Starts a task given an ID 

:statuscode 200: Success
:statuscode 500: Internal server error 

The post request must follow the JSON schema bellow: 
```

```{jsonschema} ../../../cloud_task_manager/schemas/rpc_exec_start_server_task.json
```

```{http:post} /api/v1/rpc_exec_stop_server_task
Stops a task 
The post request must follow the JSON schema bellow: 
```

```{jsonschema} ../../../cloud_task_manager/schemas/rpc_exec_stop_server_task.json
```

```{http:post} /api/v1/rpc_exec_client_requesting_task
Returns a list of tasks available to a client 
The post request must follow the JSON schema bellow: 
```

```{jsonschema} ../../../cloud_task_manager/schemas/rpc_exec_client_requesting_task.json
```
