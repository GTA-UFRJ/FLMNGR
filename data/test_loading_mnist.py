
import torch
import torchvision
from generate_mnist import RotatedMNIST
import matplotlib.pyplot as plt

loader = torch.load("./MNIST/private_dataloaders_clear/client_0_trainloader.pth")
examples = enumerate(loader)

fig = plt.figure()

def plot_image_set(example_data, example_targets):
    for i in range(6):
        plt.subplot(2,3,i+1)
        plt.tight_layout()
        plt.imshow(example_data[i][0], cmap='gray', interpolation='none')
        plt.title("Ground Truth: {}".format(example_targets[i]))
        plt.xticks([])
        plt.yticks([])
    plt.show()

key = ''
while(key != 'q'):
    id, (example_data, example_targets) = next(examples)
    plot_image_set(example_data, example_targets)
