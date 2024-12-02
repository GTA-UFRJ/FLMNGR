import os
import sqlite3
from pathlib import Path
from datetime import datetime
from pprint import pprint
from werkzeug.security import check_password_hash, generate_password_hash

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
        
        connection = sqlite3.connect(self.db_path)
        
        cursor = connection.cursor()
        self._create_tasks_table_if_not_exists(cursor)
        self._create_tags_table_if_not_exists(cursor)
        self._create_files_paths_table_if_not_exists(cursor)
        
        connection.commit()
        connection.close()

    def _create_tasks_table_if_not_exists(self, cursor:sqlite3.Cursor):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            creation_date TEXT NOT NULL,
            last_mod_date TEXT NOT NULL,
            ID TEXT PRIMARY KEY,
            host TEXT NOT NULL,
            port INTEGER CHECK(port >= 0 AND port <= 65535),
            running BOOLEAN,
            selection_criteria TEXT,
            server_arguments TEXT,
            client_arguments TEXT,
            username TEXT,
            password TEXT
        );
        """
        cursor.execute(create_table_query)

    def _create_tags_table_if_not_exists(self, cursor:sqlite3.Cursor):
        create_tags_table_query = """
        CREATE TABLE IF NOT EXISTS tags (
            ID TEXT NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (ID) REFERENCES tasks(ID)
        );
        """
        cursor.execute(create_tags_table_query)

    def _create_files_paths_table_if_not_exists(self, cursor:sqlite3.Cursor):
        create_files_paths_table_query = """
        CREATE TABLE IF NOT EXISTS files_paths (
            ID TEXT NOT NULL,
            file_path TEXT NOT NULL,
            FOREIGN KEY (ID) REFERENCES tasks(ID)
        );
        """
        cursor.execute(create_files_paths_table_query)

    def _insert_into_tasks_table(self,
        cursor:sqlite3.Cursor,
        task_id:str, 
        host:str, 
        port:int, 
        selection_criteria:str, 
        server_arguments:str, 
        client_arguments:str, 
        username:str, 
        password:str):

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
            server_arguments,
            client_arguments,
            username,
            password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); 
        """
        cursor.execute(insert_task_table_query,
            (creation_date, 
            last_mod_date, 
            task_id, 
            host, 
            port, 
            "FALSE", 
            selection_criteria, 
            server_arguments, 
            client_arguments, 
            username, 
            password))

    def _insert_into_tags_table(self, cursor:sqlite3.Cursor, task_id:str, tags:list):
        for tag in tags:
            cursor.execute("""
                INSERT INTO tags (ID, tag)
                VALUES (?, ?);
            """, (task_id, tag))
    
    def _insert_into_files_paths_table(self, cursor:sqlite3.Cursor, task_id:str, files_for_download:list):
        for tag in files_for_download:
            cursor.execute("""
                INSERT INTO files_paths (ID, file_path)
                VALUES (?, ?);
            """, (task_id, tag))

    def insert_task(self, 
        task_id:str, 
        host:str, 
        port:int, 
        username:str, 
        password:str, 
        files_paths:list, 
        selection_criteria:str="", 
        server_arguments:str="", 
        client_arguments:str="", 
        tags:list=None):
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

        :param server_arguments: command line arguments used when starting the task server (optional)  
        :type server_arguments: str

        :param client_arguments: command line arguments used when starting the task client (optional)  
        :type client_arguments: str

        :param username: username for downloading files for client tasks 
        :type username: str

        :param password: clear password used by the client to download task files
        :type password: str

        :param files_paths: list of files path that will be downloaded and used by client  
        :type files_paths: list        
        
        :param tags: A list of tags associated with the task (optional).
        :type tags: list[str]

        :raises: sqlite3.IntegrityError
        """
        if selection_criteria is None:
            selection_criteria = ''

        if server_arguments is None:
            server_arguments = ''

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        try:
            self._insert_into_tasks_table(
                cursor,
                task_id, 
                host, 
                port, 
                selection_criteria, 
                server_arguments, 
                client_arguments, 
                username, 
                password)
            
            self._insert_into_files_paths_table(cursor, task_id, files_paths)

            if tags:
                self._insert_into_tags_table(cursor, task_id, tags)

            connection.commit()

        except Exception as e:
            connection.close()
            raise e
        
        connection.close()
        
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
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE tasks
                SET running = TRUE, last_mod_date = ?
                WHERE ID = ?;
            """, (last_mod_date, task_id))

            connection.commit()
        
        except Exception as e:
            connection.close()
            raise e
        
        connection.close()

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
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                UPDATE tasks
                SET running = FALSE, last_mod_date = ?
                WHERE ID = ?;
            """, (last_mod_date, task_id))
    
            connection.commit()

        except Exception as e:
            connection.close()
            raise e

        connection.close()

    def _select_from_tasks_table(self, cursor:sqlite3.Cursor, task_id:str) -> list:
        cursor.execute("""
            SELECT 
                creation_date, 
                last_mod_date, 
                ID, 
                host, 
                port, 
                running, 
                selection_criteria,
                server_arguments, 
                client_arguments,
                username,
                password
            FROM tasks
            WHERE ID = ?;
        """, (task_id,))
        return cursor.fetchone()
    
    def _select_from_tags_table(self, cursor:sqlite3.Cursor, task_id:str) -> list:
        cursor.execute("""
            SELECT tag
            FROM tags
            WHERE ID = ?;
        """, (task_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def _select_from_files_paths_table(self, cursor:sqlite3.Cursor, task_id:str) -> list:
        cursor.execute("""
            SELECT file_path
            FROM files_paths
            WHERE ID = ?;
        """, (task_id,))
        return [row[0] for row in cursor.fetchall()]

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
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        try:
            task = self._select_from_tasks_table(cursor, task_id)
            if not task:
                raise TaskNotRegistered(task_id)
                
            files_paths = self._select_from_files_paths_table(cursor, task_id)
                
            tags = self._select_from_tags_table(cursor, task_id)
        
        except Exception as e:
            connection.close()
            raise e

        connection.close()

        return {
            "creation_date": task[0],
            "last_mod_date": task[1],
            "ID": task[2],
            "host": task[3],
            "port": task[4],
            "running": task[5],
            "selection_criteria": task[6],
            "server_arguments": task[7],
            "client_arguments": task[8],
            "username": task[9],
            "password": task[10],
            "tags": tags,
            "files_paths": files_paths
        }

    def get_task_selection_criteria_map(self)->dict:
        """
        Retrieve a dictionary mapping each task ID to its selection criteria.
        
        :return: A dictionary where keys are task IDs and values are selection criteria.
        :rtype: dict
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT ID, selection_criteria
                FROM tasks WHERE running == TRUE;
            """)
            rows = cursor.fetchall()

        except Exception as e:
            connection.close()
            raise e 

        connection.close()

        task_map = {row[0]: row[1] for row in rows}
        return task_map

    def update_task(self, 
        task_id:str, 
        host:str=None, 
        port:int=None, 
        running:bool=None, 
        selection_criteria:str=None, 
        server_arguments:str=None,
        client_arguments:str=None, 
        username:str=None, 
        password:str=None):
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

        :param server_arguments: new command line server_arguments used when starting the task (optional)  
        :type server_arguments: str

        :param username: username for downloading files for client tasks 
        :type username: str

        :param password: clear password used by the client to download task files
        :type password: str

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

        if server_arguments is not None:
            fields.append("server_arguments = ?")
            values.append(server_arguments)

        if client_arguments is not None:
            fields.append("client_arguments = ?")
            values.append(client_arguments)

        if username is not None:
            fields.append("username = ?")
            values.append(username)
        
        if password is not None:
            fields.append("password = ?")
            values.append(password)

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
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        try:
            cursor.execute(sql_query, values)
            connection.commit()
        except Exception as e:
            connection.close()
            raise e

        connection.close()
        print(f"Task {task_id} updated successfully.")

if __name__ == "__main__":
    db_interface = TasksDbInterface(str(Path().resolve()))
    db_interface.insert_task(
        task_id="1a2b", 
        host="192.168.1.1", 
        port=8080,
        username="user",
        password="123",
        files_paths=['./tasks/task_1a2b/client.py','./tasks/task_1a2b/task.py'],
        selection_criteria="(has camera) and (data >= 30)", 
        server_arguments=" arg1 arg2", 
        tags=['mnist','mlp'])
    db_interface.insert_task(task_id="2b3c", host="192.168.1.2", port=9090, username='user',
        password="123",
        files_paths=['./tasks/task_1a2b/client.py','./tasks/task_1a2b/task.py'],)
    db_interface.set_task_running("1a2b")
    task_map = db_interface.get_task_selection_criteria_map()
    pprint(task_map)
