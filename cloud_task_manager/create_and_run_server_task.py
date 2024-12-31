from microservice_interconnect.rpc_client import rpc_send
import configparser

if __name__ == "__main__":

    configs = configparser.ConfigParser()
    configs.read("config.ini")
    ret = rpc_send("rpc_exec_create_task",
            {"task_id":"4fe5",
            'host':'localhost',
            'port':8080,
            'username':'user',
            'password':'123',
            'files_paths':['client.py','task.py']
            },
            host=configs["server.broker"]["host"],
            port=configs["server.broker"]["port"])
    ret = rpc_send("rpc_exec_start_server_task",{"task_id":"4fe5"})