# FLMNGR

### Requisites:

* Conda

### Configuration

Create conda environment:
```
conda create -n flmngr
```

Activate conda environment:
```
conda activate flmngr
```

Install requirements:
```
pip install -r requirements.txt
```

### Test Flower task

In one terminal, run the Flower server
```
python -m tasks.task_4fe5.server cli
```

In other terminal, run the Flower client after waiting the server to start
```
python -m tasks.task_4fe5.client cli
```

In other terminal, run the Flower client after waiting the server to start
```
python -m tasks.task_4fe5.client cli
```

In a third terminal, run the second Flower client
```
python -m tasks.task_4fe5.client cli
```

### Test server/client task initializers

