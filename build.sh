#!/bin/bash
if [ ! -d ".build" ]; then
    virtualenv .build
fi
. .build/bin/activate
pip install -U -r requirements.txt
pip install -U tox
python -m tox $@
