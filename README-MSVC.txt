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

If you are using traditional Microsoft SDK (v7.0 for Python 2.x or v7.1 for Python 3.x) consider run_with_env.cmd from appveyor folder (submodule) as a guideline for environment setup. 
It can be also used as shell conviguration script for your build, install and run commands, i.e.: cmd /E:ON /V:ON /C run_with_env.cmd <your command> 

 
 