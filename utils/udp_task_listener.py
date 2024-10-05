import socket
import threading
import random

class UdpTaskMessageListener:

    def __init__(self, handler, ip:str='localhost'):
        self.ip = ip
        self.port = self.get_random_available_port()
        self.handler = handler
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
        self.exit_loop = False
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()

    def stop(self):
        # Era pra essa flag liberar a thread do while, mas isso não funciona
        self.send_finish_datagram_to_myself()
        if self.thread:
            self.thread.join()

    def send_finish_datagram_to_myself(self):
        tmp_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tmp_send_sock.sendto(bytes("END","utf-8"), (self.ip, self.port)) 
        tmp_send_sock.close()

    def process_received_datagram(self, data:bytes):
        if not data:
            return 
        
        try:
            self.exit_loop = ( data.decode('utf-8') == "END" )
        except UnicodeDecodeError:
            pass
        
        if not self.exit_loop:
            self.handler(data)

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip, self.port))
        print(f"Listening on {self.ip}:{self.port}...")

        while not self.exit_loop:
            try:
                data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                self.process_received_datagram(data)
            except socket.error as e:
                print(f"Socket error: {e}")

        sock.close()
