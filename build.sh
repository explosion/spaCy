#!/bin/bash -x
set -e

if [[ $# < 2 ]]; then
    echo "usage: $0 <python-path> <install-mode> [<pip-date>]"
    exit
fi

if [ ! -d ".build" ]; then
    virtualenv .build --python $1
fi
. .build/bin/activate

# install
pip install -U pip

if [ -n "${3+1}" ]; then
    python pip-date.py $3 pip setuptools wheel six
fi

pip install -r requirements.txt
if [[ "$2" == "pip" ]]; then
  python setup.py sdist;
  pip install dist/*;
fi
if [[ "$2" == "setup-install" ]]; then
  python setup.py install;
fi
if [[ "$2" == "setup-develop" ]]; then
  python setup.py develop;
  pip install -e .;
fi
pip install pytest
pip list

# script
cd .build
python -m spacy.en.download
python -m pytest ../spacy/ -x --models --vectors --slow
