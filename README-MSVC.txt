Python 2.7 Windows build has been tested with the following toolchain:
	- Python 2.7.10  :)
	- Microsoft Visual C++ Compiler Package for Python 2.7		http://www.microsoft.com/en-us/download/details.aspx?id=44266
	- C99 compliant stdint.h for MSVC				http://msinttypes.googlecode.com/svn/trunk/stdint.h
	 (C99 complian stdint.h header which is not supplied with Microsoft Visual C++ compiler prior to MSVC 2010)

Build steps:
	- pip install --upgrade setuptools
	- pip install cython fabric fabtools
	- pip install -r requirements.txt
	- python setup.py build_ext --inplace
 
 