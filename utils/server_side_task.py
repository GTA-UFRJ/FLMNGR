from utils.task import Task
import os
from time import sleep
from pathlib import Path

class ServerSideTask(Task):

    def __init__(self, work_path: str, task_id: str, messange_handler, arguments: list[str] = None) -> None:
        super().__init__(work_path, task_id)
        self.server_main_file_name = self.get_server_main_file_name(self.task_dir_name)
        self.arguments = arguments
        self.message_handler = messange_handler

    def get_server_main_file_name(self, task_dir_name:str): 
        server_file_name = os.path.join(task_dir_name, 'server.py')
        if not os.path.isfile(server_file_name):
            raise FileNotFoundError(f"File '{server_file_name}' not found in directory '{task_dir_name}'.")
        return server_file_name

    def run_task_server(self):
        self.run_task(
            self.server_main_file_name, 
            self.message_handler, 
            self.arguments)

    def stop_task_server(self):
        self.stop_task()

def message_handler(message: bytes):
    print("Handled message: ",message)

if __name__ == "__main__":
    server_task = ServerSideTask(str(Path().resolve()), "4fe5", message_handler)
    server_task.run_task_server()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server_task.stop_task_server()
    