import os
import sqlite3
from pathlib import Path
from datetime import datetime
from pprint import pprint

class TaskNotRegistered(Exception):
    def __init__(self, task_id:str):
        super().__init__(f"Task with ID={task_id} not registered")

class TasksDbInterface:
    """
    Tasks DB handler

    :param workpath: project location, within which "tasks" dir resides
    :type workpath: str
    """
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
            selection_criteria TEXT,
            arguments TEXT
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

    def _insert_into_tasks_table(self, task_id:str, host:str, port:int, selection_criteria:str, arguments:str):
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
            selection_criteria,
            arguments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?); 
        """
        self.cursor.execute(insert_task_table_query,
            (creation_date, last_mod_date, task_id, host, port, "FALSE", selection_criteria, arguments))

    def _insert_into_tags_table(self, task_id:str, tags:list[str]):
        for tag in tags:
            self.cursor.execute("""
                INSERT INTO tags (ID, tag)
                VALUES (?, ?);
            """, (task_id, tag))

    def insert_task(self, task_id:str, host:str, port:int, selection_criteria:str="", arguments:str="", tags:list[str]=None):
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

        :param arguments: command line arguments used when starting the task (optional)  
        :type arguments: str
        
        :param tags: A list of tags associated with the task (optional).
        :type tags: list[str]

        :raises: sqlite3.IntegrityError
        """
        if selection_criteria is None:
            selection_criteria = ''

        if arguments is None:
            arguments = ''

        self._insert_into_tasks_table(task_id, host, port, selection_criteria, arguments)
        
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

        :raises: TaskNotRegistered
        """
        if self.query_task(task_id) is None:
            raise TaskNotRegistered(task_id)
        
        last_mod_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            UPDATE tasks
            SET running = TRUE, last_mod_date = ?
            WHERE ID = ?;
        """, (last_mod_date, task_id))
        self.connection.commit()
        print(f"Task {task_id} is now set to running.")

    def set_task_not_running(self, task_id:str):
        """
        Set a task as not running by its ID.
        
        :param task_id: The ID of the task to update
        :type task_id: str

        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """
        if self.query_task(task_id) is None:
            raise TaskNotRegistered(task_id)
        
        last_mod_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            UPDATE tasks
            SET running = FALSE, last_mod_date = ?
            WHERE ID = ?;
        """, (last_mod_date, task_id))
        self.connection.commit()

    def _select_from_tasks_table(self, task_id:str) -> list:
        self.cursor.execute("""
            SELECT 
                creation_date, 
                last_mod_date, 
                ID, 
                host, 
                port, 
                running, 
                selection_criteria,
                arguments
            FROM tasks
            WHERE ID = ?;
        """, (task_id,))
        return self.cursor.fetchone()
    
    def _select_from_tags_table(self, task_id:str) -> list[str]:
        self.cursor.execute("""
            SELECT tag
            FROM tags
            WHERE ID = ?;
        """, (task_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def query_task(self, task_id:str)->dict:
        """
        Query a task by its ID, including all associated attributes and tags.
        
        :param task_id: The ID of the task to query.
        :type task_id: str
        
        :return: A dictionary with task details and associated tags, or None if the task does not exist.
        :rtype: dict

        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """    
        task = self._select_from_tasks_table(task_id)
        if not task:
            raise TaskNotRegistered(task_id)
            
        tags = self._select_from_tags_table(task_id)
        
        return {
            "creation_date": task[0],
            "last_mod_date": task[1],
            "ID": task[2],
            "host": task[3],
            "port": task[4],
            "running": task[5],
            "selection_criteria": task[6],
            "arguments": task[7],
            "tags": tags
        }

    def get_task_selection_criteria_map(self)->dict:
        """
        Retrieve a dictionary mapping each task ID to its selection criteria.
        
        :return: A dictionary where keys are task IDs and values are selection criteria.
        :rtype: dict
        """

        self.cursor.execute("""
            SELECT ID, selection_criteria
            FROM tasks;
        """)
        rows = self.cursor.fetchall()
        
        task_map = {row[0]: row[1] for row in rows}
        return task_map

    def update_task(self, task_id:str, host:str=None, port:int=None, running:bool=None, selection_criteria:str=None, arguments:str=None):
        """
        Update an existing task with new values. Arguments with None are not updated.
        Not used yet

        :param task_id: The ID of the task to update
        :type task_id: str

        :param host: New hostname or IP address (optional)
        :type host: str

        :param port: New port number (optional)
        :type port: int

        :param running: New running status (optional)
        :type running: bool

        :param selection_criteria: New selection criteria (optional)
        :type selection_criteria: str

        :param arguments: new command line arguments used when starting the task (optional)  
        :type arguments: str

        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """
        if not task_id:
            return
        
        if self.query_task(task_id) is None:
            raise TaskNotRegistered(task_id)
        
        # Build the SQL update query dynamically based on non-None arguments
        fields = []
        values = []
        last_mod_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if host is not None:
            fields.append("host = ?")
            values.append(host)
        
        if port is not None:
            fields.append("port = ?")
            values.append(port)
        
        if running is not None:
            fields.append("running = ?")
            values.append(running)
        
        if selection_criteria is not None:
            fields.append("selection_criteria = ?")
            values.append(selection_criteria)

        if arguments is not None:
            fields.append("arguments = ?")
            values.append(arguments)
        
        # Always update the last modification date
        fields.append("last_mod_date = ?")
        values.append(last_mod_date)
        
        # Add the ID for the WHERE clause
        values.append(task_id)
        
        # Construct the final SQL query
        sql_query = f"""
            UPDATE tasks
            SET {', '.join(fields)}
            WHERE ID = ?;
        """
        
        self.cursor.execute(sql_query, values)
        self.connection.commit()
        print(f"Task {task_id} updated successfully.")

    def close(self):
        """
        Close the database connection
        """
        if self.connection:
            self.connection.close()

if __name__ == "__main__":
    db_interface = TasksDbInterface(str(Path().resolve()))
    db_interface.insert_task(task_id="1a2b", host="192.168.1.1", port=8080, selection_criteria="(has camera) and (data >= 30)", arguments=" arg1 arg2", tags=['mnist','mlp'])
    db_interface.insert_task(task_id="2b3c", host="192.168.1.2", port=9090)
    db_interface.set_task_running("1a2b")
    task_map = db_interface.get_task_selection_criteria_map()
    pprint(task_map)
    db_interface.close()
