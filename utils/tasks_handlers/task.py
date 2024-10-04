import os
import subprocess
import sys

class Task:

    def __init__(self, work_path: str, task_id: str) -> None:
        self.task_dir_name = self.get_task_directory_name(work_path, task_id)
        self.forced_termination_timeout = 5

    def get_task_directory_name(self, work_path:str, task_id:str):
        task_dir_name = os.path.join(work_path, f"task_{task_id}")
        if not os.path.isdir(task_dir_name):
            raise FileNotFoundError(f"Directory '{task_dir_name}' does not exist.")
        return task_dir_name
    
    def run_task(self, filename:str):
        try:
            self.process = subprocess.Popen([sys.executable, filename])
            print(f"Started {self.process}")
        except PermissionError:
            print(f"Error: Permission denied for '{filename}'.")

    def stop_task(self):
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
