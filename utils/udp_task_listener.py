import socket
import threading
import random

class UdpTaskMessageListener:

    def __init__(self, handler, ip:str='localhost'):
        self.ip = ip
        self.port = self.get_random_available_port()
        self.handler = handler
        self.running = False
        self.thread = None

    def get_random_available_port(self):
        while True:
            port = random.randint(1024, 65535)  # Randomly select a port in the user range
            if self.is_port_available(port):
                return port
            
    def is_port_available(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.bind((self.ip, port))
                return True 
            except OSError:
                return False 

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()

    def stop(self):
        # Era pra essa flag liberar a thread do while, mas isso não funciona
        self.running = False
        if self.thread:
            self.thread.join()

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip, self.port))
        print(f"Listening on {self.ip}:{self.port}...")

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                if data:
                    self.handler(data)
            except socket.error as e:
                print(f"Socket error: {e}")

        sock.close()
