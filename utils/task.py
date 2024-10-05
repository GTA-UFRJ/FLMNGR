import os
import subprocess
import sys
from task_exceptions import *
from udp_task_listener import UdpTaskMessageListener

class Task:

    def __init__(self, work_path: str, task_id: str) -> None:
        self.task_id = task_id
        self.task_dir_name = self.get_task_directory_name(work_path, task_id)
        self.forced_termination_timeout = 5
        self.running = False

    def get_task_id(self) -> str:
        return self.task_id

    def get_task_directory_name(self, work_path:str, task_id:str):
        task_dir_name = os.path.join(work_path, f"task_{task_id}")
        if not os.path.isdir(task_dir_name):
            raise FileNotFoundError(f"Directory '{task_dir_name}' does not exist.")
        return task_dir_name
    
    def start_message_listener(self, message_handler):
        self.message_listener = UdpTaskMessageListener(message_handler)
        self.message_listener.start()

    def stop_message_listener(self):
        self.message_listener.stop()

    def run_task(self, filename:str, message_handler, arguments:list[str]):
        if self.running:
            raise TaskAlredyRunning(self.task_id)
        
        self.start_message_listener(message_handler)

        execution_command_list = [sys.executable, filename, str(self.message_listener.port)]
        if arguments:
            execution_command_list.extend(arguments)

        try:
            self.process = subprocess.Popen(execution_command_list)
            print(f"Started {self.process}")
            self.running = True
        except PermissionError:
            print(f"Error: Permission denied for '{filename}'.")
            raise PermissionError(f"Error: Permission denied for '{filename}'.")

    def stop_task(self):
        if not self.running:
            raise TaskAlredyStopped(self.task_id)
        if not self.process:
            raise ValueError(f"No running process found for task_id")
        print("Terminating process")
        self.process.terminate()
        self.wait_and_force_termination_after_waiting()
        self.stop_message_listener()
        self.running = False
    
    def wait_and_force_termination_after_waiting(self):
        try:
            self.process.wait(timeout=self.forced_termination_timeout)  
        except subprocess.TimeoutExpired:
            self.process.kill()
