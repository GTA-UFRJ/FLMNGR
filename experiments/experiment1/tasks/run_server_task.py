import configparser
import requests

if __name__ == "__main__":

    configs = configparser.ConfigParser()
    configs.read("config.ini")

    print("Starting task")
    url = f"""http://localhost:{configs['server.gateway']['port']}/rpc_exec_start_server_task"""
    ret =requests.post(url,data={"task_id":"4fe5"})
    if ret.status_code != 200:

        print("ERROR: Code not 200")
        exit(1)

