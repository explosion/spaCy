SHELL := /bin/bash
sha = $(shell "git" "rev-parse" "--short" "HEAD")

dist/spacy.pex : 
	python3.6 -m venv env3.6
	source env3.6/bin/activate
	pip install wheel
	pip install -r requirements.txt --no-cache-dir --no-binary :all:
	python setup.py build_ext --inplace
	python setup.py sdist
	python setup.py bdist_wheel
	python -m pip install pex
	pex dist/*.whl -e spacy -o dist/spacy-$(sha).pex
	cp dist/spacy-$(sha).pex dist/spacy.pex
	chmod a+rx dist/spacy.pex
