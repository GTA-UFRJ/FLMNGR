#!/bin/bash

if [[ -n $(command -v conda) ]]; then 
	if [[ -z $(conda env list | grep flmngr) ]]; then 
		conda create -n flmngr
	fi
	conda init
	conda activate flmngr
	pip install -r requirements.txt
fi
