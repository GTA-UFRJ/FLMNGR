from stub_service_cloud_ml import StubServiceCloudML
from time import sleep
from pathlib import Path
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
print(f"Current dir: {dir_path}")

class TestCloudMLLogic:

    def __init__(self, base_path) -> None:
        self.service_cloud_ml = StubServiceCloudML(base_path)

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

    def stop_non_existing_task(self):
        print("(1) Try to stop a task that do not exist")
        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"aaaa"}))
        try:
            assert ret == {"status_code":500,"exception":"Task with ID=aaaa not found"}
        except:
            print("Test (1) failed: ", ret)
            exit()

    def start_task_with_invalid_files_at_dik(self):
        print("(2) Try to start a task without proper files")
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_start_server_task({"task_id":"aaaa"}))
        try:
            assert ret == {"status_code":500,"exception":f"Directory '{dir_path}/tasks/task_aaaa' does not exist."} 
        except:
            print("Test (2) failed: ", ret)
            exit()

    def start_task_correctly(self):
        print("(3) Start task correctly")
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_start_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":200, "return":None}
        except:
            print("Test (3) failed: ", ret)
            exit()

    def stop_task_correctly(self):
        print("(4) Stop task correctly")
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":200, "return":None}
        except:
            print("Test (4) failed: ", ret)
            exit()

    def start_bugged_task(self):
        print("(5) Start task with a bug")
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_start_server_task(
                {"task_id":"4fe5",
                 "arguments":"test-error"}))
        try: 
            assert ret == {"status_code":200, "return":None}
        except:
            print("Test (5.1) failed: ", ret)
            exit()

        sleep(6)
        print("I will try to kill the task which should be alredy stopped")

        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"4fe5"}))
        try:
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not found"}
        except:
            print("Test (5.2) failed: ", ret)
            exit()


    def stop_task_alredy_finished(self):
        print("(6) Stop task alredy finished")
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not found"}
        except:
            print("Test (6) failed: ", ret)
            exit()

    def restart_task_correctly(self):
        print("(7) Restart task using start function")
        
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_start_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {'status_code': 200, 'return': None}
        except:
            print("Test (7) failed: ", ret)
            exit()
        
        sleep(4)
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":200, "return":None}
        except:
            print("Test (7) failed: ", ret)
            exit()

    def perform_tests(self):
        self.stop_non_existing_task()
        sleep(1)
        self.start_task_with_invalid_files_at_dik()
        sleep(1)
        self.start_task_correctly()
        sleep(6)
        self.stop_task_correctly()
        sleep(4)
        self.start_bugged_task()
        sleep(4)
        self.stop_task_alredy_finished()
        sleep(1)
        self.restart_task_correctly()
        sleep(1)
    
    def finish_tests(self):
        self.service_cloud_ml.finish_cloud_ml()
        
if __name__ == "__main__":
    tester = TestCloudMLLogic(str(Path().resolve()))
    try:
        tester.perform_tests()
    except:
        tester.finish_tests()