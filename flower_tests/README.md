# Flower Example using PyTorch

### Pre-requisites

* Miniconda 3

### Create and actiavte conda environment with requirements 

```
conda create -n flmngr
pip install -r requirements.txt
```

### Run server

```
python3 server_mnist.py
```


### Run clients in other terminals

```
python3 client_mnist.py --partition-id 0
python3 client_mnist.py --partition-id 1
```