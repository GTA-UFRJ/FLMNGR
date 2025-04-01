import os
import subprocess
import sys
from task_daemon_lib.task_exceptions import *
from task_daemon_lib.task_listener import TaskMessageListener
from typing import Callable

class Task:
    """
    A Task is an interface for running code as a child process
    This is a base class, inherited by ClientSideTask and ServerSideTask

    :param work_path: project location, within which "tasks" dir resides
    :type work_path: str

    :param task_id: hexadecimal number identifying task
    :type task_id: str

    :raises FileNotFoundError: no directory named "{work_path}/tasks/task_{task_id}"
    """
    def __init__(self, work_path: str, task_id: str, enable_listener:bool=True) -> None:
        self.work_path = work_path
        self.task_id = task_id
        self.task_dir_name = self._get_task_directory_name(task_id)
        self.forced_termination_timeout = 5
        self.running = False
        self.enable_listener = enable_listener

    def get_task_id(self) -> str:
        return self.task_id

    def _get_task_directory_name(self, task_id:str):
        task_dir_name = os.path.join(self.work_path, f"tasks/task_{task_id}")
        if not os.path.isdir(task_dir_name):
            raise FileNotFoundError(f"Directory '{task_dir_name}' does not exist.")
        return task_dir_name
    
    def _start_message_listener(self, message_handler:Callable[[bytes],None]):
        self.message_listener = TaskMessageListener(message_handler, self.process)
        self.message_listener.start()

    def _stop_message_listener(self):
        self.message_listener.stop()

    def run_task(self, filename:str, message_handler:Callable[[bytes],None], arguments:list[str], add_work_path:bool=True):
        """
        Start child process with 'filename', as well as the message listener

        :param filename: complete path for executable file
        :type filename: str

        :param message_handler: handler function for receiving bytes sent by process
        :type message_handler: Callable[[bytes],None]
        
        :param arguments: CLI args after "python3 {filename} {work_path} ..."
        :type arguments: list[str]
        
        :param add_work_path: if true, call "python3 {filename} {work_path} {args}". Else, call "python3 {filename} {args}"
        :type add_work_path: bool

        :raises TaskAlredyRunning: starting a task that is alredy running

        :raises PermissionError: doesn't have permission to run the task script  
        """
        if self.running:
            raise TaskAlredyRunning(self.task_id)

        if add_work_path:
            execution_command_list = [sys.executable, 
                                    filename, 
                                    self.work_path]
        else:
            execution_command_list = [sys.executable, 
                                    filename]
            
        if arguments:
            execution_command_list.extend(arguments)

        try:
            self.process = subprocess.Popen(execution_command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if self.enable_listener:
                self._start_message_listener(message_handler)
            print(f"Started {self.process}")
            self.running = True
        except PermissionError:
            print(f"Error: Permission denied for '{filename}'.")
            raise PermissionError(f"Error: Permission denied for '{filename}'.")

    def stop_task(self):
        """
        Stop child process started before, as well as the message listener

        :raises TaskAlredyStopped: stopping a task that is not running
        """
        if (not self.running) or (not self.process):
            raise TaskAlredyStopped(self.task_id)
        print("Terminating process")
        self.process.terminate()
        self._wait_and_force_termination_after_waiting()
        if self.enable_listener:
            self._stop_message_listener()
        self.running = False
    
    def _wait_and_force_termination_after_waiting(self):
        try:
            self.process.wait(timeout=self.forced_termination_timeout)  
        except subprocess.TimeoutExpired:
            self.process.kill()
