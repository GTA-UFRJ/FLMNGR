from microservice_interconnect.rpc_client import rpc_send
from time import sleep
from pathlib import Path
import os 
import configparser
dir_path = os.path.dirname(os.path.realpath(__file__))
print(f"Current dir: {dir_path}")

class TestCloudMLLogic:

    def __init__(self, base_path) -> None:
        db_path = os.path.join(base_path,"db/tasks.db")
        if os.path.exists(db_path):
            os.remove(db_path)

        configs = configparser.ConfigParser()
        configs.read("./config.ini")
        self.host = configs["server.broker"]["host"]
        self.port = configs["server.broker"]["port"]

        print("In other terminal, run: ")
        print("python -m cloud_task_manager.service_cloud_ml")
        input("When ready, press enter...")
        print("------------------------------")
        self.index = 1

    def start_non_registered_task(self):
        print(f"{self.index} Try to start a task that was not registered")
        ret = rpc_send("rpc_exec_start_server_task",{"task_id":"4fe5"},
                       host=self.host, port=self.port)
        try:
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not registered"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def stop_non_registered_task(self):
        print(f"{self.index} Try to stop a task that was not registered")
        ret = rpc_send("rpc_exec_stop_server_task",{"task_id":"4fe5"})
        try:
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not registered"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()
    
    def register_task(self):
        print(f"{self.index} Register a task")
        ret = rpc_send("rpc_exec_create_task",
            {"task_id":"4fe5",
             'host':'localhost',
             'port':8080,
             'selection_criteria':'(data_qnt > 50) and ("camera" in sensors)',
             'username':'user',
             'password':'123',
             'files_paths':['./task_4fe5/client.py','./task_4fe5/task.py']
             })
        try:
            assert ret == {"status_code":200,"return":None}
        except:
            print(f"Test {self.index}, part (1/2), failed: ", ret)
            exit()

        ret = rpc_send("rpc_exec_create_task",
            {"task_id":"aaaa",
             'host':'localhost',
             'port':8080,
             'username':'user',
             'password':'123',
             'files_paths':['./task_4fe5/client.py']
             })
        try:
            assert ret == {"status_code":200,"return":None}
        except:
            print(f"Test {self.index}, part (2/2), failed: ", ret)
            exit()
        self.index += 1

    def register_repeated_task(self):
        print(f"{self.index} Try to register a task with same ID")
        ret = rpc_send("rpc_exec_create_task",
            {"task_id":"4fe5",'host':'localhost','port':8080,'username':'user',
             'password':'123',
             'files_paths':['./task_4fe5/client.py']})
        try:
            assert ret == {"status_code":500,"exception":"UNIQUE constraint failed: tasks.ID"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def register_invalid_task(self):
        print(f"{self.index} Try to register task with invalid field")
        ret = rpc_send("rpc_exec_create_task",
            {"task_id":"bbbb",'host':'localhost','port':'error','username':'user',
             'password':'123',
             'files_paths':['./task_4fe5/client.py']})
        try:
            assert ret == {'status_code': 400, 
                           'exception': "rpc_exec_create_task cannot be executed due to invalid arguments: 'error' is not of type 'integer'\n\nFailed validating 'type' in schema['properties']['port']:\n    {'type': 'integer'}\n\nOn instance['port']:\n    'error'"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def start_task_with_invalid_files_at_dik(self):
        print(f"{self.index} Try to start a task without proper files")
        ret = rpc_send("rpc_exec_start_server_task",{"task_id":"aaaa"})
        try:
            assert ret == {"status_code":500,"exception":f"Directory '{dir_path}/tasks/task_aaaa' does not exist."} 
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def start_task_correctly(self):
        print(f"{self.index} Start task correctly")
        ret = rpc_send("rpc_exec_start_server_task",{"task_id":"4fe5"})
        try: 
            assert ret == {"status_code":200, "return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def stop_task_correctly(self):
        print(f"{self.index} Stop task correctly")
        ret = rpc_send("rpc_exec_stop_server_task",{"task_id":"4fe5"})
        try: 
            assert ret == {"status_code":200, "return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def start_bugged_task(self):
        print(f"{self.index} Start task with a bug")
        ret = rpc_send("rpc_exec_start_server_task",
                {"task_id":"4fe5",
                 "arguments":"test-error"})
        try: 
            assert ret == {"status_code":200, "return":None}
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()
        self.index += 1

    def stop_task_alredy_finished(self):
        print(f"{self.index} Stop task alredy finished")
        ret = rpc_send("rpc_exec_stop_server_task",{"task_id":"4fe5"})
        try: 
            assert ret == {"status_code":500,"exception":"Task with ID=4fe5 not found"}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def restart_task_correctly(self):
        print(f"{self.index} Restart task using start function")
        ret = rpc_send("rpc_exec_start_server_task",{"task_id":"4fe5"})
        try: 
            assert ret == {'status_code': 200, 'return': None}
        except:
            print(f"Test {self.index}, part (1/2), failed: ", ret)
            exit()
        
        sleep(4)

        ret = rpc_send("rpc_exec_stop_server_task",{"task_id":"4fe5"})
        try: 
            assert ret == {"status_code":200, "return":None}
        except:
            print(f"Test {self.index}, part (2/2), failed: ", ret)
            exit()
        self.index += 1

    def client_requesting_task(self):
        print(f"{self.index} Client requesting task")

        print("Test will run task 4fe5")
        ret = rpc_send("rpc_exec_start_server_task",{"task_id":"4fe5"})
        try: 
            assert ret == {'status_code': 200, 'return': None}
        except:
            print(f"Test {self.index}, part (1/3), failed: ", ret)
            exit()
        
        ret = rpc_send("rpc_exec_client_requesting_task",{"user_id":"xxxx"})
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
            print(f"Test {self.index}, part (2/3), failed: ", ret)
            exit()
        
        
        print("Test will stop task 4fe5")
        ret = rpc_send("rpc_exec_stop_server_task",{"task_id":"4fe5"})
        try: 
            assert ret == {'status_code': 200, 'return': None}
        except:
            print(f"Test {self.index}, part (3/3), failed: ", ret)
            exit()

    def update_task(self):
        print(f"{self.index} Update task selection criteria")
        ret = rpc_send("rpc_exec_update_task",{"task_id":"4fe5", "selection_criteria":"aaaaa"})
        try:
            assert ret == {"status_code":200,"return":None}
            self.index += 1
        except:
            print(f"Test {self.index} failed: ", ret)
            exit()

    def invalid_selection_crit(self):
        print(f"{self.index} Request tasks, but it has an invalid selection criteria")
        
        ret = rpc_send("rpc_exec_client_requesting_task",{"user_id":"xxxx"})
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
        
if __name__ == "__main__":
    tester = TestCloudMLLogic(str(Path().resolve()))
    tester.perform_tests()