from microservice_interconnect.rpc_client import rpc_send, register_event
import configparser

if __name__ == "__main__":

    configs = configparser.ConfigParser()
    configs.read("config.ini")
    allow_register = configs.getboolean("events","register_events")
    host = configs["server.broker"]["host"]
    port = int(configs["server.broker"]["port"])

    register_event("Operator","register_task","Started registering a task",
                   allow_registering=allow_register, host=host, port=port)
    ret = rpc_send("rpc_exec_create_task",
            {"task_id":"4fe5",
            'host':'localhost',
            'port':8080,
            'username':'user',
            'password':'123',
            'files_paths':['client.py','task.py']
            },
            host=host,
            port=port)
    
    register_event("Operator","start_task","Started starting a task",
                   allow_registering=allow_register, host=host, port=port)
    ret = rpc_send("rpc_exec_start_server_task",{"task_id":"4fe5"})