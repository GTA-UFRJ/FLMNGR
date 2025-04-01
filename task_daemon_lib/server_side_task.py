from task_daemon_lib.task import Task
import os
from time import sleep
from pathlib import Path
from typing import Callable

class ServerSideTask(Task):
    """
    Interface for running Flower server code as a child process

    :param work_path: project location, within which "tasks" dir resides
    :type work_path: str

    :param task_id: task ID
    :type task_id: str

    :param messange_handler: handler function for receiving bytes sent by process
    :type messange_handler: Callable[[bytes],None]

    :param arguments: CLI args after "python3 {filename} {work_path} ..."
    :type arguments: list[str]

    :raises FileNotFoundError: "{work_path}/tasks/task_{task_id}/server.py" does not exist
    """
    def __init__(self, work_path: str, task_id: str, messange_handler:Callable[[bytes],None], arguments: list[str] = None) -> None:
        super().__init__(work_path, task_id)
        self.server_main_file_name = self._get_server_main_file_name(self.task_dir_name)
        self.arguments = arguments
        self.message_handler = messange_handler

    def _get_server_main_file_name(self, task_dir_name:str): 
        server_file_name = os.path.join(task_dir_name, 'server.py')
        if not os.path.isfile(server_file_name):
            raise FileNotFoundError(f"File '{server_file_name}' not found in directory '{task_dir_name}'.")
        return server_file_name

    def run_task_server(self):
        """
        Run "{work_path}/tasks/task_{task_id}/server.py" as a subprocess and starts message 
        listener, which calls self.message_handler(bytes) uppon receiving bytes from child
        
        :raises TaskAlredyRunning: starting a task that is alredy running

        :raises PermissionError: doesn't have permission to run the task script  
        """
        self.run_task(
            self.server_main_file_name, 
            self.message_handler,
            self.arguments)

    def stop_task_server(self):
        """
        Stop process and message listener

        :raises TaskAlredyStopped: stopping a task that is not running
        """
        self.stop_task()

def message_handler(message: bytes):
    print("Received by handler: ", message.decode("utf8").strip())

if __name__ == "__main__":
    server_task = ServerSideTask(str(Path().resolve()), "4fe5", message_handler)
    server_task.run_task_server()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server_task.stop_task_server()
    