@echo off
rem   Python 2.7 x86-64 spaCy Windows test

IF "%1"=="32" GOTO x86-32
IF "%1"=="64" GOTO x86-64

@echo Usage: test-Python27 32/64
EXIT /B

:x86-32
PATH = D:\Python27-32\;D:\Python27-32\Scripts;%PATH%
GOTO run

:x86-64
PATH = D:\Python27\;D:\Python27\Scripts;%PATH%

:run
set PYTHONPATH=%CD%
set PYTHONPATH

rem python -m spacy.en.download

pause

python tests\test_basic_create.py
python tests\test_basic_load.py

py.test tests/ -x

python -c "import spacy.en; nlp = spacy.en.English(); print([w.text for w in nlp(u'I would like to be a dog')])"
python examples\information_extraction.py
python examples\matcher_example.py

