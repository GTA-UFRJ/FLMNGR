from user_manager.user_db_interface import UserDbInterface, UserNotRegistered
from microservice_interconnect.base_service import BaseService
from pathlib import Path
import os
import json
import configparser

class ServiceUserManager(BaseService):
    """
    Main class for User Manager microservice that executes the methods for CRUD operations on users DB

    :param workpath: project location, within which "tasks" dir resides
    :type workpath: str
    """
    def __init__(
            self, 
            workpath:str, 
            client_broker_host="localhost",
            client_broker_port=5672) -> None:
        super().__init__(broker_host=client_broker_host, broker_port=client_broker_port)
        self.workpath = workpath
        self.db_handler = UserDbInterface(workpath)

        self.add_api_endpoint(
            func=self.rpc_exec_update_user_info,
            func_name="rpc_exec_update_user_info",
            schema=self._get_schema("rpc_exec_update_user_info")
        )

        self.add_api_endpoint(
            func=self.rpc_exec_get_user_info,
            func_name="rpc_exec_get_user_info",
            schema=self._get_schema("rpc_exec_get_user_info")
        )

    def _get_schema(self, func_name:str)->dict:
        """
        Read JSON schema from file

        :param func_name: JSON message name
        :type func_name: str

        :return: JSON
        :rtype: dict

        :raises: OSError

        :raises: json.JSONDecodeError
        """
        with open(os.path.join(self.workpath,"schemas",f"{func_name}.json")) as f:
            return json.load(f)

    def rpc_exec_update_user_info(self, received:dict):
        """
        Receives a validated JSON message for inserting or updating a user in database
        
        :param received: JSON containing user ID, user attributes and sensors
        :type received: dict

        :raises: sqlite3.IntegrityError
        """
        self.db_handler.update_user(
            user_id=received["user_id"],
            data_qnt=received.get("data_qnt"),
            avg_acc_contrib=received.get("avg_acc_contrib"),
            avg_disconnection_per_round=received.get("avg_disconnection_per_round"),
            received_sensors=received.get("sensors"),
            insert_if_dont_exist=True
        )

    def rpc_exec_get_user_info(self, received:dict):
        """
        Receives a validated JSON message for querying for a user in database
        
        :param received: JSON containing user ID
        :type received: dict

        :return: user attributes and sensors list
        :rtype: dict

        :raises: sqlite3.IntegrityError
        """
        return self.db_handler.query_user(received["user_id"])

if __name__ == "__main__":

    configs = configparser.ConfigParser()
    configs.read("config.ini")

    service = ServiceUserManager(
        os.path.join(Path().resolve(),"user_manager"),
        client_broker_host=configs["server.broker"]["host"],
        client_broker_port=configs["server.broker"]["port"],
    )
    try:
        service.start()
    except KeyboardInterrupt as e:
        service.stop()