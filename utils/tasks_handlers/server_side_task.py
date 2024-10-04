import os
import subprocess
import sys
from time import sleep

# Start and stop Flower server as a child process
class ServerSideTask:

    def __init__(self, work_path: str, task_id: str) -> None:
        task_dir_name = self.get_task_directory_name(work_path, task_id)
        self.server_main_file_name = self.get_server_main_file_name(task_dir_name)
        self.forced_termination_timeout = 5

    def get_task_directory_name(self, work_path:str, task_id:str):
        task_dir_name = os.path.join(work_path, f"task_{task_id}")
        if not os.path.isdir(task_dir_name):
            raise FileNotFoundError(f"Directory '{task_dir_name}' does not exist.")
        return task_dir_name

    def get_server_main_file_name(self, task_dir_name:str): 
        server_file_name = os.path.join(task_dir_name, 'server.py')
        if not os.path.isfile(server_file_name):
            raise FileNotFoundError(f"File '{server_file_name}' not found in directory '{task_dir_name}'.")
        return server_file_name

    def run_task_server(self):
        try:
            self.process = subprocess.Popen([sys.executable, self.server_main_file_name])
            print(f"Started {self.process}")
        except PermissionError:
            print(f"Error: Permission denied for '{self.server_main_file_name}'.")

    def stop_task_server(self):
        if self.process is None:
            raise ValueError(f"No running process found for task_id")
        print("Terminating process")
        self.process.terminate()
        self.wait_and_force_termination_after_waiting()
    
    def wait_and_force_termination_after_waiting(self):
        try:
            self.process.wait(timeout=self.forced_termination_timeout)  
        except subprocess.TimeoutExpired:
            self.process.kill()

if __name__ == "__main__":
    server_task = ServerSideTask("/home/guiaraujo/FLMNGR/tasks", "4fe5")
    server_task.run_task_server()
    sleep(10)
    server_task.stop_task_server()
    