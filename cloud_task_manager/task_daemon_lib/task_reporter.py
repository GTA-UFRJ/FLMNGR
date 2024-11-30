import socket
import json
from sys import stdout, stderr

class TaskReporter:
    """
    Used by the process to send messages through the stdout pipe
    """
    def __init__(self): 
        self.send_info("Started")

    def send_stats(self, task_round:int, acc:int):
        """
        Format: {"type": "model","round": strtask_round),"acc": str(acc)}

        :param task_round: Flower communication round
        :type task_round: int

        :param acc: current model accuracy
        :type acc: int
        """
        message = {
            "type": "model",
            "round": str(task_round),
            "acc": str(acc)
        }
        json_message = json.dumps(message)
        print(json_message, flush=True)

    def send_info(self, info:str):
        """
        Format: {"type": "info","info": info}

        :param info: or warning, or generic information
        :type info: str
        """
        message = {
            "type": "info",
            "info": info
        }
        json_message = json.dumps(message)
        print(json_message, flush=True)

    def send_print(self, msg:str):
        """
        Format: {"type":"print","message":msg}

        :param message: a log, or generic message
        :type message: str
        """
        message = {
            "type": "print",
            "message": msg
        }
        json_message = json.dumps(message)
        print(json_message, flush=True)

    def send_error(self, excpetion:Exception):
        """
        Format: {"type": "error","exception": str(excpetion)}

        :param excpetion: unhandled exception that occured on child process. Typically, causes message listener termination 
        :type excpetion: Exception
        """
        message = {
            "type": "error",
            "exception": str(excpetion)
        }
        json_message = json.dumps(message)
        print(json_message, flush=True)

    def trigger(self, trigger_name:str, trigger_arguments:str=""):
        """
        Format : {"type":"trigger","trigger_name":{trigger_name},"trigger_arguments":{trigger_arguments}}

        :param trigger_name: name of the code that is executed uppon receiving this trigger
        :type trigger_name: str

        :param trigger_arguments: arguments for running trigger
        :type trigger_arguments: str
        """
        message = {
            "type": "print",
            "trigger_name":trigger_name,
            "trigger_arguments": trigger_arguments
        }
        json_message = json.dumps(message)
        print(json_message, flush=True)


