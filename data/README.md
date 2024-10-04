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

For downloading the data, prepare the dataloaders and running without
Gramine-SGX, run:

```
python3 generate_mnist.py   \
--num_partition          100  \
--num_used_clients       3    \
--train_batch_size       10   \
--server_test_batch_size 1000 \
--train_fraction         0.8  \
--download     
```

For doing the same thing for running with Gramine-SGX,run:

```
make -f generate_mnist.makefile \
SGX=1 \
KEY_NAME=_sgx_mrsigner \
BASE_PATH=$(pwd)
```

```
gramine-sgx generate_mnist ./generate_mnist.py \
--num_partition          100  \
--num_used_clients       3    \
--train_batch_size       10   \
--server_test_batch_size 1000 \
--train_fraction         0.8  \
--gramine     
```

The difference is that this will generate encrypted data with SGX sealing key.

You can replace MNIST by CIFAR10 in all the following commands in order to 
prepare CIFAR10 dataloaders.

