import time as tm
from client_task_manager.client_ml import ClientML
from client_task_manager.process_messages_from_client_task import ForwardMessagesFromClientTask
from microservice_interconnect.rpc_client import rpc_send, register_event
from task_daemon_lib.task_exceptions import *
from client_task_manager.client_info_manager import ClientInfoManager
from client_task_manager.task_files_downloader import *
import json
import os
from typing import Callable
from pathlib import Path
from time import sleep, time
import configparser
import signal

class ServiceClientML:
    """
    Main class for Client Task Manager microservice
    This is a stub that executes the methods for starting/stopping a task at server side,
    but they are not yet connected to the RabbitMQ RPC system  

    :param workpath: project location, within which "tasks" and "client_info" directories reside
    :type workpath: str

    :param client_info: JSON with client basic info
    :type client_info: dict

    :param autorun: if True, service constructor blocks the rest of the code and runs a sequence of actions by default
    :type autorun: bool

    :param policy: if "one", start the one task, using received order as priority. If "all", starts all received tasks 
    :type policy: str

    :param download_url: hostname (or IP) and port of the server that hosts tasks to be downloaded. E.g. http://127.0.0.1:5000
    :type download_url: str

    :param client_broker_host: hostname or IP of the broker at the client
    :type client_broker_host: str

    :param client_broker_port: port of the broker at the client
    :type client_broker_port: int

    :raises NotImplementedError: policy not implemented
    """
    def __init__(
        self,
        workpath:str,
        client_info:dict,
        autorun:bool=True,
        policy:str="one",
        download_url:str="http://127.0.0.1:5000",
        client_broker_host:str="localhost",
        client_broker_port:int=5672) -> None:

        self.broker_host = client_broker_host
        self.broker_port = client_broker_port

        self.client_ml_backend = ClientML(workpath)

        self.download_url = download_url
        self.tasks_path = os.path.join(workpath,"tasks")

        self.client_info_handler = ClientInfoManager(workpath, id=client_info.get("user_id"))
        self.client_info_handler.save_complete_info(client_info)
        self.initial_client_info = client_info

        self.current_tasks_list = []
        self.problematic_tasks = []

        self._set_signal()
        
        if autorun:
    
            policy_functions = {"one":self._run_task_one_policy,
                                "all":self._run_tasks_all_policy}
            self.policy_function = policy_functions.get(policy)
    
            if self.policy_function is None:
                print("Policy should be 'one' or 'all'. Default: one")
                self.policy_function = self._run_task_one_policy
        
            register_event("service_client_ml","main","Started",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
    
            self._continuous_procedure()

    def _set_signal(self):
        def signal_handler(sig,frame):
            register_event("service_client_ml","main","Interrupted",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
            self.client_ml_backend.finish_all()
            exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _update_info_procedure(self):
        """
        This function is periodically called to perform the following actions: 1) sends stats, 2) requets a task, and 3) updates current tasks list
        """
        self.rpc_call_send_client_stats()

        response = self.rpc_call_request_task()
        if (response is not None):
            self.current_tasks_list = response
        
    def _continuous_procedure(self):

        def _semaphore():
            start = time()
            while (time()-start  < request_interval) and (not self.changed_running_tasks_state):
                pass
            self.changed_running_tasks_state = False

        self.changed_running_tasks_state = False
        
        while True:
            self._update_info_procedure()
            self.policy_function(self.current_tasks_list.copy())
            _semaphore()

    def _run_tasks_all_policy(self, tasks_list:list):
        raise NotImplementedError

    def _run_task_one_policy(self, tasks_list:list):
        """
        Run the first task of the list if no task is running. If fails, try the next

        :param tasks_list: list with dictionaries of tasks infos received from the server
        :type tasks_lists: list
        """
        running_tasks = self.client_ml_backend.get_running_tasks()
        if len(running_tasks) != 0: # Task running? Do nothing
            return
        
        candidates_tasks = [task for task in tasks_list 
                            if task not in self.problematic_tasks]
        if len(candidates_tasks) == 0:
            return
        self.selected_task_info = candidates_tasks[0]

        startDownloadTime = tm.process_time_ns()
        register_event("service_client_ml","_run_task_one_policy","Started downloading task",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        task_id = self.selected_task_info.get("ID") # We assume that the received task was alredy validated at RPC library
        task_arguments = self.selected_task_info.get("client_arguments") # We assume that the received task was alredy validated at RPC library
        try:
            download_task_training_files(
                task_id=task_id,
                work_path=self.tasks_path,
                username=self.selected_task_info.get("username"),
                password=self.selected_task_info.get("password"),
                files_paths=self.selected_task_info.get("files_paths"),
                download_server_url=self.download_url
            )
            register_event("service_client_ml","_run_task_one_policy","Finished downloading task",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
            register_event("service_client_ml","download_task_time",f"{tm.process_time_ns()-startDownloadTime}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

            self.start_client_task(task_id, task_arguments)
            return
        except (TaskDownloadGenericError, TaskDownloadAuthFail, TaskNotFoundInServer) as e:
            print(f"Exception occured while downloading task {task_id}: {e}")    
        except (FileNotFoundError, TaskIdAlredyInUse, TaskAlredyRunning, PermissionError) as e:
            print(f"Exception occured while starting the task {task_id}: {e}")    
        
        self.problematic_tasks.append(self.selected_task_info)

    def rpc_call_send_client_stats(self):
        """
        Get client info stored in client_info dir inside workpath and sends it to the server
        """
        startTime = tm.process_time_ns()
        register_event("service_client_ml","rpc_call_send_client_stats","Started getting client stats for sending",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        try:
            request = self.client_info_handler.get_info_if_changed()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not get info file: {e}. Restarting stats")
            self.client_info_handler.save_complete_info(self.initial_client_info)
            request = self.initial_client_info

        if request is None:
            return

        print("Reporting stats...")
        response = rpc_send("rpc_exec_update_user_info",request,
                            host=self.broker_host, port=self.broker_port)
        if response.get("status_code") != 200:
            print(f"Error after sending client info: {response.get('exception')}")
        else:
            print(f"New info registered with success")

        register_event("service_client_ml","rpc_call_send_client_stats","Finished getting client stats for sending",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
        register_event("service_client_ml","update_info_time",f"{tm.process_time_ns()-startTime}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def rpc_call_request_task(self) -> list:
        """
        Sends an RPC message to cloud task manager requesting compatible tasks

        :return: list of tasks info
        :rtype: list
        """
        startTime = tm.process_time_ns()
        register_event("service_client_ml","rpc_call_request_task","Started requesting task",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        try:
            client_info = self.client_info_handler.get_info()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not get info file: {e}. Restarting stats")
            self.client_info_handler.save_complete_info(self.initial_client_info)

        response = rpc_send(
            "rpc_exec_client_requesting_task",
            {"user_id":client_info.get('user_id')},
            host=self.broker_host,
            port=self.broker_port)
        if response.get("status_code") != 200:
            register_event("service_client_ml","rpc_call_request_task","Failed requesting task",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
            print(f"Error after requesting task: {response.get('exception')}")
            return []
        else:
            register_event("service_client_ml","rpc_call_request_task","Finished requesting task",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
            register_event("service_client_ml","request_task_time",f"{tm.process_time_ns()-startTime}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
            return response.get("return")
    
    def handle_error_from_task(self, task_id:str):
        """
        This function is executed to handle an error received by the task 
        message forwarder, which handles messages from the Flower subprocess 
        
        :param task_id: task ID
        :type task_id: str

        :raises TaskIdNotFound: task not found 
        """
        register_event("service_client_ml","handle_error_from_task",f"Started handling error from task {task_id}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        try:
            print("Treat error from task...")
            self.client_ml_backend.stop_task(task_id)
            print(f"Since an error was encountered in task {task_id}, it will be send to quarentine")
            self.problematic_tasks.append(self.selected_task_info)
        except TaskAlredyStopped:
            print(f"Received error from task {task_id}, which was alredy stopped")
        
        register_event("service_client_ml","handle_error_from_task",f"Finished handling error from task {task_id}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        self.changed_running_tasks_state = True

    def start_client_task(self, task_id:str, arguments:str):
        """
        After downloading task, starts it
        
        :param task_id: task ID
        :type task_id: str
        
        :param arguments: command line arguments when startting child task
        :type arguments: str
        
        :raises FileNotFoundError: "{work_path}/tasks/task_{task_id}/client.py" does not exist
        
        :raises TaskIdAlredyInUse: could not start a task that is alredy in the map

        :raises TaskAlredyRunning: try to start a task that was not stopped

        :raises PermissionError: doesn't have permission to run the task script
        """
        startTime = tm.process_time_ns()
        register_event("service_client_ml","start_client_task","Started client task initialization",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
        

        def finish_task(task_id:str):
            startTime = tm.process_time_ns()
            register_event("service_client_ml","finish_task",f"Started handling task {task_id} finalization",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
            
            try:
                self.client_ml_backend.stop_task(task_id)
                register_event("service_client_ml","finish_task",f"Finished handling task {task_id} finalization",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
                register_event("service_client_ml","finish_task_time",f"{tm.process_time_ns()-startTime}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
            except Exception as e:
                print(e)
                register_event("service_client_ml","finish_task",f"Finished handling task {task_id} finalization",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
                register_event("service_client_ml","finish_client_task_time",f"{tm.process_time_ns()-startTime}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
                raise e
            
            self.changed_running_tasks_state = True


        forwarder = ForwardMessagesFromClientTask(
            task_id,
            self.handle_error_from_task,
            finish_task)
        callback = forwarder.process_messages
        
        self.client_ml_backend.start_new_task(
            task_id,
            callback,
            arguments
        )

        register_event("service_client_ml","start_client_task","Finish client task initialization",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
        register_event("service_client_ml","start_client_task_time",f"{tm.process_time_ns()-startTime}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

if __name__ == "__main__":

    configs = configparser.ConfigParser()
    configs.read("config.ini")
    allow_register = configs.getboolean("events","register_events")
    request_interval = int(configs["client.params"]["request_interval"])

    service = ServiceClientML(
        os.path.join(Path().resolve(),"client_task_manager"),
        {
            "user_id":"guilhermeeec",
            "data_qnt":0,
            "avg_acc_contrib":None,
            "avg_disconnection_per_round":None,
            "sensors":["camera","ecu"]
        },
        download_url=f"http://{configs['server.broker']['host']}:5000",
        client_broker_host=configs["client.broker"]["host"],
        client_broker_port=configs["client.broker"]["port"],
    )
