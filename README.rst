==============================
spaCy: Industrial-strength NLP
==============================

.. image:: https://travis-ci.org/spacy-io/spaCy.svg?branch=master
    :target: https://travis-ci.org/spacy-io/spaCy

spaCy is a library for advanced natural language processing in Python and Cython.

Documentation and details: https://spacy.io/

spaCy is built on the very latest research, but it isn't researchware.  It was
designed from day 1 to be used in real products. It's commercial open-source
software, released under the MIT license.


Features
--------

* Labelled dependency parsing (91.8% accuracy on OntoNotes 5)
* Named entity recognition (82.6% accuracy on OntoNotes 5)
* Part-of-speech tagging (97.1% accuracy on OntoNotes 5)
* Easy to use word vectors
* All strings mapped to integer IDs
* Export to numpy data arrays
* Alignment maintained to original string, ensuring easy mark up calculation
* Range of easy-to-use orthographic features.
* No pre-processing required. spaCy takes raw text as input, warts and newlines and all.

Top Peformance
-------------

* Fastest in the world: <50ms per document.  No faster system has ever been
  announced.
* Accuracy within 1% of the current state of the art on all tasks performed
  (parsing, named entity recognition, part-of-speech tagging).  The only more
  accurate systems are an order of magnitude slower or more.

Supports
--------

* CPython 2.6, 2.7, 3.3, 3.4, 3.5 (only 64 bit)
* OSX
* Linux
* Windows (Cygwin, MinGW, Visual Studio)

Difficult to support:

* PyPy
