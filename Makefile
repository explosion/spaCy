SHELL := /bin/bash

ifndef SPACY_EXTRAS
override SPACY_EXTRAS = spacy-lookups-data jieba pkuseg==0.0.25 sudachipy sudachidict_core
endif

ifndef PYVER
override PYVER = 3.6
endif

VENV := ./env$(PYVER)

version := $(shell "bin/get-version.sh")
package := $(shell "bin/get-package.sh")

ifndef SPACY_BIN
override SPACY_BIN = $(package)-$(version).pex
endif

dist/$(SPACY_BIN) : wheelhouse/spacy-$(version).stamp
	$(VENV)/bin/pex \
		-f ./wheelhouse \
		--no-index \
		--disable-cache \
		-m spacy \
		-o $@ \
		$(package)==$(version) \
		$(SPACY_EXTRAS)
	chmod a+rx $@
	cp $@ dist/spacy.pex

dist/pytest.pex : wheelhouse/pytest-*.whl
	$(VENV)/bin/pex -f ./wheelhouse --no-index --disable-cache -m pytest -o $@ pytest pytest-timeout mock
	chmod a+rx $@

wheelhouse/spacy-$(PYVER)-$(version).stamp : $(VENV)/bin/pex setup.py spacy/*.py* spacy/*/*.py*
	$(VENV)/bin/pip wheel . -w ./wheelhouse
	$(VENV)/bin/pip wheel $(SPACY_EXTRAS) -w ./wheelhouse

	touch $@

wheelhouse/pytest-%.whl : $(VENV)/bin/pex
	$(VENV)/bin/pip wheel pytest pytest-timeout mock -w ./wheelhouse

$(VENV)/bin/pex :
	python$(PYVER) -m venv $(VENV)
	$(VENV)/bin/pip install -U pip setuptools pex wheel

.PHONY : clean test

test : dist/spacy-$(version).pex dist/pytest.pex
	( . $(VENV)/bin/activate ; \
	PEX_PATH=dist/spacy-$(version).pex ./dist/pytest.pex --pyargs spacy -x ; )

clean : setup.py
	rm -rf dist/*
	rm -rf ./wheelhouse
	rm -rf $(VENV)
	python setup.py clean --all
