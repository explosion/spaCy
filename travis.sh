#!/bin/bash

if [ "${VIA}" == "pypi" ]; then
    rm -rf *
    pip install spacy-nightly
    python -m spacy download en
fi

if [[ "${VIA}" == "sdist" && "${TRAVIS_PULL_REQUEST}" == "false" ]]; then
  rm -rf *
  pip uninstall spacy
  wget https://api.explosion.ai/build/spacy/sdist/$TRAVIS_COMMIT
  mv $TRAVIS_COMMIT sdist.tgz
  pip install -U sdist.tgz
fi


if [ "${VIA}" == "compile" ]; then
  pip install -r requirements.txt
  python setup.py build_ext --inplace
  pip install -e .
fi
