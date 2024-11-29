from client_ml import ClientML
from stub_process_messages_from_task import StubForwardMessagesFromTask
from task_daemon_lib.task_exceptions import TaskAlredyStopped
from client_info_manager import ClientInfoManager
from task_files_downloader import download_task_training_files
import json
import os
from typing import Callable

class StubServiceClientML:
    """
    Main class for Client Task Manager microservice
    This is a stub that executes the methods for starting/stopping a task at server side,
    but they are not yet connected to the RabbitMQ RPC system  

    :param workpath: project location, within which "tasks" dir resides
    :type workpath: str

    :param client_info: JSON with client basic info
    :type client_info: dict

    :param policy: if "one", start the one task, using received order as priority. If "all", starts all received tasks 
    :type policy: str

    :param policy: if "one", start the one task, using received order as priority. If "all", starts all received tasks 
    :type policy: str
    """
    def __init__(
        self,
        workpath:str,
        client_info:dict,
        autorun:bool=True,
        policy:str="one",
        download_url:str="http://127.0.0.1:5000") -> None:

        self.client_ml_backend = ClientML(workpath)

        self.download_url = download_url
        self.tasks_path = os.path.join(workpath,"tasks")

        self.client_info_handler = ClientInfoManager(workpath)
        self.initial_client_info = client_info

        if autorun:

            self.client_info_handler.save_complete_info(client_info)
    
            policy_functions = {"one":self.run_task_one_policy,
                                "all":self.run_tasks_all_policy}
            policy_function = policy_functions.get(policy)
    
            if policy_function is None:
                print("Policy should be 'one' or 'all'. Default: one")
                policy_function = self.run_task_one_policy
    
            self.current_tasks_list = []
            self.problematic_tasks = []
    
            self._continuous_procedure(policy_function)

    def _update_info_procedure(self):
        """
        This function is periodically called to perform the following actions:
        1) sends stats
        2) requets a task
        3) updates current tasks list
        """
        self.rpc_call_send_client_stats()

        response = self.rpc_call_request_task()
        if (response is not None):
            self.current_tasks_list = response
        
    def _continuous_procedure(self, policy_function:Callable[[list],None]):
        while True:
            self._update_info_procedure()
            policy_function(self.current_tasks_list.copy())

    def run_tasks_all_policy(self, tasks_list:list):
        raise NotImplementedError

    def run_task_one_policy(self, tasks_list:list):
        """
        Run the first task of the list if no task is running. If fails, try the next

        :param tasks_list: list with dictionaries of tasks infos received from the server
        :type tasks_lists: list
        """
        running_tasks = self.client_ml_backend.get_running_tasks()
        if running_tasks != []: # Task running? Do nothing
            return
        
        candidates_tasks = [task for task in tasks_list 
                            if task not in self.problematic_tasks]
        selected_task_info = candidates_tasks[0]
        
        task_id = selected_task_info.get("ID") # We assume that the received task was alredy validated at RPC library
        task_arguments = selected_task_info.get("arguments") # We assume that the received task was alredy validated at RPC library
        try:
            download_task_training_files(
                task_id=task_id,
                work_path=self.tasks_path,
                username=selected_task_info.get("username"),
                password=selected_task_info.get("password"),
                files_paths=selected_task_info.get("files_paths"),
                download_server_url=self.download_url
            )
        except Exception as e:
            print(f"Exception occured while starting task {task_id}: {e}")
            self.problematic_tasks.append(selected_task_info)

        self.start_client_task(task_id, task_arguments)

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
        
        """
        # Fake processing for now
        print(f"Should send request {request} now")

    def rpc_call_request_task(self) -> list:
        """
        Sends an RPC message to cloud task manager requesting compatible tasks

        :return: list of tasks info
        :rtype: list
        """
        client_info = self.client_info_handler.get_info()
        """
        rpc_client = RpcClient("request_task")
        response = rpc_client.call({"client_id":client_info.get('client_id')})
        #if response.get("status") != 200:
        #    print(f"Error after requesting task: {response.get("exception")}")
        return response
        """
        response = [
                {'ID': '4fe5', 
                'host': 'localhost', 
                'port': 8080, 
                'tags': [], 
                'client_arguments': None, 
                'username': 'user', 
                'password': '123', 
                'files_paths': ['./task_4fe5/client.py', './task_4fe5/task.py']}
            ]
        print(f"Should receive {response} now")
        return response
    
    def handle_error_from_task(self, task_id:str):
        """
        This function is executed to handle an error received by the task 
        message forwarder, which handles messages from the Flower subprocess 
        
        :param task_id: task ID
        :type task_id: str

        :raises: TaskIdNotFound
        """
        try:
            print("Treat error from task...")
            self.client_ml_backend.stop_task(task_id)
        except TaskAlredyStopped:
            print(f"Received error from task {task_id}, which was alredy stopped")

    def start_client_task(self, task_id:str, arguments:str):
        """
        After downloading task, starts it
        
        :param task_id: task ID
        :type task_id: str
        
        :param arguments: command line arguments when startting child task
        :type arguments: str
        
        :raises: FileNotFoundError 
        
        :raises: TaskIdAlredyInUse

        :raises: TaskAlredyRunning

        :raises: PermissionError
        """
        
        forwarder = StubForwardMessagesFromTask(
            task_id,
            self.handle_error_from_task)
        callback = forwarder.process_messages
        
        self.client_ml_backend.start_new_task(
            task_id,
            callback,
            arguments
        )

