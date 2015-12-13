#!/bin/bash
if [ ! -d ".build" ]; then
    virtualenv --always-copy .build
fi
. .build/bin/activate
pip install -U -r requirements.txt
python -m tox $@
