from cloud_ml import CloudML
from stub_process_messages_from_task import StubForwardMessagesFromTask
from task_daemon_lib.task_exceptions import TaskAlredyStopped
from tasks_db_interface import TasksDbInterface

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