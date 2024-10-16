#!/bin/bash

if [[ -n $(command -v conda) ]]; then 
	if [[ -z $(conda env list | grep flmngr) ]]; then 
		# Install environment
	fi
	conda activate flmngr
fi
