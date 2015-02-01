spaCy
=====

[![Build Status](https://travis-ci.org/honnibal/spaCy.svg?branch=master)](https://travis-ci.org/honnibal/spaCy)

http://honnibal.github.io/spaCy

Fast, state-of-the-art natural language processing pipeline. Commercial licenses available, or use under AGPL.


* Several bug-fixes have now been pushed to master
* Tests fail on some platforms, including Travis CI, due to memory errors.
* Tests pass on my local machines OSX and Ubuntu machines (for Python2.7 and Python 3.4)

The problem is likely due to non-portable usage of the Py_UNICODE data type in my Cython code, or possibly in the binary file formats of lexemes.bin, vec.bin, or the model file read by thinc.learner.LinearModel.

I'm trying to reproduce the problem. Once this is fixed and docs are updated I will push version 0.4 to PyPi.

I have a flight from Sydney to New York in 24 hours, so this problem may remain unfixed for a few days.


Supports:

* CPython 2.7
* CPython 3.4
* OSX
* Linux 

Want to support:

* Windows

Difficult to support:

* PyPy 2.7
* PyPy 3.4

