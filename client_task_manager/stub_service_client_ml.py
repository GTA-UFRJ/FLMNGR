from client_ml import ClientML
from stub_process_messages_from_task import StubForwardMessagesFromTask
from task_daemon_lib.task_exceptions import TaskAlredyStopped
from client_info_manager import ClientInfoManager
import json

class StubServiceClientML:
    """
    Main class for Client Task Manager microservice
    This is a stub that executes the methods for starting/stopping a task at server side,
    but they are not yet connected to the RabbitMQ RPC system  

    :param workpath: project location, within which "tasks" dir resides
    :type workpath: str

    :param client_info: JSON with client basic info
    :type client_info: dict
    """
    def __init__(
        self,
        workpath:str,
        client_info:dict) -> None:

        self.cloud_ml_backend = ClientML(workpath)
        self.client_info_handler = ClientInfoManager(workpath)
        self.initial_client_info = client_info
        self.client_info_handler.save_complete_info(client_info)

    def rpc_call_send_client_stats(self):
        """
        Get client info stored in client_info dir inside workpath and sends it to the server
        """
        try:
            request = self.client_info_handler.get_info_if_changed()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not get info file: {e}. Restarting stats")
            self.client_info_handler.save_complete_info(self.initial_client_info)
            request = self.initial_client_info

        if request is None:
            print("Nothing interesting to report...")
            return

        """
        rpc_client = RpcClient("send_client_stats")
        response = rpc_client.call(request)
        #if response.get("status") != 200:
        #    print(f"Error after sending client info: {response.get("exception")}")
        return response
        """
        # Fake processing for now
        print(f"Should send request {request} now")

    def rpc_call_request_task(self):
        """
        Sends an RPC message to cloud task manager requesting compatible tasks
        """
        client_info = self.client_info_handler.get_info()
        """
        rpc_client = RpcClient("request_task")
        response = rpc_client.call({"client_id":client_info.get('client_id')})
        #if response.get("status") != 200:
        #    print(f"Error after requesting task: {response.get("exception")}")
        return response
        """
            