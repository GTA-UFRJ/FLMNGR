from stub_service_client_ml import StubServiceClientML
from time import sleep
from pathlib import Path
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
print(f"Current dir: {dir_path}")

class TestClientMLLogic:

    def __init__(self, base_path) -> None:
        info_path = os.path.join(base_path,"client_info/clinet_info.pkl")
        if os.path.exists(info_path):
            os.remove(info_path)

        self.service_client_ml = StubServiceClientML(
            base_path,
            {
                "ID":"guilhermeeec",
                "data_qnt":0,
                "avg_acc_contrib":None,
                "avg_disconnection_per_round":None,
                "has_camera":False,
                "has_gw_ecu":True
            })
        self.index = 1

    # Must be part of BaseService
    def get_success_message(self, returned_data=None):
        return {"status_code":200,"return":returned_data}
    
    # Must be part of BaseService
    def get_fail_message(self, returned_exception:Exception=None):
        if not returned_exception:
            return {"status_code":500}
        return {"status_code":500,"exception":str(returned_exception)}

    # Must be part of BaseService
    def call_function(self, func):
        try:
            ret = func()
            return self.get_success_message(ret)
        except Exception as e:
            return self.get_fail_message(e) 
        
    def force_store_client_info(self, client_info:dict):
        self.service_client_ml.client_info_handler.save_complete_info(client_info)
        
    def force_update_client_info(self, client_info:dict):
        self.service_client_ml.client_info_handler.update_info(client_info)
        
    def send_client_info(self):
        print(f"{self.index} Update client info locally")

        print("But, before, I will force creating a fake client info")
        self.force_store_client_info({
            "ID":"guilhermeeec",
            "data_qnt":323,
            "avg_acc_contrib":0.12,
            "avg_disconnection_per_round":0.44,
            "has_camera":False,
            "has_gw_ecu":True
        })

        ret = self.call_function(lambda: self.service_client_ml.rpc_call_send_client_stats())
        try:
            assert ret == {"status_code":200,"return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def update_client_info(self):
        print(f"{self.index} Update client info locally")

        print("But, before, I will force updating a fake client info")
        self.force_update_client_info({
            "ID":"guilhermeeec",
            "data_qnt":327
        })

        ret = self.call_function(lambda: self.service_client_ml.rpc_call_send_client_stats())
        try:
            assert ret == {"status_code":200,"return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def request_task(self):
        print(f"{self.index} Request task")

        ret = self.call_function(lambda: self.service_client_ml.rpc_call_request_task())
        try:
            assert ret == {"status_code":200,"return":[{'ID': '4fe5', 'host': 'localhost', 'port': 8080, 'tags': []}]}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()
    
    def start_task_with_invalid_files_at_dik(self):
        print(f"{self.index} Try to start a task without proper files")

        ret = self.call_function(
            lambda: self.service_client_ml.rpc_exec_start_client_task({"task_id":"aaaa"}))
        try:
            assert ret == {"status_code":500,"exception":f"Directory '{dir_path}/tasks/task_aaaa' does not exist."} 
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def request_task(self):
        print(f"{self.index} Request task")

        ret = self.call_function(lambda: self.service_client_ml.rpc_call_request_task())
        try:
            assert ret == {"status_code":200,"return":[{'ID': '4fe5', 'host': 'localhost', 'port': 8080, 'tags': []}]}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()
    
    def start_task_correctly(self):
        print(f"{self.index} Start task correctly")
        ret = self.call_function(
            lambda: self.service_client_ml.rpc_exec_start_client_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":200, "return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def stop_task_correctly(self):
        print(f"{self.index} Stop task correctly")
        ret = self.call_function(
            lambda: self.service_client_ml.rpc_exec_stop_client_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":200, "return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def start_bugged_task(self):
        print(f"{self.index} Start task with a bug")
        ret = self.call_function(
            lambda: self.service_client_ml.rpc_exec_start_client_task(
                {"task_id":"4fe5",
                 "arguments":"test-error"}))
        try: 
            assert ret == {"status_code":200, "return":None}
        except:
            print(f"Test {self.index}, part (1/2), failed: ", ret)
            exit()

        sleep(6)
        print("I will try to kill the task which should be alredy stopped")

        ret = self.call_function(lambda: self.service_client_ml.rpc_exec_stop_client_task({"task_id":"4fe5"}))
        try:
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not found"}
        except:
            print(f"Test {self.index}, part (2/2), failed: ", ret)
            exit()
        self.index += 1

    def stop_task_alredy_finished(self):
        print(f"{self.index} Stop task alredy finished")
        ret = self.call_function(
            lambda: self.service_client_ml.rpc_exec_stop_client_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not found"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def perform_tests(self):
        self.send_client_info()
        sleep(1)
        self.update_client_info()
        sleep(1)
        self.start_task_with_invalid_files_at_dik()
        sleep(1)
        self.request_task()
        sleep(1)
        self.start_task_correctly()
        sleep(6)
        self.stop_task_correctly()
        sleep(4)
        self.start_bugged_task()
        sleep(4)
        self.stop_task_alredy_finished()
        sleep(1)
        
    def finish_tests(self):
        self.service_client_ml.client_ml_backend.finish_all()
        
if __name__ == "__main__":
    tester = TestClientMLLogic(str(Path().resolve()))
    tester.perform_tests()