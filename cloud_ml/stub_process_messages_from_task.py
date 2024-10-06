import json
from utils.task_exceptions import TaskUnknownMessageType
 
# will be used by service_cloud_ml for running RPC calls uppon receiving messages
# for updating task database 
class StubForwardMessagesFromTask:

    def __init__(self, task_id:str):
        self.task_id = task_id

    def call_coresponding_func_by_type(self, message:dict):
        message_type = message.get("type")
        if message_type == "model":
            self.process_model(message)
        elif message_type == "info":
            self.process_info(message)
        elif message_type == "print":
            self.process_print(message)
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
        print(f"Sending model message from task {self.task_id} to Rabbit: {message}")

    def process_info(self, message):
        print(f"Sending info message from task {self.task_id} to Rabbit: {message}")

    def process_model(self, message):
        print(f"Sending model message from task {self.task_id} to Rabbit: {message}")

    def process_print(self, message):
        print("P ", message["message"])