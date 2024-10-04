# Data preparation

The goal of this project is to prepare dataloaders for FedAvg Distributed and 
flowers_validation projects. 

Create the following directories:
```
mkdir MNIST
mkdir MNIST/private_dataloaders_clear
mkdir MNIST/private_dataloaders
mkdir MNIST/public_dataloaders
```

For downloading the data, prepare the dataloaders and running, run:

```
python3 generate_mnist.py    \
--num_partition          10  \
--num_used_clients       10  \
--train_batch_size       10  \
--server_test_batch_size 10  \
--train_fraction         0.9 \
--download     
```

You can replace MNIST by CIFAR10 in all the following commands in order to 
prepare CIFAR10 dataloaders.

