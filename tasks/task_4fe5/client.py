import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
if sys.argv[1] != "cli":
    sys.path.append(sys.argv[1])

from flwr.client import NumPyClient, start_client
from task import DEVICE, Net, get_weights, load_data, set_weights, test, train
from utils.task_reporter import TaskReporter

# Define FlowerClient and client_fn
class FlowerClient(NumPyClient):
    def fit(self, parameters, config):
        set_weights(net, parameters)
        results = train(net, trainloader, testloader, epochs=1, device=DEVICE)
        return get_weights(net), len(trainloader.dataset), results

    def evaluate(self, parameters, config):
        set_weights(net, parameters)
        loss, accuracy = test(net, testloader)
        return loss, len(testloader.dataset), {"accuracy": accuracy}

if __name__ == "__main__":

    if sys.argv[1] != "cli":
        task_reporter = TaskReporter()

    net = Net().to(DEVICE)
    trainloader, testloader = load_data()

    try:
        start_client(
            server_address="127.0.0.1:8080",
            client=FlowerClient().to_client(),
        )
    except Exception as e:
        task_reporter.send_error(e)
