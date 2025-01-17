import configparser
import requests

import uuid

if __name__ == "__main__":
    configs = configparser.ConfigParser()
    configs.read("config.ini")

    print("Registering new task")
    url = (
        f"""http://localhost:{configs['server.gateway']['port']}/rpc_exec_create_task"""
    )
    ret = requests.post(
        url,
        headers={"Content-type": "application/json"},
        data="""{"task_id":"4fe5",
            "host":"localhost",
            "port":8080,
            "username":"user",
            "password":"123",
            "files_paths":["client.py","task.py"]
    }""",
    )

    print(ret.content)
    if ret.status_code != 200:
        print("ERROR: Code not 200")
        exit(1)
