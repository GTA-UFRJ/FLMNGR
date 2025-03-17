import os
import json
import configparser
from pathlib import Path
import signal
import sys
import time as tm

from cloud_task_manager.cloud_ml import CloudML
from cloud_task_manager.criteria_evaluation_engine import *
from cloud_task_manager.tasks_db_interface import TasksDbInterface
from microservice_interconnect.rpc_client import rpc_send, register_event
from task_daemon_lib.task_exceptions import TaskAlredyStopped
from microservice_interconnect.base_service import BaseService
from cloud_task_manager.process_messages_from_task import ForwardMessagesFromTask

class CouldNotRetrieveUser(Exception):
    def __init__(self, user_id:str):
        super().__init__(f"Could not retrieve info from user with ID={user_id}")

class ServiceCloudML(BaseService):
    """
    Main class for Cloud Task Manager microservice that executes the methods for starting/stopping a task at server side

    :param workpath: project location, within which "tasks" dir resides
    :type workpath: str
    """

    def __init__(
            self, 
            workpath: str, 
            broker_host:str="localhsot",
            broker_port:str=5672) -> None:
        super().__init__(broker_host=broker_host, broker_port=broker_port)
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.workpath = workpath
        self.cloud_ml_backend = CloudML(workpath)
        self.db_handler = TasksDbInterface(workpath)

        self.add_api_endpoint(
            func=self.rpc_exec_create_task,
            func_name="rpc_exec_create_task",
            schema=self._get_schema("rpc_exec_create_task"),
        )

        self.add_api_endpoint(
            func=self.rpc_exec_start_server_task,
            func_name="rpc_exec_start_server_task",
            schema=self._get_schema("rpc_exec_start_server_task"),
        )

        self.add_api_endpoint(
            func=self.rpc_exec_stop_server_task,
            func_name="rpc_exec_stop_server_task",
            schema=self._get_schema("rpc_exec_stop_server_task"),
        )

        self.add_api_endpoint(
            func=self.rpc_exec_client_requesting_task,
            func_name="rpc_exec_client_requesting_task",
            schema=self._get_schema("rpc_exec_client_requesting_task"),
        )

        self.add_api_endpoint(
            func=self.rpc_exec_update_task,
            func_name="rpc_exec_update_task",
            schema=self._get_schema("rpc_exec_update_task"),
        )

        self.add_api_endpoint(
            func=self.rpc_exec_get_task_by_id,
            func_name="rpc_exec_get_task_by_id",
            schema=self._get_schema("rpc_exec_get_task_by_id"),
        )

        register_event("service_cloud_ml","main","Started",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def _get_schema(self, func_name: str) -> dict:
        """
        Read JSON schema from file

        :param func_name: JSON message name
        :type func_name: str

        :return: JSON
        :rtype: dict

        :raises: OSError

        :raises: json.JSONDecodeError
        """
        with open(os.path.join(self.workpath, "schemas", f"{func_name}.json")) as f:
            return json.load(f)

    def handle_error_from_task(self, task_id: str):
        """
        This function is executed to handle an error received by the task
        message forwarder, which handles messages from the Flower subprocess

        :param task_id: task ID
        :type task_id: str

        :raises: TaskIdNotFound
        """
        register_event("service_cloud_ml","handle_error_from_task",f"Started handling error from task {task_id}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        try:
            self.db_handler.set_task_not_running(task_id)
            self.cloud_ml_backend.stop_task(task_id)

        except TaskAlredyStopped:
            print(f"Received error from task {task_id}, which was alredy stopped")

        register_event("service_cloud_ml","handle_error_from_task",f"Finished handling error from task {task_id}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def rpc_exec_create_task(self, received: dict):
        """
        Receives a validated JSON message for configuring a new task in database, but not start yet

        :param received: JSON containing task ID, host, port, arguments, selection criteria, tags, ...
        :type received: dict

        :raises: sqlite3.IntegrityError
        """
        startTime = tm.process_time_ns()
        register_event("service_cloud_ml","rpc_exec_create_task","Started task creation",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        self.db_handler.insert_task(
            task_id=received["task_id"],
            host=received["host"],
            port=received["port"],
            username=received["username"],
            password=received["password"],
            files_paths=received["files_paths"],
            selection_criteria=received.get("selection_criteria"),
            server_arguments=received.get("server_arguments"),
            client_arguments=received.get("client_arguments"),
            tags=received.get("tags"),
        )

        register_event("service_cloud_ml","rpc_exec_create_task",f"Finished task creation",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
        register_event("service_cloud_ml","create_task_time",f"{tm.process_time_ns()-startTime}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def rpc_exec_start_server_task(self, received: dict):
        """
        Receives a validated JSON message for starting a server task
        Validation occurs using our RPC library

        :param received: JSON containing task ID and optional arguments
        :type received: dict

        :raises: FileNotFoundError

        :raises: TaskIdAlredyInUse

        :raises: TaskAlredyRunning

        :raises: PermissionError

        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """
        startTime = tm.process_time_ns()
        register_event("service_cloud_ml","rpc_exec_start_server_task","Started server task initialization",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        def finish_task(task_id: str):
            try:
                self.rpc_exec_stop_server_task({"task_id": task_id})
            except Exception as e:
                print(e)
                raise e

        forwarder = ForwardMessagesFromTask(
            received["task_id"], self.handle_error_from_task, finish_task, self.workpath
        )
        callback = forwarder.process_messages

        preinserted_task_info_dict = self.db_handler.query_task(received["task_id"])
        if received.get("arguments") is not None:
            # Case 1: arguments informed by field received in RPC JSON message
            arguments = received.get("arguments")
        else:
            # Case 2: default arguments, regstered in DB
            arguments = preinserted_task_info_dict.get("server_arguments")

        self.db_handler.set_task_running(received["task_id"])

        try:
            self.cloud_ml_backend.start_new_task(
                received["task_id"], callback, arguments
            )
        except Exception as e:
            self.db_handler.set_task_not_running(received["task_id"])
            raise e
        
        register_event("service_cloud_ml","rpc_exec_start_server_task","Finished server task initialization",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
        register_event("service_cloud_ml","start_task_time",f"{tm.process_time_ns()-startTime}",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def rpc_exec_stop_server_task(self, received: dict):
        """
        Receives a validated JSON message for stopping a server task

        :param received: JSON containing task ID
        :type received: dict

        :raises: TaskIdNotFound

        :raises: TaskAlredyStopped

        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """
        register_event("service_cloud_ml","rpc_exec_stop_server_task","Started server task finalization",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        self.db_handler.set_task_not_running(received["task_id"])

        self.cloud_ml_backend.stop_task(received["task_id"])

        register_event("service_cloud_ml","rpc_exec_stop_server_task","Finished server task finalization",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def rpc_exec_client_requesting_task(self, received: dict) -> list:
        """
        Receives a validated JSON message from client and verify if there is a compatible task

        :param received: JSON containing client ID
        :type received: dict

        :return: list with selected tasks information (ID, host, port, tags, ...)
        :rtype: list
        """
        register_event("service_cloud_ml","rpc_exec_client_requesting_task","Started responding requested task to client",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        if received['user_id'] == 'xxxx':
            # Fake client, for tests
            client_info = {
                "ID": "guilhermeeec",
                "data_qnt": 323,
                "avg_acc_contrib": 0.12,
                "avg_disconnection_per_round": 0.44,
                "sensors": ["camera", "ecu"],
            }
        else:
            client_info = self.rpc_call_query_client_info(received['user_id'])
            if client_info is None:
                raise CouldNotRetrieveUser(received['user_id'])

        task_id_to_sel_crit_map = self.db_handler.get_task_selection_criteria_map()

        compatible_tasks_id_list = []
        for task_id, sel_crit_expression in task_id_to_sel_crit_map.items():
            try:
                is_compatible = eval_select_crit_expression(
                    sel_crit_expression, client_info
                )
                print(is_compatible)
                if is_compatible:
                    compatible_tasks_id_list.append(task_id)
            except InvalidSelCrit as e:
                print(f"Problem checking compatibility with task {task_id}: {e}")
                raise InvalidSelCrit

        task_att_sent_to_client = (
            "ID",
            "host",
            "port",
            "tags",
            "client_arguments",
            "username",
            "password",
            "files_paths",
        )
        tasks_info_list = []
        for task_id in compatible_tasks_id_list:
            task_info = self.db_handler.query_task(task_id)
            task_info_to_send = dict((k, task_info[k]) for k in task_att_sent_to_client)
            tasks_info_list.append(task_info_to_send)

        register_event("service_cloud_ml","rpc_exec_client_requesting_task","Finished responding requested task to client",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        return tasks_info_list

    def rpc_exec_update_task(self, received: dict):
        """
        Receives a validated JSON message with new info for a task

        :param received: JSON containing optional task info
        :type received: dict

        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """
        register_event("service_cloud_ml","rpc_exec_update_task","Started updating task",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        self.db_handler.update_task(
            task_id=received.get("task_id"),
            host=received.get("host"),
            port=received.get("port"),
            running=received.get("port"),
            selection_criteria=received.get("selection_criteria"),
            server_arguments=received.get("server_arguments"),
            client_arguments=received.get("client_arguments"),
            username=received.get("username"),
            password=received.get("password"),
        )

        register_event("service_cloud_ml","rpc_exec_update_task","Finished updating task",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def rpc_call_query_client_info(self, client_id: str) -> dict:
        """
        Send an RPC message for client manager service with client ID requesting for its info

        :param client_id: client ID
        :type client_id: str

        :returns: returned JSON from RPC with client info
        :rtype: dicts
        """
        register_event("service_cloud_ml","rpc_call_query_client_info","Started querying client info",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        response = rpc_send("rpc_exec_get_user_info",{"user_id":client_id},
                            host=self.broker_host, port=self.broker_port)
        if response.get("status_code") != 200:
            print(f"Failded to get user info: {response.get("exception")}")
            return None
        
        register_event("service_cloud_ml","rpc_call_query_client_info","Finished querying client info",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        return response["return"]
    
    def rpc_exec_get_task_by_id(self, received:dict):
        task_dict = self.db_handler.query_task(received.get("task_id"))
        return task_dict

if __name__ == "__main__":
    configs = configparser.ConfigParser()
    configs.read("config.ini")

    host = configs["server.broker"]["host"]
    port = int(configs["server.broker"]["port"])
    allow_register = configs.getboolean("events","register_events")

    def signal_handler(sig,frame):
        register_event("service_cloud_ml","main","Interrupted",allow_registering=allow_register,host=host,port=port)
        service.cloud_ml_backend.finish_all()
        service.stop()
        exit(0)
        
    service = ServiceCloudML(
        os.path.join(Path().resolve(),"cloud_task_manager"), 
        host, 
        port)
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        service.start()
    except Exception as e:
        service.cloud_ml_backend.finish_all()
        service.stop()
