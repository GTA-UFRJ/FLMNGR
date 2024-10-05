import socket
import json

class TaskReporter:

    def __init__(self, port, ip='localhost'):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP socket

    def send(self, json_message:dict):
        try:
            self.sock.sendto(json_message, (self.ip, self.port))  
            print(f"Sent message: {json_message}")
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
            "type": "model",
            "info": info
        }
        json_message = json.dumps(message).encode('utf-8')
        self.send(json_message)

    def close(self):
        self.sock.close()
