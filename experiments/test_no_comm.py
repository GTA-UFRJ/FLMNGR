from pathlib import Path
import os 
from time import time
import subprocess
import sys

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '../cloud_task_manager'))
sys.path.append(os.path.join(here, '../client_task_manager'))

from stub_service_cloud_ml import StubServiceCloudML
from stub_service_client_ml import StubServiceClientML

class NoCommunication:

    def __init__(self):
        self._prepare()
        self._run()
        self._finish()
    
    def _delete_data_files(self):
        db_path = os.path.join(self.cloud_task_manager_path,"db/tasks.db")
        if os.path.exists(db_path):
            os.remove(db_path)

        info_path = os.path.join(self.client_task_manager_path,"client_info/guilhermeeec_info.json")
        if os.path.exists(info_path):
            os.remove(info_path)

        info_path = os.path.join(self.client_task_manager_path,"tasks/task_4fe5/client.py")
        if os.path.exists(info_path):
            os.remove(info_path)

        info_path = os.path.join(self.client_task_manager_path,"tasks/task_4fe5/task.py")
        if os.path.exists(info_path):
            os.remove(info_path)

    def _prepare(self):
        this_path = str(Path().resolve())
        self.cloud_task_manager_path = os.path.join(this_path,"../cloud_task_manager")
        self.client_task_manager_path = os.path.join(this_path,"../client_task_manager")
        self._delete_data_files()
        
        self.cloud_task_manager = StubServiceCloudML(self.cloud_task_manager_path)
        self.client_1_task_manager = StubServiceClientML(
            workpath=self.client_task_manager_path,
            client_info={
                "ID":"guilhermeeec",
                "data_qnt":323,
                "avg_acc_contrib":0.12,
                "avg_disconnection_per_round":0.44,
                "has_camera":False,
                "has_gw_ecu":True 
            },
            autorun=False
        )
        self.client_2_task_manager = StubServiceClientML(
            workpath=self.client_task_manager_path,
            client_info={
                "ID":"gta",
                "data_qnt":400,
                "avg_acc_contrib":0.1,
                "avg_disconnection_per_round":0.2,
                "has_camera":False,
                "has_gw_ecu":True 
            },
            autorun=False
        )

        self.task_downlaod_server = subprocess.Popen(
            ["python3",
             os.path.join(self.cloud_task_manager_path,"host_tasks.py"),
             self.cloud_task_manager_path])

    def _server_create_and_start_task(self):

        start = time()
        self.cloud_task_manager.rpc_exec_create_task(
            {"task_id":"4fe5",
             'host':'localhost',
             'port':8080,
             'selection_criteria':'(data_qnt > 50) and (has_camera == False)',
             'username':'user',
             'password':'123',
             'files_paths':['client.py','task.py']
             })
        print(f"[TIME] to cloud_task_manager.rpc_exec_create_task = {time()-start}")

        start = time()
        self.cloud_task_manager.rpc_exec_start_server_task(
            {"task_id":"4fe5"}
        )
        print(f"[TIME] to cloud_task_manager.rpc_exec_start_server_task = {time()-start}")

    def _clients_send_info_and_server_update(self):
        start = time()
        self.client_1_task_manager.rpc_call_send_client_stats()
        print("Not implemented: pdate client in the server database")
        print(f"[TIME] to client_1_task_manager.rpc_call_send_client_stats and (not implemented) = {time()-start}")

        #self.client_2_task_manager.rpc_call_send_client_stats()

    def _clients_request_task_and_server_responded(self):
        start = time()
        self.client_1_task_manager.rpc_call_request_task()
        response_1 = self.cloud_task_manager.rpc_exec_client_requesting_task({"client_id":"gta"})
        print(response_1)
        print(f"[TIME] to client_1_task_manager.rpc_call_request_task and cloud_task_manager.rpc_exec_client_requesting_task = {time()-start}")

        self.client_2_task_manager.rpc_call_request_task()
        response_2 = self.cloud_task_manager.rpc_exec_client_requesting_task({"client_id":"gta"})

        return response_1, response_2

    def _clients_choose_download_and_start_task(self, response_1, response_2):
        # Call self.client_{1,2}_task_manager.run_task_one_policy(response)
        start = time()
        self.client_1_task_manager.run_task_one_policy(response_1)
        print(f"[TIME] to client_1_task_manager.download_task_training_files, cloud_task_manager.download_file, and client_1_task_manager.start_client_task = {time()-start}")
        
        self.client_2_task_manager.run_task_one_policy(response_2)

    def _run(self):
        print("========== Start experiment 0 ==========")
        
        self._server_create_and_start_task()
        input("---Press enter---")

        self._clients_send_info_and_server_update()
        input("---Press enter---")

        response_1, response_2 = self._clients_request_task_and_server_responded()
        input("---Press enter---")

        self._clients_choose_download_and_start_task(response_1, response_2)
        input("---Press enter---")

        print("=========== End experiment 0 ===========")

    def _finish(self):
        self.task_downlaod_server.kill()
        self._delete_data_files()

if __name__ == "__main__":
    exp = NoCommunication()