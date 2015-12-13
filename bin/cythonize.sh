#!/bin/bash
if [ ! -d ".cythonize" ]; then
    virtualenv .cythonize
fi
. .cythonize/bin/activate
pip install -U -r requirements.txt
./bin/cythonize.py $@
