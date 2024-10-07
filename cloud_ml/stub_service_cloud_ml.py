from cloud_ml.cloud_ml import CloudML
from cloud_ml.stub_process_messages_from_task import StubForwardMessagesFromTask

# The definitive ServiceCloudMl use cloud_ml, but will interact with RabbitMQ
class StubServiceCloudML:

    def __init__(
        self,
        workpath:str) -> None:
        
        self.cloud_ml_backend = CloudML(workpath)

    def finish_cloud_ml(self):
        self.cloud_ml_backend.finish_all()

    def handle_error_from_task(self, task_id:str):
        self.cloud_ml_backend.stop_task(task_id)

    def rpc_exec_start_server_task(self, received:dict):
        forwarder = StubForwardMessagesFromTask(
            received['task_id'],
            self.handle_error_from_task)
        callback = forwarder.process_messages

        self.cloud_ml_backend.start_new_task(
            received['task_id'],
            callback,
            received.get('arguments')
        )

    def rpc_exec_stop_server_task(self, received:dict):
        self.cloud_ml_backend.stop_task(received['task_id'])