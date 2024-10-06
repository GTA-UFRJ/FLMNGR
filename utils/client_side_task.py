from utils.task import Task
import os
from time import sleep
from pathlib import Path

class ClientSideTask(Task):

    def __init__(self, work_path: str, task_id: str, messange_handler, arguments: list[str] = None) -> None:
        super().__init__(work_path, task_id)
        self.client_main_file_name = self.get_client_main_file_name(self.task_dir_name)
        self.arguments = arguments
        self.message_handler = messange_handler

    def get_client_main_file_name(self, task_dir_name:str): 
        client_file_name = os.path.join(task_dir_name, 'client.py')
        if not os.path.isfile(client_file_name):
            raise FileNotFoundError(f"File '{client_file_name}' not found in directory '{task_dir_name}'.")
        return client_file_name

    def run_task_client(self):
        self.run_task(self.client_main_file_name, self.message_handler, self.arguments)

    def stop_task_client(self):
        self.stop_task()


def message_handler(message: bytes):
    print(message)

if __name__ == "__main__":
    client_task = ClientSideTask(str(Path().resolve()), "4fe5", message_handler)
    client_task.run_task_client()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        client_task.stop_task_server()
    