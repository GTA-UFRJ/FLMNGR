import json
from task_daemon_lib.task_exceptions import TaskUnknownMessageType
from task_daemon_lib.trigger import Trigger
from typing import Callable
 
# will be used by service_cloud_ml for receiving messages
# from Flower subprocesses for updating task database 
class StubForwardMessagesFromTask:
    """
    Handles messages received from subprocess using task listener from FTDL

    :param task_id: task ID
    :type task_id: str

    :param uppon_receiving_error: function that receives task ID for finishing it 
    :type uppon_receiving_error: Callable[[str],None]
    """
    def __init__(self, task_id:str, uppon_receiving_error: Callable[[str],None], work_path:str):
        self.task_id = task_id
        self.work_path = work_path
        self.uppon_receiving_error = uppon_receiving_error

    def call_coresponding_func_by_type(self, message:dict):
        """
        Use received message's type field to find the corresponding private method and call it 

        :param message: received message that can be anything
        :type message: bytes

        :raises: TaskUnknownMessageType
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
        elif message_type == "trigger":
            self.process_trigger(message.get("trigger_name"), message.get("trigger_arguments"))
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
            print(f"[{self.task_id}] {message.decode("utf8").strip()}")

    def process_error(self, exception_message:str):
        """
        Call uppon_receiving_error external function to finish the task

        :param exception_message: received exception message from task
        :type exception_message: str
        """
        try:
            print(f"Received error from task {self.task_id}: {exception_message}")
            self.uppon_receiving_error(self.task_id)
        except Exception as e:
            print(f"Could not completelly process the error: {e}")
    
    def process_trigger(self, trigger_name:str, trigger_arguments:str):
        """
        Run a triggered code

        :param trigger_name: name of the code that is executed uppon receiving this trigger
        :type trigger_name: str

        :param trigger_arguments: arguments for running trigger
        :type trigger_arguments: str
        """
        try:
            print(f"Received trigger from task {self.task_id}: {trigger_name} {trigger_arguments}")
            trigger = Trigger(self.work_path, self.task_id, trigger_name, trigger_arguments)
            trigger.run_trigger()
        except Exception as e:
            print(f"Could not run trigger: {e}")

    def process_model(self, model: bytes):
        print(f"Saving model message from task {self.task_id}: {model}")

    def process_info(self, info: dict):
        print(f"Sending info message from task {self.task_id} to log: {info}")

    def process_print(self, message: str):
        print("P ", message["message"])