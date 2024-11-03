from task_daemon_lib.server_side_task import ServerSideTask
from task_daemon_lib.task_exceptions import *

# Start and stop multiple server-side tasks
class CloudML:

    def __init__(self, work_path:str) -> None:
        self.task_id_to_task_object_map = {}
        self.work_path = work_path

    def insert_new_task_in_map(self, task_id:str, server_side_task_object:ServerSideTask) -> ServerSideTask:
        if task_id in self.task_id_to_task_object_map:
            raise TaskIdAlredyInUse(task_id)
        print(f"Added task {task_id}")
        self.task_id_to_task_object_map[task_id] = server_side_task_object

    def remove_task_from_map(self, task_id:str) -> ServerSideTask:
        try:
            return self.task_id_to_task_object_map.pop(task_id)
        except KeyError as e:
            raise TaskIdNotFound(task_id)

    def start_new_task(self, task_id:str, message_handler, arguments:str): 
        if arguments is None:
            arguments_list = None
        else:
            arguments_list = arguments.split(" ")
        
        server_side_task_object = ServerSideTask(
            self.work_path, 
            task_id,
            message_handler,
            arguments_list)
        
        self.insert_new_task_in_map(task_id, server_side_task_object)
        server_side_task_object.run_task_server()

    def stop_task(self, task_id:str):
        server_side_task_object = self.remove_task_from_map(task_id)
        server_side_task_object.stop_task_server()

    def finish_all(self):
        print("Abort all tasks!")
        for task_id, server_side_task_object in self.task_id_to_task_object_map.items():
            server_side_task_object.stop_task_server()