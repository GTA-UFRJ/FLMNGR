import socket
import random
from task_reporter import TaskReporter

def is_port_available(ip,port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.bind((ip, port))
            return True 
        except OSError:
            return False
    
def get_random_available_port():
    while True:
        port = random.randint(1024, 65535)  # Randomly select a port in the user range
        if is_port_available(port):
            return port 
        
def get_server_task_reporter_and_port(argv:list) -> tuple[TaskReporter,int]:
    return TaskReporter(int(argv[1])), int(argv[2])