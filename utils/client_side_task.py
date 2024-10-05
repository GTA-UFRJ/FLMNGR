from task import Task
import os
from time import sleep

class ClientSideTask(Task):

    def __init__(self, work_path: str, task_id: str, arguments: list[str] = None) -> None:
        super().__init__(work_path, task_id)
        self.client_main_file_name = self.get_client_main_file_name(self.task_dir_name)
        self.arguments = arguments

    def get_client_main_file_name(self, task_dir_name:str): 
        client_file_name = os.path.join(task_dir_name, 'client.py')
        if not os.path.isfile(client_file_name):
            raise FileNotFoundError(f"File '{client_file_name}' not found in directory '{task_dir_name}'.")
        return client_file_name

    def run_task_client(self):
        self.run_task(self.client_main_file_name, self.arguments)

    def stop_task_client(self):
        self.stop_task()

if __name__ == "__main__":
    client_task = ClientSideTask("/home/guiaraujo/FLMNGR/tasks", "4fe5")
    client_task.run_task_client()
    sleep(10)
    client_task.stop_task_client()
    