SHELL := /bin/bash
sha = $(shell "git" "rev-parse" "--short" "HEAD")
version = $(shell "bin/get-version.sh")
wheel = spacy-$(version)-cp36-cp36m-linux_x86_64.whl

dist/spacy.pex : dist/spacy-$(sha).pex
	cp dist/spacy-$(sha).pex dist/spacy.pex
	chmod a+rx dist/spacy.pex

dist/spacy-$(sha).pex : dist/$(wheel)
	env3.6/bin/python -m pip install pex==1.5.3
	env3.6/bin/pex pytest dist/$(wheel) spacy_lookups_data -e spacy -o dist/spacy-$(sha).pex

dist/$(wheel) : setup.py spacy/*.py* spacy/*/*.py*
	python3.6 -m venv env3.6
	source env3.6/bin/activate
	env3.6/bin/pip install wheel
	env3.6/bin/pip install -r requirements.txt --no-cache-dir 
	env3.6/bin/python setup.py build_ext --inplace
	env3.6/bin/python setup.py sdist
	env3.6/bin/python setup.py bdist_wheel

.PHONY : clean

clean : setup.py
	source env3.6/bin/activate
	rm -rf dist/*
	python setup.py clean --all
