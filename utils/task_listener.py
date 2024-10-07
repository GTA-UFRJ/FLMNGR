import socket
import threading
import random

class TaskMessageListener:

    def __init__(self, handler, process):
        self.handler = handler
        self.thread = None
        self.process = process

    def process_received_message(self, data:bytes):
        if data:
            self.handler(data)
        
    def listen(self):
        while not self.exit_loop:
            stdout_output = self.process.stdout.readline()
            self.process_received_message(stdout_output) 
            
            stderr_output = self.process.stderr.readline()
            self.process_received_message(stderr_output) 
        
        self.process.stdout.close()
        self.process.stderr.close()
        self.process.wait()
    
    def start(self):
        self.exit_loop = False
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()

    def stop(self):
        self.exit_loop = True
        if self.thread:
            self.thread.join(timeout=1)
