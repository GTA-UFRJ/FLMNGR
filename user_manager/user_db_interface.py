import os
import sqlite3
from pathlib import Path
from datetime import datetime
from pprint import pprint

class UserNotRegistered(Exception):
    def __init__(self, task_id:str):
        super().__init__(f"User with ID={task_id} not registered")

class UserDbInterface:
    """
    User DB handler

    :param workpath: project location
    :type workpath: str
    """
    def __init__(self, work_path: str):
        self.db_path = os.path.join(work_path,"db/users.db")
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        connection = sqlite3.connect(self.db_path)
        
        cursor = connection.cursor()
        self._create_stats_table_if_not_exists(cursor)
        self._create_sensors_table_if_not_exists(cursor)
        
        connection.commit()
        connection.close()

    def _create_stats_table_if_not_exists(self, cursor:sqlite3.Cursor):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS stats (
            creation_date TEXT NOT NULL,
            last_mod_date TEXT NOT NULL,
            ID TEXT PRIMARY KEY,
            data_qnt INT NOT NULL,
            avg_acc_contrib FLOAT,
            avg_discon_per_round FLOAT
        );
        """
        cursor.execute(create_table_query)

    def _create_sensors_table_if_not_exists(self, cursor:sqlite3.Cursor):
        create_tags_table_query = """
        CREATE TABLE IF NOT EXISTS sensors (
            ID TEXT NOT NULL,
            sensor TEXT NOT NULL,
            FOREIGN KEY (ID) REFERENCES stats(ID)
        );
        """
        cursor.execute(create_tags_table_query)

    def _insert_into_stats_table(self,
        cursor:sqlite3.Cursor,
        user_id:str,
        data_qnt:int,
        avg_acc_contrib:float,
        avg_discon_per_round:float):

        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_mod_date = creation_date
        insert_stats_table_query = """
        INSERT INTO stats (
            creation_date, 
            last_mod_date, 
            ID, 
            data_qnt,
            avg_acc_contrib,
            avg_discon_per_round)
        VALUES (?, ?, ?, ?, ?, ?); 
        """
        cursor.execute(insert_stats_table_query,
            (creation_date, 
            last_mod_date, 
            user_id,
            data_qnt,
            avg_acc_contrib,
            avg_discon_per_round))

    def _insert_into_sensors_table(self, cursor:sqlite3.Cursor, user_id:str, sensors:list):
        for sensor in sensors:
            cursor.execute("""
                INSERT INTO sensors (ID, sensor)
                VALUES (?, ?);
            """, (user_id, sensor))

    def _delete_from_sensors_table(self, cursor:sqlite3.Cursor, user_id:str, sensors:list):
        for sensor in sensors:
            cursor.execute("""
                DELETE FROM sensors WHERE ID = ? AND sensor = ?;
            """, (user_id, sensor))

    def insert_user(self, 
        user_id:str,
        sensors:list,
        data_qnt:int=0,
        avg_acc_contrib:float=None,
        avg_discon_per_round:float=None):
        """
        Insert a new task into the stats table and optionally insert sensors
        
        :param user_id: Unique identifier for the user (nickname).
        :type user_id: str

        :param sensors: list of string with sensors names (strings). Can be empty
        :type sensors: list

        :param data_qnt: amount of data used for training (default is 0)
        :type data_qnt: int

        :param avg_acc_contrib: avarege of accuracy increment along tasks rounds (optional) 
        :type avg_acc_contrib: float 

        :param avg_discon_per_round: avarege number of disconnections along tasks rounds (optional) 
        :type avg_discon_per_round: float 
        
        :raises: sqlite3.IntegrityError
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        try:
            self._insert_into_stats_table(cursor, user_id, data_qnt, avg_acc_contrib, avg_discon_per_round)
            self._insert_into_sensors_table(cursor, user_id, sensors)
            connection.commit()
        except Exception as e:
            connection.close()
            raise e
        
        connection.close()
        
        print(f"User {user_id} inserted successfully.")

    def _select_from_stats_table(self, cursor:sqlite3.Cursor, user_id:str) -> list:
        cursor.execute("""
            SELECT 
                creation_date, 
                last_mod_date, 
                ID, 
                data_qnt,
                avg_acc_contrib,
                avg_discon_per_round
            FROM stats
            WHERE ID = ?;
        """, (user_id,))
        return cursor.fetchone()
    
    def _select_from_sensors_table(self, cursor:sqlite3.Cursor, user_id:str) -> list:
        cursor.execute("""
            SELECT sensor
            FROM sensors
            WHERE ID = ?;
        """, (user_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def query_user(self, user_id:str)->dict:
        """
        Query a user by its ID, including all associated attributes and sensors
        
        :param user_id: the ID of the user to query.
        :type user_id: str
        
        :return: a dictionary with user attributes and sensors list, or None if the user does not exists.
        :rtype: dict

        :raises: sqlite3.Error

        :raises: UserNotRegistered
        """    
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        try:
            stats = self._select_from_stats_table(cursor, user_id)
            if not stats:
                raise UserNotRegistered(user_id)
                
            sensors_list = self._select_from_sensors_table(cursor, user_id)
        
        except Exception as e:
            connection.close()
            raise e

        connection.close()

        return {
            "creation_date": stats[0],
            "last_mod_date": stats[1],
            "ID": stats[2],
            "data_qnt":stats[3],
            "avg_acc_contrib":stats[4],
            "avg_disconnection_per_round":stats[5],
            "sensors":sensors_list
        }
    
    def _build_sql_update_stats_query(
        self,
        user_id:str,
        data_qnt:int=None,
        avg_acc_contrib:float=None,
        avg_disconnection_per_round:float=None
        ):

        # Build the SQL update query dynamically based on non-None arguments
        fields = []
        values = []
        last_mod_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if data_qnt is not None:
            fields.append("data_qnt = ?")
            values.append(data_qnt)
        
        if avg_acc_contrib is not None:
            fields.append("avg_acc_contrib = ?")
            values.append(avg_acc_contrib)
        
        if avg_disconnection_per_round is not None:
            fields.append("avg_disconnection_per_round = ?")
            values.append(avg_disconnection_per_round)

        # Always update the last modification date
        fields.append("last_mod_date = ?")
        values.append(last_mod_date)
        
        # Add the ID for the WHERE clause
        values.append(user_id)
        
        sql_query = f"""
            UPDATE stats
            SET {', '.join(fields)}
            WHERE ID = ?;
        """

        return sql_query, values
    
    def _insert_new_sensors(self, cursor:sqlite3.Cursor, user_info:dict, new_sensors_list:list=None):
        sensors_to_insert = [sensor for sensor in new_sensors_list if sensor not in user_info["sensors"]]
        self._insert_into_sensors_table(cursor, user_info["ID"], sensors_to_insert)

    def _delete_old_sensors(self, cursor:sqlite3.Cursor, user_info:dict, new_sensors_list:list=None):
        sensors_to_delete = [sensor for sensor in user_info["sensors"] if sensor not in new_sensors_list]
        self._delete_from_sensors_table(cursor, user_info["ID"], sensors_to_delete)

    def update_user(self, 
        user_id:str, 
        data_qnt:int=None,
        avg_acc_contrib:float=None,
        avg_disconnection_per_round:float=None,
        received_sensors:list=None
        ):
        """
        Update an existing client with new attrbutes and sensors. Arguments with None are not updated.

        :param user_id: the ID of the user to update
        :type user_id: str

        :param data_qnt: amount of data used for training (default is 0)
        :type data_qnt: int

        :param avg_acc_contrib: avarege of accuracy increment along tasks rounds (optional) 
        :type avg_acc_contrib: float 

        :param avg_discon_per_round: avarege number of disconnections along tasks rounds (optional) 
        :type avg_discon_per_round: float 

        :param sensors: list of string with sensors names (strings). Can be empty
        :type sensors: list

        :raises: sqlite3.Error

        :raises: TaskNotRegistered
        """
        if not user_id:
            return
        
        user_info = self.query_user(user_id)
        if user_info is None:
            raise UserNotRegistered(user_id)
        
        update_stats_query, update_stats_values = self._build_sql_update_stats_query(
            user_id, 
            data_qnt,
            avg_acc_contrib, 
            avg_disconnection_per_round)
            
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        try:
            cursor.execute(update_stats_query, update_stats_values)
            if received_sensors is not None:
                self._insert_new_sensors(cursor, user_info, received_sensors)
                self._delete_old_sensors(cursor, user_info, received_sensors)    
            connection.commit()
        except Exception as e:
            connection.close()
            raise e

        connection.close()
        print(f"User {user_id} updated successfully.")

if __name__ == "__main__":
    if os.path.exists("db/users.db"):
        os.remove("db/users.db")
    db_interface = UserDbInterface(str(Path().resolve()))
    db_interface.insert_user(
        user_id="guilhermeeec",
        sensors=["intelbras_cam","rpi4","canedge"],
        data_qnt=0)
    db_interface.update_user(
        user_id="guilhermeeec",
        avg_acc_contrib=0.123,
        received_sensors=["rpi4","rpizero"]
    )
    user = db_interface.query_user("guilhermeeec")
    pprint(user)
