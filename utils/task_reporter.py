import socket
import json
from sys import stdout, stderr

class TaskReporter:

    def __init__(self, port, ip='localhost', redirect_print=True):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        if redirect_print:
            self.set_redirect_output_to_task_reporter()

    def send(self, json_message:dict):
        try:
            self.sock.sendto(json_message, (self.ip, self.port))  
            #print(f"Sent message: {json_message}")
        except Exception as e:
            print(f"Failed to send message: {e}")

    def send_stats(self, task_round:int, acc:int):
        message = {
            "type": "model",
            "round": str(task_round),
            "acc": str(acc)
        }
        json_message = json.dumps(message).encode('utf-8')
        self.send(json_message)

    def send_info(self, info:str):
        message = {
            "type": "info",
            "info": info
        }
        json_message = json.dumps(message).encode('utf-8')
        self.send(json_message)

    def send_print(self, msg:str):
        message = {
            "type": "print",
            "message": msg
        }
        json_message = json.dumps(message).encode('utf-8')
        self.send(json_message)

    def close(self):
        self.sock.close()

    def set_redirect_output_to_task_reporter(self):
        stdout = stderr = self

    def write(self, message:str):
        if message.strip():
            self.send_print(message.encode())
    
    # Required for compatibility with sys.stdout, but not needed for UDP.
    def flush(self):
        pass 

