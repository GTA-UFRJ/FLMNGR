#!/bin/bash

if [[ -n $(command -v conda) ]]; then 
	if [[ -z $(conda env list | grep flmngr) ]]; then 
		conda create -n flmngr python=3.12.7
		conda activate flmngr
		conda install pip
		pip install -r requirements.txt
	fi
	conda activate flmngr
fi
