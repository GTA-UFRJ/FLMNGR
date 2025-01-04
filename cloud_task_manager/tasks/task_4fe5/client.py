import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
if sys.argv[1] != "cli":
    sys.path.append(sys.argv[1])

from flwr.client import NumPyClient, start_client
from task import DEVICE, Net, get_weights, load_data, set_weights, test, train
from task_daemon_lib.task_reporter import TaskReporter
from microservice_interconnect.rpc_client import register_event
import configparser

# Define FlowerClient and client_fn
class FlowerClient(NumPyClient):
    def fit(self, parameters, config):
        set_weights(net, parameters)
        print("start training")
        results = train(net, trainloader, testloader, epochs=1, device=DEVICE)
        return get_weights(net), len(trainloader.dataset), results

    def evaluate(self, parameters, config):
        set_weights(net, parameters)
        loss, accuracy = test(net, testloader)
        return loss, len(testloader.dataset), {"accuracy": accuracy}

if __name__ == "__main__":

    try:
        configs = configparser.ConfigParser()
        configs.read("config.ini")

        host = configs["client.broker"]["host"]
        port = int(configs["client.broker"]["port"])
        allow_register = configs.getboolean("events","register_events")
        
        if sys.argv[1] != "cli":
            task_reporter = TaskReporter()
            register_event("task_client","main","Started",allow_registering=allow_register,host=host,port=port)

        net = Net().to(DEVICE)
        
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
        trainloader, testloader = load_data(data_path)

        if len(sys.argv) >= 3:
            if sys.argv[2] == "test-error":
                raise Exception

        print("start")
        start_client(
            server_address="127.0.0.1:8080",
            client=FlowerClient().to_client(),
        )    
        
        if sys.argv[1] != "cli":
            register_event("task_client","main","Finished",allow_registering=allow_register,host=host,port=port)
            task_reporter.send_info("Finished")
    
    except Exception as e:
        print(f"Error! {e}")
        if sys.argv[1] == "cli":
            raise e
        register_event("task_client","main","Error!",allow_registering=allow_register,host=host,port=port)
        task_reporter.send_error(e)

