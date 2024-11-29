from task_daemon_lib.client_side_task import ClientSideTask
from task_daemon_lib.task_exceptions import *
from typing import Callable

class ClientML:
    """
    Start and stop client-side tasks. Mantain client-side tasks OBJECTS in a map using task ID as key

    :param work_path: project location, within which "tasks" dir resides
    :type work_path: str
    """
    def __init__(self, work_path:str) -> None:
        self.task_id_to_task_object_map = {}
        self.work_path = work_path

    def _insert_new_task_in_map(self, task_id:str, client_side_task_object:ClientSideTask) -> ClientSideTask:
        """
        Inserts new started task in map (private)
        
        :param task_id: task ID
        :type task_id: str

        :param client_side_task_object: task handler, used to run and stop process
        :type client_side_task_object: ClientSideTask
        
        :raises: TaskIdAlredyInUse

        :return: inserted task object 
        :rtype: ClientSideTask
        """
        if task_id in self.task_id_to_task_object_map:
            raise TaskIdAlredyInUse(task_id)
        print(f"Added task {task_id}")
        self.task_id_to_task_object_map[task_id] = client_side_task_object

    def _remove_task_from_map(self, task_id:str) -> ClientSideTask:
        """
        Removes stopped task from map  
        
        :param task_id: task ID
        :type task_id: str
        
        :raises: TaskIdNotFound

        :return: removed task object 
        :rtype: ClientSideTask
        """
        try:
            return self.task_id_to_task_object_map.pop(task_id)
        except KeyError as e:
            raise TaskIdNotFound(task_id)

    def start_new_task(self, task_id:str, message_handler:Callable[[bytes],None], arguments:str): 
        """
        Start mew task and inserts in the map 
        
        :param task_id: task ID
        :type task_id: str
        
        :param message_handler: function to forward received messages from task
        :type message_handler: Callable[[bytes],None]
        
        :param arguments: string to append to the command with arguments separated by " "
        :type arguments: str
        
        :raises: FileNotFoundError 
        
        :raises: TaskIdAlredyInUse

        :raises: TaskAlredyRunning

        :raises: PermissionError
        """
        if arguments is None:
            arguments_list = None
        else:
            arguments_list = arguments.split(" ")

        client_side_task = ClientSideTask(
            self.work_path, 
            task_id,
            message_handler,
            arguments_list)
        
        self._insert_new_task_in_map(task_id, client_side_task)
        client_side_task.run_task_client()

    def stop_task(self, task_id:str):
        """
        Stop task and removes from the map 
        
        :param task_id: task ID
        :type task_id: str
        
        :raises: TaskIdNotFound 
        
        :raises: TaskAlredyStopped
        """
        client_side_task_object = self._remove_task_from_map(task_id)
        client_side_task_object.stop_task_client()

    def finish_all(self):
        """
        Finishes all tasks
        """

        print("Stopping all tasks!")
        for task_id in self.task_id_to_task_object_map.keys():
            try:
                self.stop_task(task_id)
                print(f"Stopped task {task_id}")
            except TaskAlredyStopped:
                print(f"Task {task_id} was alredy stopped")
    
    def get_running_tasks(self) -> list:
        """
        Returns a list with running task's IDs
        """
        return self.task_id_to_task_object_map.keys() 
