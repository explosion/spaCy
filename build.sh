#!/bin/bash -x
set -e

if [[ $# < 3 ]]; then
    echo "usage: $0 <python-path> <pip-date> <install-mode>"
    exit
fi

if [ ! -d ".build" ]; then
    virtualenv .build --python $1
fi
. .build/bin/activate

# install
pip install -U pip
python pip-date.py $2 pip setuptools wheel six
pip install -r requirements.txt
if [[ "$3" == "pip" ]]; then
  python setup.py sdist;
  pip install dist/*;
fi
if [[ "$3" == "setup-install" ]]; then
  python setup.py install;
fi
if [[ "$3" == "setup-develop" ]]; then
  python setup.py develop;
  pip install -e .;
fi
pip install pytest
pip list

# script
cd .build
python -m spacy.en.download
python -m pytest ../spacy/ -x --models --vectors --slow
