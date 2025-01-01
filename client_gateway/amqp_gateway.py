from microservice_interconnect.base_service import BaseService
from microservice_interconnect.rpc_client import register_event
import json
import os
import requests
import configparser
from pathlib import Path

class CloudOperationFailed(Exception):
    def __init__(self, url:str):
        super().__init__(f"Could not receive a valid response from {url} endpoint")

class ServiceAmqpGateway(BaseService):
    """
    Redirect AMQP messages from client broker to HTTP cloud gateway
    """
    def __init__(
            self,
            workpath: str,  
            client_broker_host="localhost", 
            client_broker_port=5672,
            cloud_gateway_host="localhost", 
            cloud_gateway_port=5672) -> None:
        super().__init__(broker_host=client_broker_host, broker_port=client_broker_port)

        self.broker_host = client_broker_host
        self.broker_port = client_broker_port

        self.workpath = workpath
        self.server_url = f"http://{cloud_gateway_host}:{cloud_gateway_port}"

        self.add_api_endpoint(
            func=self.rpc_redirect_update_user_info,
            func_name="rpc_exec_update_user_info",
            schema=self._get_schema("rpc_exec_update_user_info")
        )

        self.add_api_endpoint(
            func=self.rpc_redirect_client_requesting_task,
            func_name="rpc_exec_client_requesting_task",
            schema=self._get_schema("rpc_exec_client_requesting_task")
        )

        register_event("client_gateway","main","Started",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

    def _get_schema(self, func_name: str) -> dict:
        """
        Read JSON schema from file

        :param func_name: JSON message name
        :type func_name: str

        :return: JSON
        :rtype: dict

        :raises: OSError

        :raises: json.JSONDecodeErrorpc_exec_update_user_infor
        """
        with open(os.path.join(self.workpath, "schemas", f"{func_name}.json")) as f:
            return json.load(f)

    def _redirect_json_to_url(self, url:str, data:dict) -> dict:
        """
        Send JSON data to URL using HTTP and returns JSON response  
        """
        response = requests.post(url=url, json=data)
        if response.status_code == 200:
            return response.json()
        elif response.status_code in [400,500]:
            response_json = response.json()
            response_json["exception"] = response_json.pop("return")
            return response_json
        else:
            raise CloudOperationFailed(url)

    def rpc_redirect_update_user_info(self, received:dict):
        register_event("client_gateway","rpc_redirect_update_user_info","Started redirecting update user info msg",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        url=f"{self.server_url}/rpc_exec_update_user_info"

        # Do not validate server response!
        response_from_cloud_gateway = self._redirect_json_to_url(url, data=received)
        
        register_event("client_gateway","rpc_redirect_update_user_info","Finished redirecting update user info msg",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
        return response_from_cloud_gateway

    def rpc_redirect_client_requesting_task(self, received:dict):
        register_event("client_gateway","rpc_redirect_client_requesting_task","Started redirecting task request msg",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)

        url=f"{self.server_url}/rpc_exec_client_requesting_task"

        # Do not validate server response!
        response_from_cloud_gateway = self._redirect_json_to_url(url, data=received)
    
        register_event("client_gateway","rpc_redirect_client_requesting_task","Finished redirecting task request msg",allow_registering=allow_register,host=self.broker_host,port=self.broker_port)
        return response_from_cloud_gateway
    
    
if __name__ == "__main__":

    configs = configparser.ConfigParser()
    configs.read("./config.ini")
    allow_register = configs.getboolean("events","register_events")

    service = ServiceAmqpGateway(
        workpath=os.path.join(Path().resolve(), "client_gateway"),
        client_broker_host=configs["client.broker"]["host"],
        client_broker_port=configs["client.broker"]["port"],
        cloud_gateway_host=configs["server.broker"]["host"],
        cloud_gateway_port=configs["server.gateway"]["port"],
    )

    try:
        service.start()
    except KeyboardInterrupt as e:
        service.stop()