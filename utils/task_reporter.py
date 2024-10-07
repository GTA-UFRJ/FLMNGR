import socket
import json
from sys import stdout, stderr

class TaskReporter:

    def __init__(self): 
        pass

    def send_stats(self, task_round:int, acc:int):
        message = {
            "type": "model",
            "round": str(task_round),
            "acc": str(acc)
        }
        json_message = json.dumps(message)
        print(json_message, flush=True)

    def send_info(self, info:str):
        message = {
            "type": "info",
            "info": info
        }
        json_message = json.dumps(message)
        print(json_message, flush=True)

    def send_print(self, msg:str):
        message = {
            "type": "print",
            "message": msg
        }
        json_message = json.dumps(message)
        print(json_message, flush=True)

    def send_error(self, excpetion:Exception):
        message = {
            "type": "error",
            "exception": str(excpetion)
        }
        json_message = json.dumps(message)
        print(json_message, flush=True)

