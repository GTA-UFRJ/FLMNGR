import json
import os
from microservice_interconnect.base_service import BaseService
from pathlib import Path

class SampleService(BaseService):
    def __init__(self, work_path:str):
        super().__init__()
        print(f"work path: {work_path}")

        self.add_api_endpoint(
            func_name="rpc_exec_a",
            schema=self.get_schema(os.path.join(work_path,"microservice_interconnect/rpc_exec_a.schema.json")),
            func=self.rpc_exec_a)
        
        self.add_api_endpoint(
            func_name="rpc_exec_a_bug",
            schema=self.get_schema(os.path.join(work_path,"microservice_interconnect/rpc_exec_a.schema.json")),
            func=self.rpc_exec_a_bug)
    
    def get_schema(self, schema_path:str):
        with open(schema_path, 'r') as f:
            return json.load(f)

    def rpc_exec_a(self, received:dict)->int:
        print(f"Received: {received}")
        return received["arg_1"] + 1
    
    def rpc_exec_a_bug(self, received:dict)->int:
        print(f"Received: {received}")
        raise Exception("This is an error message")

if __name__ == "__main__":
    print("Starting microservice")
    service = SampleService(str(Path().resolve()))
    service.start()
