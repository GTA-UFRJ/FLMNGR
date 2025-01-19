from microservice_interconnect.rpc_client import rpc_send, register_event
import configparser
import requests
import time as tm

if __name__ == "__main__":

    configs = configparser.ConfigParser()
    configs.read("config.ini")
    allow_register = configs.getboolean("events","register_events")
    host = configs["server.broker"]["host"]
    port = int(configs["server.broker"]["port"])

    register_event("Operator","register_task","Started registering a task", allow_registering=allow_register, host=host, port=port)
    startTime = tm.process_time_ns()
    ret = requests.post(
        f"http://localhost:{configs['server.gateway']['port']}/rpc_exec_create_task",headers={"Content-type":"Application/json"},
        data="""{"task_id":"4fe5",
"host":"localhost",
"port":8080,
"username":"user",
"password":"123",
"files_paths":["client.py","task.py"]
}""")
    
    registerTime = tm.process_time_ns() - startTime
    if ret.status_code != 200:
        print("ERROR on request")
        print(ret.content)
        exit(1)
    register_event("Operator","register_task", "Finished registering a task", allow_registering=allow_register, host=host, port=port)
    register_event("Operator","operator_register_task_time", f"{registerTime}", allow_registering=allow_register, host=host, port=port)
    

    register_event("Operator","start_task","Started starting a task", allow_registering=allow_register, host=host, port=port)
    startTime = tm.process_time_ns()
    ret = requests.post(
        f"http://localhost:{configs['server.gateway']['port']}/rpc_exec_start_server_task",headers={"Content-type":"Application/json"},
        data="""{"task_id":"4fe5"}""")
    if ret.status_code != 200:
        print("ERROR on request")
        print(ret.content)
        exit(1)
    processTime = tm.process_time_ns() - startTime
    register_event("Operator","start_task","Finished starting a task", allow_registering=allow_register, host=host, port=port)
    register_event("Operator","operator_register_task_time",f"{processTime}", allow_registering=allow_register, host=host, port=port)

