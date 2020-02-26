SHELL := /bin/bash
WHEELHOUSE := ./wheelhouse
PYVER := 3.6
VENV := ./env$(PYVER)

version = $(shell "bin/get-version.sh")

dist/spacy-$(version).pex : wheelhouse/spacy-$(version)-*.whl
	pex -f ./wheelhouse --no-index --disable-cache -m spacy -o dist/spacy-$(version).pex spacy==$(version) jsonschema
	chmod a+rx dist/spacy-$(version).pex

dist/pytest.pex : wheelhouse/pytest-*.whl
	$(VENV)/bin/pex -f ./wheelhouse --no-index --disable-cache -m pytest -o dist/pytest.pex pytest pytest-timeout mock
	chmod a+rx dist/pytest.pex

wheelhouse/spacy-$(version)-%.whl : $(VENV)/bin/pex setup.py spacy/*.py* spacy/*/*.py*
	$(VENV)/bin/pip wheel . -w ./wheelhouse
	$(VENV)/bin/pip wheel jsonschema spacy_lookups_data -w ./wheelhouse

wheelhouse/pytest-%.whl : $(VENV)/bin/pex
	$(VENV)/bin/pip wheel pytest pytest-timeout mock -w ./wheelhouse

$(VENV) : 
	python$(PYVER) -m venv $(VENV)
	$(VENV)/bin/python -m pip install pex wheel

.PHONY : clean test

test : dist/spacy-$(version).pex dist/pytest.pex
	PEX_PATH=dist/spacy-$(version).pex ./dist/pytest.pex --pyargs spacy -x

clean : setup.py
	source env3.6/bin/activate
	rm -rf dist/*
	rm -rf ./wheelhouse
	python setup.py clean --all
