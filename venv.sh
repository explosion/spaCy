#!/bin/bash
set -e

if [ ! -d ".build" ]; then
    virtualenv .build --python $1
fi

if [ -d ".build/bin" ]; then
    source .build/bin/activate
elif [ -d ".build/Scripts" ]; then
    source .build/Scripts/activate
fi

python build.py prepare $3
python build.py $2
python build.py test
