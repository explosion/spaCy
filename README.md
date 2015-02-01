spaCy
=====

**Several bug-fixes have now been pushed to master**

Builds on Travis CI are failing periodically due to memory errors,  but not on my local machines (for Python2.7 and Python 3.4). The problem is likely due to non-portable usage of the Py_UNICODE data type in my Cython code, or possibly in the binary file formats of lexemes.bin, vec.bin, or the model file read by thinc.learner.LinearModel

I'm trying to reproduce the problem. Once this is fixed and docs are updated I will push version 0.4 to PyPi.

http://honnibal.github.io/spaCy

Fast, state-of-the-art natural language processing pipeline. Commercial licenses available, or use under AGPL.

Tested (and working) with:

* CPython 2.7
* CPython 3.4
* OSX
* Linux 

Untested:

* Windows

Fails with:

* PyPy 2.7
* PyPy 3.4

