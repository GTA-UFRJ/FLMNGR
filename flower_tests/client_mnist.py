import argparse
import warnings
from collections import OrderedDict

import flwr as fl
from flwr_datasets import FederatedDataset
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision.transforms import Compose, Normalize, ToTensor
from tqdm import tqdm
import torchvision

from pathlib import Path

# #############################################################################
# 1. Regular PyTorch pipeline: nn.Module, train, test, and DataLoader
# #############################################################################

warnings.filterwarnings("ignore", category=UserWarning)
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#torch.manual_seed(42)
#torch.cuda.manual_seed(42)
DATA_PATH = "../data"


class RotatedMNIST(torchvision.datasets.MNIST):
  def __getitem__(self, i):
      pass

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(784, 200)
        self.fc2 = nn.Linear(200, 200)
        self.out = nn.Linear(200, 10)

    def forward(self, x):
        x = x.flatten(1) # [B x 784]
        x = F.relu(self.fc1(x)) # [B x 200]
        x = F.relu(self.fc2(x)) # [B x 200]
        x = self.out(x) # [B x 10]
        return x


def train(net, trainloader, epochs): 
    """Train the model on the training set."""
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(net.parameters(), lr=0.05)
    for _ in range(epochs):
        for (i, (x,y)) in enumerate(trainloader):
            x = x.to(DEVICE)
            y = y.to(DEVICE)
            optimizer.zero_grad()
            out = net(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

def test(net, testloader):
    """Validate the model on the test set."""
    criterion = torch.nn.CrossEntropyLoss()
    correct, total, loss = 0, 0, 0.0
    with torch.no_grad():
        for (t, (x,y)) in enumerate(testloader):
            x = x.to(DEVICE)
            y = y.to(DEVICE)
            out = net(x)
            loss += criterion(out, y).item()
            correct += torch.sum(torch.argmax(out, dim=1) == y).item()
            total += x.shape[0]
    accuracy = correct / total
    print("Accuracy = " + str(accuracy))
    return loss, accuracy


def load_data(partition_id):
    trainloader = torch.load("{p}/MNIST/private_dataloaders_clear/client_{i}_trainloader.pth".format(p=DATA_PATH,i=partition_id))
    testloader = torch.load("{p}/MNIST/private_dataloaders_clear/client_{i}_testloader.pth".format(p=DATA_PATH,i=partition_id))

    return trainloader, testloader


# #############################################################################
# 2. Federation of the pipeline with Flower
# #############################################################################

# Get partition id
parser = argparse.ArgumentParser(description="Flower")
parser.add_argument(
    "--partition-id",
    choices=range(0,100),
    required=True,
    type=int,
    help="Partition of the dataset divided into 3 iid partitions created artificially.",
)
partition_id = parser.parse_args().partition_id

# Load model and data (simple CNN, CIFAR-10)
net = Net().to(DEVICE)
trainloader, testloader = load_data(partition_id=partition_id)


# Define Flower client
class FlowerClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        #input("Getting model parameters. Press enter")
        return [val.cpu().numpy() for _, val in net.state_dict().items()]

    def set_parameters(self, parameters):
        #input("Setting model parameters. Press enter")
        params_dict = zip(net.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        net.load_state_dict(state_dict)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        train(net, trainloader, epochs=1)
        return self.get_parameters(config={}), len(trainloader.dataset), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        loss, accuracy = test(net, testloader)
        return loss, len(testloader.dataset), {"accuracy": accuracy}

'''
def client_fn(cid:str):
    return FlowerClient().to_client()
app = ClientApp(client_fn=client_fn,)
'''

# Start Flower client
fl.client.start_client(
    server_address="127.0.0.1:8080",
    client=FlowerClient().to_client(),
    root_certificates=Path("./certificates/ca.crt").read_bytes()
)