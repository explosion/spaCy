@echo off
rem   Python 2.7 x86-64 spaCy Windows build
rem   Toolchain:
rem      Python 2.7.10  :)
rem      Microsoft Visual C++ Compiler Package for Python 2.7:
rem            http://www.microsoft.com/en-us/download/details.aspx?id=44266
rem      C99 compliant stdint.h for MSVC: 
rem            http://msinttypes.googlecode.com/svn/trunk/stdint.h

IF "%1"=="32" GOTO x86-32
IF "%1"=="64" GOTO x86-64

@echo Usage: build-Python27 32/64
EXIT /B

:x86-32
PATH = D:\Python27-32\;D:\Python27-32\Scripts;%PATH%
GOTO run

:x86-64
PATH = D:\Python27\;D:\Python27\Scripts;%PATH%

:run

IF NOT EXIST "%LOCALAPPDATA%\Programs\Common\Microsoft\Visual C++ for Python\9.0\VC\include\stdint.h" COPY D:\local\include\stdint.h "%LOCALAPPDATA%\Programs\Common\Microsoft\Visual C++ for Python\9.0\VC\include\stdint.h"

pip install --upgrade setuptools
pip install cython fabric fabtools
pip install -r requirements.txt
python setup.py build_ext --inplace
python setup.py install

rem mkdir corpora
rem cd corpora
rem mkdir en
rem cd en

rem powershell -Command "(New-Object Net.WebClient).DownloadFile('http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz', 'WordNet-3.0.tar.gz')"

rem set PYTHONPATH = %~dp0
rem python bin\init_model.py en lang_data\ corpora\ spacy\en\data

rem python setup.py test
rem python setup.py install
rem python tests\conftest.py