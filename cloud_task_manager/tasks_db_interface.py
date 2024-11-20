import os
import sqlite3
from pathlib import Path
from datetime import datetime

class TasksDbInterface:

    def __init__(self, work_path: str):
        self.db_path = os.path.join(work_path,"db/tasks.db")
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        
        self._create_tasks_table_if_not_exists()
        self._create_tags_table_if_not_exists()

    def _create_tasks_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            creation_date TEXT NOT NULL,
            last_mod_date TEXT NOT NULL,
            ID TEXT PRIMARY KEY,
            host TEXT NOT NULL,
            port INTEGER CHECK(port >= 0 AND port <= 65535),
            running BOOLEAN,
            selection_criteria TEXT
        );
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def _create_tags_table_if_not_exists(self):
        create_tags_table_query = """
        CREATE TABLE IF NOT EXISTS tags (
            ID TEXT NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (ID) REFERENCES tasks(ID)
        );
        """
        self.cursor.execute(create_tags_table_query)
        self.connection.commit()

    def _insert_into_tasks_table(self, task_id:str, host:str, port:int, selection_criteria:str):
        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_mod_date = creation_date
        insert_task_table_query = """
        INSERT INTO tasks (
            creation_date, 
            last_mod_date, 
            ID, 
            host, 
            port, 
            running, 
            selection_criteria)
        VALUES (?, ?, ?, ?, ?, ?, ?); 
        """
        self.cursor.execute(insert_task_table_query,
            (creation_date, last_mod_date, task_id, host, port, "FALSE", selection_criteria))

    def _insert_into_tags_table(self, task_id:str, tags:list[str]):
        for tag in tags:
            self.cursor.execute("""
                INSERT INTO tags (ID, tag)
                VALUES (?, ?);
            """, (task_id, tag))

    def insert_task(self, task_id:str, host:str, port:int, selection_criteria:str="", tags:list[str]=None):
        """
        Insert a new task into the tasks table and optionally insert tags.
        
        :param task_id: Unique identifier for the task (4 hex digits).
        :type task_id: str

        :param host: hostname or IP of the server
        :type host: str

        :param port: network port number of the server (unsigned 16-bit integer).
        :type port: int

        :param selection_criteria: boolean expression for selecting clients using its atributes
        :type selection_criteria: str
        
        :param tags: A list of tags associated with the task (optional).
        :type tags: list[str]

        :raises: sqlite3.IntegrityError
        """
        self._insert_into_tasks_table(task_id, host, port, selection_criteria)
        
        if tags:
            self._insert_into_tags_table(task_id, tags)
        
        self.connection.commit()
        print(f"Task {task_id} inserted successfully.")

    def set_task_running(self, task_id:str):
        """
        Set a task as running by its ID.
        
        :param task_id: The ID of the task to update
        :type task_id: str

        :raises: sqlite3.Error
        """
        last_mod_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            UPDATE tasks
            SET running = TRUE, last_mod_date = ?
            WHERE ID = ?;
        """, (last_mod_date, task_id))
        self.connection.commit()
        print(f"Task {task_id} is now set to running.")

    def set_task_not_running(self, task_id):
        """
        Set a task as not running by its ID.
        
        :param task_id: The ID of the task to update
        :type task_id: str

        :raises: sqlite3.Error
        """
        last_mod_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            UPDATE tasks
            SET running = FALSE, last_mod_date = ?
            WHERE ID = ?;
        """, (last_mod_date, task_id))
        self.connection.commit()
        print(f"Task {task_id} is now set to running.")

    def close(self):
        """
        Close the database connection
        """
        if self.connection:
            self.connection.close()

if __name__ == "__main__":
    db_interface = TasksDbInterface(str(Path().resolve()))
    db_interface.insert_task(
        task_id="2a2b",
        host="192.168.1.1",
        port=8080,
        selection_criteria="priority",
        tags=["mnist"]
    )
    db_interface.set_task_running("2a2b")
    db_interface.close()
