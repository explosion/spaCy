spaCy: Industrial-strength NLP
******************************

spaCy is a library for advanced natural language processing in Python and 
Cython. `See here <https://spacy.io>`_ for documentation and details. spaCy is built on 
the very latest research, but it isn't researchware.  It was designed from day 1 
to be used in real products. It's commercial open-source software, released under 
the MIT license.

.. image:: http://i.imgur.com/wFvLZyJ.png
    :target: https://travis-ci.org/explosion/spaCy

.. image:: https://travis-ci.org/explosion/spaCy.svg?branch=master
    :target: https://travis-ci.org/explosion/spaCy

Where to ask questions
======================

+---------------------------+------------------------------------------------------------------------------------------------------------+
| 🔴 **Bug reports**        | `GitHub Issue tracker <https://github.com/explosion/spaCy/issues>`_                                        |
+---------------------------+------------------------------------------------------------------------------------------------------------+
| ⁉️ **Usage questions**    | `StackOverflow <http://stackoverflow.com/questions/tagged/spacy>`_, `Reddit usergroup                      | 
|                           | <https://www.reddit.com/r/spacynlp>`_, `Gitter chat <https://gitter.im/spaCy-users>`_                      |
+---------------------------+------------------------------------------------------------------------------------------------------------+
| 💬 **General discussion** |  `Reddit usergroup <https://www.reddit.com/r/spacynlp>`_, `Gitter chat <https://gitter.im/spaCy-users>`_   |
+---------------------------+------------------------------------------------------------------------------------------------------------+
| 💥 **Commercial support** |  contact@explosion.ai                                                                                      |
+---------------------------+------------------------------------------------------------------------------------------------------------+

Features
========

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
==============

* Fastest in the world: <50ms per document.  No faster system has ever been
  announced.
* Accuracy within 1% of the current state of the art on all tasks performed
  (parsing, named entity recognition, part-of-speech tagging).  The only more
  accurate systems are an order of magnitude slower or more.

Supports
========

* CPython 2.6, 2.7, 3.3, 3.4, 3.5 (only 64 bit)
* OSX
* Linux
* Windows (Cygwin, MinGW, Visual Studio)

Install spaCy
=============

spaCy is compatible with 64-bit CPython 2.6+/3.3+ and runs on Unix/Linux, OS X 
and Windows. Source and binary packages are available via 
`pip <https://pypi.python.org/pypi/spacy>`_ and `conda <https://anaconda.org/spacy/spacy>`_. 
If there are no binary packages for your platform available please make sure that
you have a working build enviroment set up. See notes on Ubuntu, OS X and Windows
for details.

conda
-----

.. code:: bash

    conda config --add channels spacy  # only needed once
    conda install spacy

pip
---

When using pip it is generally recommended to install packages in a virtualenv to
avoid modifying system state:

.. code:: bash

    # make sure you are using a recent pip/virtualenv version
    python -m pip install -U pip virtualenv

    virtualenv .env
    source .env/bin/activate

    pip install spacy

Python packaging is awkward at the best of times, and it's particularly tricky with
C extensions, built via Cython, requiring large data files. So, please report issues
as you encounter them.

Install model
=============

After installation you need to download a language model. Currently only models for 
English and German, named ``en`` and ``de``, are available.

.. code:: bash

    python -m spacy.en.download
    python -m spacy.de.download
    sputnik --name spacy en_glove_cc_300_1m_vectors # For better word vectors

Then check whether the model was successfully installed:

.. code:: bash

    python -c "import spacy; spacy.load('en'); print('OK')"

The download command fetches and installs about 500 MB of data which it installs 
within the ``spacy`` package directory.

Upgrading spaCy
===============

To upgrade spaCy to the latest release:

conda
-----

.. code:: bash

    conda update spacy

pip
---

.. code:: bash

    pip install -U spacy

Sometimes new releases require a new language model. Then you will have to upgrade to 
a new model, too. You can also force re-downloading and installing a new language model:

.. code:: bash

    python -m spacy.en.download --force

Compile from source
===================

The other way to install spaCy is to clone its GitHub repository and build it from 
source. That is the common way if you want to make changes to the code base.

You'll need to make sure that you have a development enviroment consisting of a 
Python distribution including header files, a compiler, pip, virtualenv and git 
installed. The compiler part is the trickiest. How to do that depends on your 
system. See notes on Ubuntu, OS X and Windows for details.

.. code:: bash

    # make sure you are using recent pip/virtualenv versions
    python -m pip install -U pip virtualenv

    #  find git install instructions at https://git-scm.com/downloads
    git clone https://github.com/spacy-io/spaCy.git

    cd spaCy
    virtualenv .env && source .env/bin/activate
    pip install -r requirements.txt
    pip install -e .
    
