import json
from utils.task_exceptions import TaskUnknownMessageType
from utils.udp_task_listener import UdpTaskMessageListener
 
# will be used by service_cloud_ml for running RPC calls uppon receiving messages
# for updating task database 
class ProcessMessagesFromTask:

    def __init__(self):
        self.udp_listener = UdpTaskMessageListener(self.process_message)

    def call_coresponding_func_by_type(self, message:dict):
        message_type = message.get("type")
        if message_type == "model":
            self.process_model(message)
        elif message_type == "info":
            self.process_info(message)
        else:
            raise TaskUnknownMessageType()

    def process_message(self, packet:bytes):
        try:
            message = json.loads(packet.decode('utf-8'))  # Convert bytes to JSON dictionary
            self.call_coresponding_func_by_type(message)
        except json.JSONDecodeError:
            print("Received invalid JSON data")
        except Exception as e:
            print(f"Error processing message: {e}")

    def process_model(self, message):
        print(f"Sending model message to Rabbit: {message}")

    def process_info(self, message):
        print(f"Sending info message to Rabbit: {message}")

    def start_listening(self):
        self.udp_listener.start()

    def stop_listening(self):
        self.udp_listener.stop()

    def get_listening_port(self) -> int:
        return self.udp_listener.port