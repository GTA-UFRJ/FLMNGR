import os
import json
import time as tm
import configparser
from pathlib import Path

from cloud_task_manager.cloud_ml import CloudML
from cloud_task_manager.criteria_evaluation_engine import *
from cloud_task_manager.tasks_db_interface import TasksDbInterface
from microservice_interconnect.rpc_client import rpc_send
from task_daemon_lib.task_exceptions import TaskAlredyStopped
from microservice_interconnect.base_service import BaseService
from cloud_task_manager.process_messages_from_task import ForwardMessagesFromTask

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
        self.broker_port
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
        try:
            self.cloud_ml_backend.stop_task(task_id)
        except TaskAlredyStopped:
            print(f"Received error from task {task_id}, which was alredy stopped")

    def rpc_exec_create_task(self, received: dict):
        """
        Receives a validated JSON message for configuring a new task in database, but not start yet

        :param received: JSON containing task ID, host, port, arguments, selection criteria, tags, ...
        :type received: dict

        :raises: sqlite3.IntegrityError
        """
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
        if register_events:
            rpc_send(
                "events",
                {
                    "time": tm.time(),
                    "domain": "cloud",
                    "service": "service_cloud_ml.py",
                    "function": "rpc_exec_start_server_task",
                    "event": "Initialization",
                },
            )

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
        self.db_handler.set_task_not_running(received["task_id"])

        self.cloud_ml_backend.stop_task(received["task_id"])

    def rpc_exec_client_requesting_task(self, received: dict) -> list:
        """
        Receives a validated JSON message from client and verify if there is a compatible task

        :param received: JSON containing client ID
        :type received: dict

        :return: list with selected tasks information (ID, host, port, tags, ...)
        :rtype: list
        """
        client_info = self.rpc_call_query_client_info(received["client_id"])
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

        return tasks_info_list

    def rpc_exec_update_task(self, received: dict):
        """
        Receives a validated JSON message with new info for a task

        :param received: JSON containing optional task info
        :type received: dict

        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """
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

    def rpc_call_query_client_info(self, client_id: str) -> dict:
        """
        Send an RPC message for client manager service with client ID requesting for its info

        :param client_id: client ID
        :type client_id: str

        :returns: returned JSON from RPC with client info
        :rtype: dicts
        """

        # response = rpc_send("rpc_exec_query_client_info",{"client_id":client_id})

        # Fake response. Should get from cloud client manager service DB using the code above
        return {
            "ID": "guilhermeeec",
            "data_qnt": 323,
            "avg_acc_contrib": 0.12,
            "avg_disconnection_per_round": 0.44,
            "sensors": ["camera", "ecu"],
        }

if __name__ == "__main__":
    configs = configparser.ConfigParser()
    configs.read("config.ini")

    host = configs["server.broker"]["host"]
    port = int(configs["server.broker"]["port"])
    register_events = configs.getboolean("events","register_events")

    if register_events:
        rpc_send(
            "events",
            {
                "time": tm.time(),
                "domain": "cloud",
                "service": "service_cloud_ml.py",
                "function": "",
                "event": "Service initialization",
            },
            host,
            port,
        )
    service = ServiceCloudML(
        os.path.join(Path().resolve(),"cloud_task_manager"), 
        host, 
        port)
    try:
        service.start()
    except KeyboardInterrupt as e:
        service.stop()
