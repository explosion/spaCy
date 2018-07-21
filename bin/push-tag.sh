#!/usr/bin/env bash

set -e

# Insist repository is clean
git diff-index --quiet HEAD

git checkout master
git pull origin master
version=$(grep "__version__ = " spacy/about.py)
version=${version/__version__ = }
version=${version/\'/}
version=${version/\'/}
git tag "v$version"
git push origin --tags
