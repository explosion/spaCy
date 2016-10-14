#!/bin/bash

if [ "${VIA}" == "pypi" ]; then
    rm -rf *
    pip install spacy
fi

if [ "${VIA}" == "sdist" ]; then
  rm -rf *
  wget https://api.explosion.ai/build/spacy/sdist/$TRAVIS_COMMIT
  pip install $TRAVIS_COMMIT
fi


if [ "${VIA}" == "compile" ]; then
  pip install -r requirements.txt
  pip install -e .
  mkdir -p corpora/en
  cd corpora/en
  wget --no-check-certificate http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz
  tar -xzf WordNet-3.0.tar.gz
  mv WordNet-3.0 wordnet
  cd ../../
  mkdir models/
  python bin/init_model.py en lang_data/ corpora/ models/en
fi
