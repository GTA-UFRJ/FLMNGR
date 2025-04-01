from user_manager.user_db_interface import UserDbInterface, UserNotRegistered
from microservice_interconnect.base_service import BaseService
from microservice_interconnect.rpc_client import register_event
from pathlib import Path
import os
import json
import configparser

class ServiceUserManager(BaseService):
    """
    Main class for User Manager microservice that executes the methods for CRUD operations on users DB

    :param workpath: project location, within which "tasks" dir resides
    :type workpath: str

    :param server_broker_host: hostname or IP of broker
    :type server_broker_host: str

    :param server_broker_port: broker port
    :type server_broker_port: int
    """
    def __init__(
            self, 
            workpath:str, 
            server_broker_host:str="localhost",
            server_broker_port:int=5672) -> None:
        super().__init__(broker_host=server_broker_host, broker_port=server_broker_port)
        self.workpath = workpath
        self.db_handler = UserDbInterface(workpath)

        self.broker_host = server_broker_host
        self.broker_port = server_broker_port

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

        register_event("service_user_manager","main","Started",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def _get_schema(self, func_name:str)->dict:
        """
        Read JSON schema from file

        :param func_name: JSON message name
        :type func_name: str

        :raises OSError: if schema file was not found

        :raises json.JSONDecodeError: invalid JSON file format 

        :return: JSON
        :rtype: dict
        """
        with open(os.path.join(self.workpath,"schemas",f"{func_name}.json")) as f:
            return json.load(f)

    def rpc_exec_update_user_info(self, received:dict):
        """
        Receives a validated JSON message for inserting or updating a user in database
        
        :param received: JSON containing user ID, user attributes and sensors
        :type received: dict

        :raises sqlite3.IntegrityError: could not perform DB statement

        :raises user_db_interface.UserNotRegistered: user not found
        """
        register_event("service_user_manager","rpc_exec_update_user_info","Started updating user info",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        self.db_handler.update_user(
            user_id=received["user_id"],
            data_qnt=received.get("data_qnt"),
            avg_acc_contrib=received.get("avg_acc_contrib"),
            avg_disconnection_per_round=received.get("avg_disconnection_per_round"),
            received_sensors=received.get("sensors"),
            insert_if_dont_exist=True
        )

        register_event("service_user_manager","rpc_exec_update_user_info","Finished updating user info",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def rpc_exec_get_user_info(self, received:dict):
        """
        Receives a validated JSON message for querying for a user in database
        
        :param received: JSON containing user ID
        :type received: dict

        :raises sqlite3.IntegrityError: could not perform DB statement

        :raises user_db_interface.UserNotRegistered: user not found

        :return: user attributes and sensors list
        :rtype: dict
        """
        register_event("service_user_manager","rpc_exec_get_user_info","Started getting user info",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
        user_info = self.db_handler.query_user(received["user_id"])
        register_event("service_user_manager","rpc_exec_get_user_info","Finished getting user info",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
        return user_info

if __name__ == "__main__":

    configs = configparser.ConfigParser()
    configs.read("config.ini")
    allow_register = configs.getboolean("events","register_events")

    service = ServiceUserManager(
        os.path.join(Path().resolve(),"user_manager"),
        server_broker_host=configs["server.broker"]["host"],
        server_broker_port=configs["server.broker"]["port"],
    )
    try:
        service.start()
    except KeyboardInterrupt as e:
        service.stop()