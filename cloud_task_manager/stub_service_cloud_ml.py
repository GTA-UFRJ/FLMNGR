from cloud_ml import CloudML
from stub_process_messages_from_task import StubForwardMessagesFromTask
from task_daemon_lib.task_exceptions import TaskAlredyStopped

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

    def finish_cloud_ml(self):
        """
        Finishes all tasks
        """
        self.cloud_ml_backend.finish_all()

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

    def rpc_exec_start_server_task(self, received:dict):
        """
        Receives a validated JSON message for starting a server task
        Validation occurs using our RPC library 
        
        :param received: JSON containing task ID, arguments, selection criteria, and tags for starting task
        :type received: dict

        :raises: FileNotFoundError 
        
        :raises: TaskIdAlredyInUse
        
        :raises: TaskAlredyRunning

        :raises: PermissionError
        """
        forwarder = StubForwardMessagesFromTask(
            received['task_id'],
            self.handle_error_from_task)
        callback = forwarder.process_messages

        # Selection criteria and tags not yet used

        self.cloud_ml_backend.start_new_task(
            received['task_id'],
            callback,
            received.get('arguments')
        )

    def rpc_exec_stop_server_task(self, received:dict):
        """
        Receives a validated JSON message for stopping a server task
        Validation occurs using our RPC library 
        
        :param received: JSON containing task ID
        :type received: dict

        :raises: TaskIdNotFound
        
        :raises: TaskAlredyStopped
        """
        self.cloud_ml_backend.stop_task(received['task_id'])