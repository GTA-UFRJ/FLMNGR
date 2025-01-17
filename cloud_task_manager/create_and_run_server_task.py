import configparser
import requests

if __name__ == "__main__":

    configs = configparser.ConfigParser()
    configs.read("config.ini")

    print("Registering new task")
    url = f"""http://localhost:{configs['server.broker']['port']}/rpc_exec_create_task"""
    ret = requests.post(url,data={"task_id":"4fe5",
            'host':'localhost',
            'port':8080,
            'username':'user',
            'password':'123',
            'files_paths':['client.py','task.py']
    })

    print(ret)
    if ret.status_code != 200:
        print("ERROR: Code not 200")
        exit(1)

    print()
    print("Starting task")
    url = f"""http://localhost:{configs['server.broker']['port']}/rpc_exec_start_server_task"""
    ret =requests.post(url,data={"task_id":"4fe5"})
    if ret.status_code != 200:

        print("ERROR: Code not 200")
        exit(1)

