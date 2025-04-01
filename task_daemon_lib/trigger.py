from task_daemon_lib.task import Task
import os
from pathlib import Path

class Trigger(Task):
    """
    Interface for running server trigger code as a child process

    :param work_path: project location, within which "tasks" dir resides. If "{work_path}/tasks/task_{task_id}/{trigger_id}" does not exist, raises Exception
    :type work_path: str

    :param task_id: especifies the task that triggered
    :type task_id: str

    :param trigger_id: name of trigger Python code file 
    :type trigger_id: str

    :param arguments: CLI args after "python3 {filename} ..."
    :type arguments: list[str]

    :raises: FileNotFoundError 
    """
    def __init__(self, work_path: str, task_id: str, trigger_id:str, arguments: list[str] = None) -> None:
        super().__init__(work_path, task_id, enable_listener=False)
        self.trigger_file_name = self._get_trigger_main_file_name(self.task_dir_name, trigger_id)
        self.arguments = arguments
        def dummy_handler(received:bytes):
            return
        self.message_handler = dummy_handler

    def _get_trigger_main_file_name(self, task_dir_name:str, trigger_id:str): 
        trigger_file_name = os.path.join(task_dir_name, f"{trigger_id}.py")
        if not os.path.isfile(trigger_file_name):
            raise FileNotFoundError(f"File '{trigger_file_name}' not found in directory '{task_dir_name}'.")
        return trigger_file_name

    def run_trigger(self):
        """
        Run "{work_path}/tasks/task_{task_id}/{trigger_id}.py as a subprocess and starts message 
        listener, which calls self.message_handler(bytes) uppon receiving bytes from child
        
        :raises: TaskAlredyRunning

        :raises: PermissionError
        """
        self.run_task(
            self.trigger_file_name, 
            self.message_handler, 
            self.arguments,
            add_work_path=False)

    def stop_trigger(self):
        """
        Stop process and message listener

        :raises: TaskAlredyStopped
        """
        self.stop_task()

if __name__ == "__main__":
    trigger = Trigger(str(Path().resolve()), "4fe5", "trigger_example", "acc")
    trigger.run_trigger()
    