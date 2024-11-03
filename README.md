# FLMNGR

### Requisites:

* Conda

### Configuration

Create conda environment:
```
conda create -n flmngr python=3.12.7
```

Activate conda environment:
```
conda activate flmngr
```

Install requirements:
```
conda install pip
pip install -r requirements.txt
```

### Documentation 

```
cd docs
sphinx-build -M html source build
```
