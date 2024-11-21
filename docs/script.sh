#!/bin/bash
sphinx-build -M html source build
python3 -m http.server -d build/html
