#!/bin/bash
set -e

if [ ! -d ".build" ]; then
    virtualenv .build --python $1
fi

. .build/bin/activate
python build.py $2 $3
