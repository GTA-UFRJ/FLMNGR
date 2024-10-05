from task import Task
import os
from time import sleep

class ServerSideTask(Task):

    def __init__(self, work_path: str, task_id: str, arguments: list[str] = None) -> None:
        super().__init__(work_path, task_id)
        self.server_main_file_name = self.get_server_main_file_name(self.task_dir_name)
        self.arguments = arguments

    def get_server_main_file_name(self, task_dir_name:str): 
        server_file_name = os.path.join(task_dir_name, 'server.py')
        if not os.path.isfile(server_file_name):
            raise FileNotFoundError(f"File '{server_file_name}' not found in directory '{task_dir_name}'.")
        return server_file_name

    def run_task_server(self):
        self.run_task(self.server_main_file_name, self.arguments)

    def stop_task_server(self):
        self.stop_task()

if __name__ == "__main__":
    server_task = ServerSideTask("/home/guiaraujo/FLMNGR/tasks", "4fe5")
    server_task.run_task_server()
    sleep(10)
    server_task.stop_task_server()
    