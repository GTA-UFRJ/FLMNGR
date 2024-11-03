from task_daemon_lib.task import Task
import os
from time import sleep
from pathlib import Path
from typing import Callable

class ServerSideTask(Task):

    def __init__(self, work_path: str, task_id: str, messange_handler:Callable[[bytes],None], arguments: list[str] = None) -> None:
        """
        Interface for running Flower server code as a child process

        :param work_path: project location, within which "tasks" dir resides. If "{work_path}/tasks/task_{task_id}/server.py" does not exist, raises Exception
        :type work_path: str

        :param messange_handler: handler function for receiving bytes sent by process
        :type task_id: Callable[[bytes],None]

        :param arguments: CLI args after "python3 {filename} {work_path} ..."
        :type arguments: list[str]

        :raises: FileNotFoundError 
        """
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
        
        :raises: TaskAlredyRunning

        :raises: PermissionError
        """
        self.run_task(
            self.server_main_file_name, 
            self.message_handler,
            self.arguments)

    def stop_task_server(self):
        """
        Stop process and message listener

        :raises: TaskAlredyStopped
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
    