Compared to regular install via pip and conda `requirements.txt <requirements.txt>`_ 
additionally installs developer dependencies such as cython.

Ubuntu
------

Install system-level dependencies via ``apt-get``:

.. code:: bash

    sudo apt-get install build-essential python-dev git

OS X
----

Install a recent version of XCode, including the so-called "Command Line Tools". 
OS X ships with Python and git preinstalled.

Windows
-------

Install a version of Visual Studio Express or higher that matches the version 
that was used to compile your Python interpreter. For official distributions 
these are VS 2008 (Python 2.7), VS 2010 (Python 3.4) and VS 2015 (Python 3.5).

Workaround for obsolete system Python
=====================================

If you're stuck using a system with an old version of Python, and you don't 
have root access, we've prepared a bootstrap script to help you compile a local 
Python install. Run:

.. code:: bash

    curl https://raw.githubusercontent.com/spacy-io/gist/master/bootstrap_python_env.sh | bash && source .env/bin/activate

Run tests
=========

spaCy comes with an extensive test suite. First, find out where spaCy is 
installed:

.. code:: bash
    
    python -c "import os; import spacy; print(os.path.dirname(spacy.__file__))"

Then run ``pytest`` on that directory. The flags ``--vectors``, ``--slow`` 
and ``--model`` are optional and enable additional tests:

.. code:: bash
    
    # make sure you are using recent pytest version
    python -m pip install -U pytest

    python -m pytest <spacy-directory> --vectors --model --slow

API Documentation and Usage Examples
====================================

For the detailed documentation, check out the `spaCy website <https://spacy.io/docs/>`_.

* `Usage Examples <https://spacy.io/docs/#examples>`_
* `API <https://spacy.io/docs/#api>`_
* `Annotation Specification <https://spacy.io/docs/#annotation>`_
* `Tutorials <https://spacy.io/docs/#tutorials>`_


Changelog
=========

2016-05-10 `v0.101.0 <../../releases/tag/0.101.0>`_: *Fixed German model*
-------------------------------------------------------------------------

* Fixed bug that prevented German parses from being deprojectivised.
* Bug fixes to sentence boundary detection.
* Add rich comparison methods to the Lexeme class.
* Add missing ``Doc.has_vector`` and ``Span.has_vector`` properties.
* Add missing ``Span.sent`` property.

2016-05-05 `v0.100.7 <../../releases/tag/0.100.7>`_: *German!*
--------------------------------------------------------------

spaCy finally supports another language, in addition to English. We're lucky 
to have Wolfgang Seeker on the team, and the new German model is just the 
beginning. Now that there are multiple languages, you should consider loading 
spaCy via the ``load()`` function. This function also makes it easier to load extra 
word vector data for English:

.. code:: python

    import spacy
    en_nlp = spacy.load('en', vectors='en_glove_cc_300_1m_vectors')
    de_nlp = spacy.load('de')
    
To support use of the load function, there are also two new helper functions: 
``spacy.get_lang_class`` and ``spacy.set_lang_class``. Once the German model is 
loaded, you can use it just like the English model:

.. code:: python

    doc = nlp(u'''Wikipedia ist ein Projekt zum Aufbau einer Enzyklopädie aus freien Inhalten, zu dem du mit deinem Wissen beitragen kannst. Seit Mai 2001 sind 1.936.257 Artikel in deutscher Sprache entstanden.''')
    
    for sent in doc.sents:
        print(sent.root.text, sent.root.n_lefts, sent.root.n_rights)
    
    # (u'ist', 1, 2)
    # (u'sind', 1, 3)
    
The German model provides tokenization, POS tagging, sentence boundary detection, 
syntactic dependency parsing, recognition of organisation, location and person 
entities, and word vector representations trained on a mix of open subtitles and 
Wikipedia data. It doesn't yet provide lemmatisation or morphological analysis, 
and it doesn't yet recognise numeric entities such as numbers and dates.

**Bugfixes**

* spaCy < 0.100.7 had a bug in the semantics of the ``Token.__str__`` and ``Token.__unicode__`` built-ins: they included a trailing space.
* Improve handling of "infixed" hyphens. Previously the tokenizer struggled with multiple hyphens, such as "well-to-do".
* Improve handling of periods after mixed-case tokens
* Improve lemmatization for English special-case tokens
* Fix bug that allowed spaces to be treated as heads in the syntactic parse
* Fix bug that led to inconsistent sentence boundaries before and after serialisation.
* Fix bug from deserialising untagged documents.

2016-03-08 `v0.100.6 <../../releases/tag/0.100.6>`_: *Add support for GloVe vectors*
------------------------------------------------------------------------------------

This release offers improved support for replacing the word vectors used by spaCy. 
To install Stanford's GloVe vectors, trained on the Common Crawl, just run:

.. code:: bash
    sputnik --name spacy install en_glove_cc_300_1m_vectors

