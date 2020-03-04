SHELL := /bin/bash
PYVER := 3.6
VENV := ./env$(PYVER)

version := $(shell "bin/get-version.sh")

dist/spacy-$(version).pex : wheelhouse/spacy-$(version).stamp
	$(VENV)/bin/pex -f ./wheelhouse --no-index --disable-cache -m spacy -o $@ spacy==$(version) jsonschema
	chmod a+rx $@

dist/pytest.pex : wheelhouse/pytest-*.whl
	$(VENV)/bin/pex -f ./wheelhouse --no-index --disable-cache -m pytest -o $@ pytest pytest-timeout mock
	chmod a+rx $@

wheelhouse/spacy-$(version).stamp : $(VENV)/bin/pex setup.py spacy/*.py* spacy/*/*.py*
	$(VENV)/bin/pip wheel . -w ./wheelhouse
	$(VENV)/bin/pip wheel jsonschema spacy_lookups_data -w ./wheelhouse
	touch $@

wheelhouse/pytest-%.whl : $(VENV)/bin/pex
	$(VENV)/bin/pip wheel pytest pytest-timeout mock -w ./wheelhouse

$(VENV)/bin/pex :
	python$(PYVER) -m venv $(VENV)
	$(VENV)/bin/python -m pip install pex wheel

.PHONY : clean test

test : dist/spacy-$(version).pex dist/pytest.pex
	( . $(VENV)/bin/activate ; \
	PEX_PATH=dist/spacy-$(version).pex ./dist/pytest.pex --pyargs spacy -x ; )

clean : setup.py
	rm -rf dist/*
	rm -rf ./wheelhouse
	rm -rf $(VENV)
	python setup.py clean --all
