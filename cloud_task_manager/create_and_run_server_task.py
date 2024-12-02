from microservice_interconnect.rpc_client import rpc_send

if __name__ == "__main__":
    ret = rpc_send("rpc_exec_create_task",
            {"task_id":"4fe5",
            'host':'localhost',
            'port':8080,
            'username':'user',
            'password':'123',
            'files_paths':['client.py','task.py']
            })
    ret = rpc_send("rpc_exec_start_server_task",{"task_id":"4fe5"})