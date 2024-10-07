import json
from utils.task_exceptions import TaskUnknownMessageType
 
# will be used by service_cloud_ml for running RPC calls uppon receiving messages
# for updating task database 
class StubForwardMessagesFromTask:

    def __init__(self, task_id:str, uppon_receiving_error):
        self.task_id = task_id
        self.uppon_receiving_error = uppon_receiving_error

    def call_coresponding_func_by_type(self, message:dict):
        message_type = message.get("type")
        if message_type == "model":
            self.process_model(message)
        elif message_type == "info":
            self.process_info(message)
        elif message_type == "print":
            self.process_print(message)
        elif message_type == "error":
            self.process_error(message)
        else:
            raise TaskUnknownMessageType()

    def process_messages(self, message:bytes):
        try:
            message = json.loads(message.decode("utf8")) 
            self.call_coresponding_func_by_type(message)   
        except UnicodeDecodeError:
            pass
        except (json.JSONDecodeError, TaskUnknownMessageType):
            # Replace by a log 
            print(f"[{self.task_id}] {message.decode("utf8").strip()}")

    def process_error(self, message:dict):
        try:
            excpetion_message = message["exception"]
            print(f"Received error from task {self.task_id}: {excpetion_message}")
            self.uppon_receiving_error(self.task_id)
        except Exception as e:
            print(f"Could not completelly process the error: {e}")
        
    
    def process_model(self, message):
        print(f"Sending model message from task {self.task_id} to Rabbit: {message}")

    def process_info(self, message):
        print(f"Sending info message from task {self.task_id} to Rabbit: {message}")

    def process_model(self, message):
        print(f"Sending model message from task {self.task_id} to Rabbit: {message}")

    def process_print(self, message):
        print("P ", message["message"])