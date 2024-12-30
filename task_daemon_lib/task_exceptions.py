
class TaskIdAlredyInUse(Exception):
    def __init__(self, task_id:str):
        super().__init__(f"Task with ID={task_id} alredy exists")

class TaskAlredyRunning(Exception):
    def __init__(self, task_id:str):
        super().__init__(f"Task with ID={task_id} alredy running")

class TaskAlredyStopped(Exception):
    def __init__(self, task_id:str):
        super().__init__(f"Task with ID={task_id} alredy stopped")

class TaskIdNotFound(Exception):
    def __init__(self, task_id:str):
        super().__init__(f"Task with ID={task_id} not found")

class TaskUnknownMessageType(Exception):
    def __init__(self):
        super().__init__(f"Unknown message type sent by task")