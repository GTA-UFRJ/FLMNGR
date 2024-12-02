from stub_service_cloud_ml import StubServiceCloudML
from time import sleep
from pathlib import Path
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
print(f"Current dir: {dir_path}")

class TestStubCloudMLLogic:

    def __init__(self, base_path) -> None:
        db_path = os.path.join(base_path,"db/tasks.db")
        if os.path.exists(db_path):
            os.remove(db_path)

        self.service_cloud_ml = StubServiceCloudML(base_path)
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

    def start_non_registered_task(self):
        print(f"{self.index} Try to start a task that was not registered")
        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_start_server_task({"task_id":"4fe5"}))
        try:
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not registered"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def stop_non_registered_task(self):
        print(f"{self.index} Try to stop a task that was not registered")
        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"4fe5"}))
        try:
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not registered"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()
    
    def register_task(self):
        print(f"{self.index} Register a task")

        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_create_task(
            {"task_id":"4fe5",
             'host':'localhost',
             'port':8080,
             'selection_criteria':'(data_qnt > 50) and (has_camera == False)',
             'username':'user',
             'password':'123',
             'files_paths':['./task_4fe5/client.py','./task_4fe5/task.py']
             }))
        try:
            assert ret == {"status_code":200,"return":None}
        except:
            print(f"Test {self.index}, part (1/2), failed: ", ret)
            exit()

        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_create_task(
            {"task_id":"aaaa",
             'host':'localhost',
             'port':8080,
             'username':'user',
             'password':'123',
             'files_paths':['./task_4fe5/client.py']}))
        try:
            assert ret == {"status_code":200,"return":None}
        except:
            print(f"Test {self.index}, part (2/2), failed: ", ret)
            exit()
        self.index += 1

    def register_repeated_task(self):
        print(f"{self.index} Try to register a task with same ID")
        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_create_task(
            {"task_id":"4fe5",'host':'localhost','port':8080,'username':'user',
             'password':'123',
             'files_paths':['./task_4fe5/client.py']}))
        try:
            assert ret == {"status_code":500,"exception":"UNIQUE constraint failed: tasks.ID"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def register_invalid_task(self):
        print(f"{self.index} Try to register task with invalid field")
        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_create_task(
            {"task_id":"bbbb",'host':'localhost','port':'error','username':'user',
             'password':'123',
             'files_paths':['./task_4fe5/client.py']}))
        try:
            assert ret == {"status_code":500,"exception":"CHECK constraint failed: port >= 0 AND port <= 65535"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def start_task_with_invalid_files_at_dik(self):
        print(f"{self.index} Try to start a task without proper files")

        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_start_server_task({"task_id":"aaaa"}))
        try:
            assert ret == {"status_code":500,"exception":f"Directory '{dir_path}/tasks/task_aaaa' does not exist."} 
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def start_task_correctly(self):
        print(f"{self.index} Start task correctly")
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_start_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":200, "return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def stop_task_correctly(self):
        print(f"{self.index} Stop task correctly")
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":200, "return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def start_bugged_task(self):
        print(f"{self.index} Start task with a bug")
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_start_server_task(
                {"task_id":"4fe5",
                 "arguments":"test-error"}))
        try: 
            assert ret == {"status_code":200, "return":None}
        except:
            print(f"Test {self.index}, part (1/2), failed: ", ret)
            exit()

        sleep(6)
        print("I will try to kill the task which should be alredy stopped")

        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"4fe5"}))
        try:
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not found"}
        except:
            print(f"Test {self.index}, part (2/2), failed: ", ret)
            exit()
        self.index += 1

    def stop_task_alredy_finished(self):
        print(f"{self.index} Stop task alredy finished")
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not found"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def restart_task_correctly(self):
        print(f"{self.index} Restart task using start function")
        
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_start_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {'status_code': 200, 'return': None}
        except:
            print(f"Test {self.index}, part (1/2), failed: ", ret)
            exit()
        
        sleep(4)

        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_stop_server_task({"task_id":"4fe5"}))
        try: 
            assert ret == {"status_code":200, "return":None}
        except:
            print(f"Test {self.index}, part (2/2), failed: ", ret)
            exit()
        self.index += 1

    def client_requesting_task(self):
        print(f"{self.index} Client requesting task")

        print("I will force 'running' field for task 4fe5 to running")
        self.service_cloud_ml.db_handler.set_task_running("4fe5")
        
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_client_requesting_task({"client_id":"xxxx"}))
        try: 
            assert ret == {'status_code': 200, 'return': 
                           [{'ID': '4fe5', 
                             'host': 'localhost', 
                             'port': 8080, 
                             'tags': [], 
                             'client_arguments': None, 
                             'username': 'user', 
                             'password': '123', 
                             'files_paths': ['./task_4fe5/client.py', './task_4fe5/task.py']}]}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()
        
        print("I will force 'running' field for task 4fe5 to not running")
        self.service_cloud_ml.db_handler.set_task_not_running("4fe5")

    def update_task(self):
        print(f"{self.index} Update task selection criteria")

        ret = self.call_function(lambda: self.service_cloud_ml.rpc_exec_update_task(
            {"task_id":"4fe5", "selection_criteria":"aaaaa"}))
        try:
            assert ret == {"status_code":200,"return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def invalid_selection_crit(self):
        print(f"{self.index} Request tasks, but they have an invalid selection criteria")
        
        ret = self.call_function(
            lambda: self.service_cloud_ml.rpc_exec_client_requesting_task({"client_id":"xxxx"}))
        try: 
            assert ret == {'status_code': 200, 'return': []}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def perform_tests(self):
        self.start_non_registered_task()
        sleep(1)
        self.stop_non_registered_task()
        sleep(1)
        self.register_task()
        sleep(1)
        self.register_repeated_task()
        sleep(1)
        self.register_invalid_task()
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
        self.client_requesting_task()
        sleep(1)
        self.update_task()
        sleep(1)
        self.invalid_selection_crit()
        sleep(1)
    
    def finish_tests(self):
        self.service_cloud_ml.cloud_ml_backend.finish_all()
        
if __name__ == "__main__":
    tester = TestStubCloudMLLogic(str(Path().resolve()))
    tester.perform_tests()