from cloud_ml import CloudML
from stub_process_messages_from_task import StubForwardMessagesFromTask
from task_daemon_lib.task_exceptions import TaskAlredyStopped
from tasks_db_interface import TasksDbInterface
from criteria_evaluation_engine import *

class StubServiceCloudML:
    """
    Main class for Cloud Task Manager microservice
    This is a stub that executes the methods for starting/stopping a task at server side,
    but they are not yet connected to the RabbitMQ RPC system  

    :param workpath: project location, within which "tasks" dir resides
    :type workpath: str
    """
    def __init__(
        self,
        workpath:str) -> None:
        
        self.cloud_ml_backend = CloudML(workpath)
        self.db_handler = TasksDbInterface(workpath)

    def handle_error_from_task(self, task_id:str):
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

    def rpc_exec_create_task(self, received):
        """
        Receives a validated JSON message for configuring a new task in database, but not start yet
        
        :param received: JSON containing task ID, host, port, arguments, selection criteria, and tags
        :type received: dict

        :raises: sqlite3.IntegrityError
        """
        self.db_handler.insert_task(
            task_id=received['task_id'],
            host=received['host'],
            port=received['port'],
            selection_criteria=received.get('selection_criteria'),
            arguments=received.get('arguments'),
            tags=received.get('tags')
        )

    def rpc_exec_start_server_task(self, received:dict):
        """
        Receives a validated JSON message for starting a server task
        Validation occurs using our RPC library 
        
        :param received: JSON containing task ID
        :type received: dict

        :raises: FileNotFoundError 
        
        :raises: TaskIdAlredyInUse
        
        :raises: TaskAlredyRunning

        :raises: PermissionError

        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """
        forwarder = StubForwardMessagesFromTask(
            received['task_id'],
            self.handle_error_from_task)
        callback = forwarder.process_messages

        preinserted_task_info_dict = self.db_handler.query_task(received['task_id'])
        if received.get('arguments') is not None:
            # Case 1: arguments informed by received argument
            arguments = received.get('arguments')
        else:
            # Case 2: default arguments, regstered in DB 
            arguments = preinserted_task_info_dict.get('ID')

        self.db_handler.set_task_running(received['task_id'])

        try:
            self.cloud_ml_backend.start_new_task(
                received['task_id'],
                callback,
                arguments
            )
        except Exception as e:
            self.db_handler.set_task_not_running(received['task_id'])
            raise e

    def rpc_exec_stop_server_task(self, received:dict):
        """
        Receives a validated JSON message for stopping a server task
        
        :param received: JSON containing task ID
        :type received: dict

        :raises: TaskIdNotFound
        
        :raises: TaskAlredyStopped
        
        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """
        self.db_handler.set_task_not_running(received['task_id'])

        self.cloud_ml_backend.stop_task(received['task_id'])

    def rpc_exec_client_requesting_task(self, received: dict) -> list:
        """
        Receives a validated JSON message from client and verify if there is a compatible task

        :param received: JSON containing client ID
        :type received: dict

        :return: list with selected tasks information (ID, host, port, tags)
        :rtype: list
        """
        client_info = self.rpc_call_query_client_info(received['client_id'])
        task_id_to_sel_crit_map = self.db_handler.get_task_selection_criteria_map()
        
        compatible_tasks_id_list = []
        for task_id, sel_crit_expression in task_id_to_sel_crit_map.items():
            try:
                is_compatible = eval_select_crit_expression(sel_crit_expression, client_info)
                print(is_compatible)
                if is_compatible:
                    compatible_tasks_id_list.append(task_id)
            except InvalidSelCrit as e:
                print(f"Problem checking compatibility with task {task_id}: {e}")

        task_att_sent_to_client = ("ID","host","port","tags")
        tasks_info_list = []
        for task_id in compatible_tasks_id_list:
            task_info = self.db_handler.query_task(task_id)
            task_info_to_send = dict((k, task_info[k]) for k in task_att_sent_to_client)
            tasks_info_list.append(task_info_to_send)
        
        return tasks_info_list
    
    def rpc_exec_update_task(self, received:dict):
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
            arguments=received.get("arguments")
        )

    def rpc_call_query_client_info(self, client_id:str) -> dict:
        """
        Send an RPC message for client manager service with client ID requesting for its info

        :param client_id: client ID
        :type client_id: str

        :returns: returned JSON from RPC with client info
        :rtype: dicts
        """
        pass
        """
        rpc_client = RpcClient("query_client_info")
        request = {"client_id":client_id}
        response = rpc_client.call(request)
        """
        # Fake response. Should get from cloud client manager service DB using the code above
        return {
            "ID":"guilhermeeec",
            "data_qnt":323,
            "avg_acc_contrib":0.12,
            "avg_disconnection_per_round":0.44,
            "has_camera":False,
            "has_gw_ecu":True
        }
