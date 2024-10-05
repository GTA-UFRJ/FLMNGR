from flwr.client import NumPyClient, start_client
from task import DEVICE, Net, get_weights, load_data, set_weights, test, train

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
    net = Net().to(DEVICE)
    trainloader, testloader = load_data()

    start_client(
        server_address="127.0.0.1:8080",
        client=FlowerClient().to_client(),
    )