To reduce memory usage and loading time, we've trimmed the vocabulary down to 1m entries.

This release also integrates all the code necessary for German parsing. A German model 
will be released shortly. To assist in multi-lingual processing, we've added a ``load()`` 
function. To load the English model with the GloVe vectors:

.. code:: python
    spacy.load('en', vectors='en_glove_cc_300_1m_vectors')

2016-02-07 `v0.100.5 <../../releases/tag/0.100.5>`_
---------------------------------------------------

Fix incorrect use of header file, caused from problem with thinc

2016-02-07 `v0.100.4 <../../releases/tag/0.100.4>`_: *Fix OSX problem introduced in 0.100.3*
--------------------------------------------------------------------------------------------

Small correction to right_edge calculation

2016-02-06 `v0.100.3 <../../releases/tag/0.100.3>`_
---------------------------------------------------

Support multi-threading, via the ``.pipe`` method. spaCy now releases the GIL around the
parser and entity recognizer, so systems that support OpenMP should be able to do
shared memory parallelism at close to full efficiency.

We've also greatly reduced loading time, and fixed a number of bugs.

2016-01-21 `v0.100.2 <../../releases/tag/0.100.2>`_
---------------------------------------------------

Fix data version lock that affected v0.100.1

2016-01-21 `v0.100.1 <../../releases/tag/0.100.1>`_: *Fix install for OSX*
--------------------------------------------------------------------------

v0.100 included header files built on Linux that caused installation to fail on OSX.
This should now be corrected. We also update the default data distribution, to
include a small fix to the tokenizer.

2016-01-19 `v0.100 <../../releases/tag/0.100>`_: *Revise setup.py, better model downloads, bug fixes*
-----------------------------------------------------------------------------------------------------

* Redo setup.py, and remove ugly headers_workaround hack. Should result in fewer install problems.
* Update data downloading and installation functionality, by migrating to the Sputnik data-package manager. This will allow us to offer finer grained control of data installation in future.
* Fix bug when using custom entity types in ``Matcher``. This should work by default when using the
  ``English.__call__`` method of running the pipeline. If invoking ``Parser.__call__`` directly to do NER,
  you should call the ``Parser.add_label()`` method to register your entity type.
* Fix head-finding rules in ``Span``.
* Fix problem that caused ``doc.merge()`` to sometimes hang
* Fix problems in handling of whitespace

2015-11-08 `v0.99 <../../releases/tag/0.99>`_: *Improve span merging, internal refactoring*
-------------------------------------------------------------------------------------------

* Merging multi-word tokens into one, via the ``doc.merge()`` and ``span.merge()`` methods, no longer invalidates existing ``Span`` objects. This makes it much easier to merge multiple spans, e.g. to merge all named entities, or all base noun phrases. Thanks to @andreasgrv for help on this patch.
* Lots of internal refactoring, especially around the machine learning module, thinc. The thinc API has now been improved, and the spacy._ml wrapper module is no longer necessary.
* The lemmatizer now lower-cases non-noun, noun-verb and non-adjective words.
* A new attribute, ``.rank``, is added to Token and Lexeme objects, giving the frequency rank of the word.

2015-11-03 `v0.98 <../../releases/tag/0.98>`_: *Smaller package, bug fixes*
---------------------------------------------------------------------------

* Remove binary data from PyPi package.
* Delete archive after downloading data
* Use updated cymem, preshed and thinc packages
* Fix information loss in deserialize
* Fix ``__str__`` methods for Python2

2015-10-23 `v0.97 <../../releases/tag/0.97>`_: *Load the StringStore from a json list, instead of a text file*
--------------------------------------------------------------------------------------------------------------

* Fix bugs in download.py
* Require ``--force`` to over-write the data directory in download.py
* Fix bugs in ``Matcher`` and ``doc.merge()``

2015-10-19 `v0.96 <../../releases/tag/0.96>`_: *Hotfix to .merge method*
------------------------------------------------------------------------

* Fix bug that caused text to be lost after ``.merge``
* Fix bug in Matcher when matched entities overlapped

2015-10-18 `v0.95 <../../releases/tag/0.95>`_: *Bugfixes*
---------------------------------------------------------

* Reform encoding of symbols
* Fix bugs in ``Matcher``
* Fix bugs in ``Span``
* Add tokenizer rule to fix numeric range tokenization
* Add specific string-length cap in Tokenizer
* Fix ``token.conjuncts```

2015-10-09 `v0.94 <../../releases/tag/0.94>`_
---------------------------------------------

* Fix memory error that caused crashes on 32bit platforms
* Fix parse errors caused by smart quotes and em-dashes

2015-09-22 `v0.93 <../../releases/tag/0.93>`_
---------------------------------------------

Bug fixes to word vectors
