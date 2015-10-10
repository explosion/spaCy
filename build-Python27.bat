@echo off
rem   Python 2.7 x86-64 spaCy Windows build
rem   Toolchain:
rem      Python 2.7.10  :)
rem      Microsoft Visual C++ Compiler Package for Python 2.7:
rem            http://www.microsoft.com/en-us/download/details.aspx?id=44266
rem      C99 compliant stdint.h for MSVC: 
rem            http://msinttypes.googlecode.com/svn/trunk/stdint.h


PATH = D:\Python27\;D:\Python27\Scripts;%PATH%
IF NOT EXIST "%LOCALAPPDATA%\Programs\Common\Microsoft\Visual C++ for Python\9.0\VC\include\stdint.h" COPY D:\local\include\stdint.h "%LOCALAPPDATA%\Programs\Common\Microsoft\Visual C++ for Python\9.0\VC\include\stdint.h"


SET INCLUDE = D:\local\include;%INCLUDE%

pip install --upgrade setuptools
pip install cython fabric fabtools
pip install -r requirements.txt
python setup.py build_ext --inplace
pause
python setup.py build
python setup.py test
python setup.py install
rem python tests\conftest.py
rem python tests\test_matcher.py    
