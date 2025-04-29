import json
from task_daemon_lib.task_exceptions import TaskUnknownMessageType
from typing import Callable
 
# will be used by service_client_ml for receiving messages
# from Flower subprocesses for updating task database 
class ForwardMessagesFromClientTask:
    """
    Handles messages received from subprocess using task listener from FTDL

    :param task_id: task ID
    :type task_id: str

    :param uppon_receiving_error: function that receives task ID for finishing it 
    :type uppon_receiving_error: Callable[[str],None]
    """
    def __init__(self, task_id:str, uppon_receiving_error: Callable[[str],None], uppon_receiving_finish: Callable[[str],None]):
        self.task_id = task_id
        self.uppon_receiving_error = uppon_receiving_error
        self.uppon_receiving_finish = uppon_receiving_finish

    def call_coresponding_func_by_type(self, message:dict):
        """
        Use received message's type field to find the corresponding private method and call it 

        :param message: received message that can be anything
        :type message: bytes

        :raises TaskUnknownMessageType: value corresponding to key "type" is not model, info, message, exception, or trigger
        """
        message_type = message.get("type")
        if message_type == "model":
            self.process_model(message.get("model"))
        elif message_type == "info":
            self.process_info(message.get("info"))
        elif message_type == "print":
            self.process_print(message.get("message"))
        elif message_type == "error":
            self.process_error(message.get("exception"))
        else:
            raise TaskUnknownMessageType()

    def process_messages(self, message:bytes):
        """
        Main method for receiving messages from FTDL task listener

        :param message: received message that can be anything
        :type message: bytes
        """
        try:
            message = json.loads(message.decode("utf8")) 
            self.call_coresponding_func_by_type(message)   
        except UnicodeDecodeError:
            pass
        except (json.JSONDecodeError, TaskUnknownMessageType):
            # Replace by a log 
            print(f"[{self.task_id}] {message.decode('utf8').strip()}")

    def process_error(self, exception_message:str):
        """
        Call uppon_receiving_error external function to finish the task

        :param message: received exception message from task
        :type message: str
        """
        try:
            print(f"Received error from task {self.task_id}: {exception_message}")
            self.uppon_receiving_error(self.task_id)
        except Exception as e:
            print(f"Could not completelly process the error: {e}")
    
    def process_model(self, model: bytes):
        print(f"Saving model message from task {self.task_id}: {model}")

    def process_info(self, info: str):
        if info == "Finished":
            print(f"Received finish info from task {self.task_id}")
            self.uppon_receiving_finish(self.task_id)

    def process_print(self, message: str):
        print("P ", message["message"])
