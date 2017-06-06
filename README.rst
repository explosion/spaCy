spaCy: Industrial-strength NLP
******************************

spaCy is a library for advanced natural language processing in Python and
Cython. spaCy is built on  the very latest research, but it isn't researchware.
It was designed from day one to be used in real products. spaCy currently supports
English, German, French and Spanish, as well as tokenization for Italian,
Portuguese, Dutch, Swedish, Finnish, Norwegian, Hungarian, Bengali, Hebrew,
Chinese and Japanese. It's commercial open-source software, released under the
MIT license.

⭐️ **Test spaCy v2.0.0 alpha and the new models!** `Read the release notes here. <https://github.com/explosion/spaCy/releases/tag/v2.0.0-alpha>`_

💫 **Version 1.8 out now!** `Read the release notes here. <https://github.com/explosion/spaCy/releases/>`_

.. image:: https://img.shields.io/travis/explosion/spaCy/master.svg?style=flat-square
    :target: https://travis-ci.org/explosion/spaCy
    :alt: Travis Build Status
    
.. image:: https://img.shields.io/appveyor/ci/explosion/spacy/master.svg?style=flat-square
    :target: https://ci.appveyor.com/project/explosion/spacy
    :alt: Appveyor Build Status

.. image:: https://img.shields.io/github/release/explosion/spacy.svg?style=flat-square
    :target: https://github.com/explosion/spaCy/releases
    :alt: Current Release Version

.. image:: https://img.shields.io/pypi/v/spacy.svg?style=flat-square
    :target: https://pypi.python.org/pypi/spacy
    :alt: pypi Version

.. image:: https://anaconda.org/conda-forge/spacy/badges/version.svg
    :target: https://anaconda.org/conda-forge/spacy
    :alt: conda Version

.. image:: https://img.shields.io/badge/gitter-join%20chat%20%E2%86%92-09a3d5.svg?style=flat-square
    :target: https://gitter.im/explosion/spaCy
    :alt: spaCy on Gitter

.. image:: https://img.shields.io/twitter/follow/spacy_io.svg?style=social&label=Follow
    :target: https://twitter.com/spacy_io
    :alt: spaCy on Twitter

📖 Documentation
================

=================== ===
`Usage Workflows`_  How to use spaCy and its features.
`API Reference`_    The detailed reference for spaCy's API.
`Troubleshooting`_  Common problems and solutions for beginners.
`Tutorials`_        End-to-end examples, with code you can modify and run.
`Showcase & Demos`_ Demos, libraries and products from the spaCy community.
`Contribute`_       How to contribute to the spaCy project and code base.
=================== ===

.. _Usage Workflows: https://spacy.io/docs/usage/
.. _API Reference: https://spacy.io/docs/api/
.. _Troubleshooting: https://spacy.io/docs/usage/troubleshooting
.. _Tutorials: https://spacy.io/docs/usage/tutorials
.. _Showcase & Demos: https://spacy.io/docs/usage/showcase
.. _Contribute: https://github.com/explosion/spaCy/blob/master/CONTRIBUTING.md

💬 Where to ask questions
==========================

====================== ===
**Bug reports**        `GitHub issue tracker`_
**Usage questions**    `StackOverflow`_, `Gitter chat`_, `Reddit user group`_
**General discussion** `Gitter chat`_, `Reddit user group`_
**Commercial support** contact@explosion.ai
====================== ===

.. _GitHub issue tracker: https://github.com/explosion/spaCy/issues
.. _StackOverflow: http://stackoverflow.com/questions/tagged/spacy
.. _Gitter chat: https://gitter.im/explosion/spaCy
.. _Reddit user group: https://www.reddit.com/r/spacynlp

Features
========

* Non-destructive **tokenization**
* Syntax-driven sentence segmentation
* Pre-trained **word vectors**
* Part-of-speech tagging
* **Named entity** recognition
* Labelled dependency parsing
* Convenient string-to-int mapping
* Export to numpy data arrays
* GIL-free **multi-threading**
* Efficient binary serialization
* Easy **deep learning** integration
* Statistical models for **English**, **German**, **French** and **Spanish**
* State-of-the-art speed
* Robust, rigorously evaluated accuracy

See `facts, figures and benchmarks <https://spacy.io/docs/api/>`_.

Top Performance
---------------

* Fastest in the world: <50ms per document.  No faster system has ever been
  announced.
* Accuracy within 1% of the current state of the art on all tasks performed
  (parsing, named entity recognition, part-of-speech tagging).  The only more
  accurate systems are an order of magnitude slower or more.

Supports
--------

==================== ===
**Operating system** macOS / OS X, Linux, Windows (Cygwin, MinGW, Visual Studio)
**Python version**   CPython 2.6, 2.7, 3.3+. Only 64 bit.
**Package managers** `pip`_ (source packages only), `conda`_ (via ``conda-forge``)
==================== ===

.. _pip: https://pypi.python.org/pypi/spacy
.. _conda: https://anaconda.org/conda-forge/spacy

Install spaCy
=============

Installation requires a working build environment. See notes on Ubuntu,
macOS/OS X and Windows for details.

pip
---

Using pip, spaCy releases are currently only available as source packages.

.. code:: bash

    pip install -U spacy

When using pip it is generally recommended to install packages in a ``virtualenv``
to avoid modifying system state:

.. code:: bash

    virtualenv .env
    source .env/bin/activate
    pip install spacy

conda
-----

Thanks to our great community, we've finally re-added conda support. You can now
install spaCy via ``conda-forge``:

.. code:: bash

    conda config --add channels conda-forge
    conda install spacy

For the feedstock including the build recipe and configuration,
check out `this repository <https://github.com/conda-forge/spacy-feedstock>`_.
Improvements and pull requests to the recipe and setup are always appreciated.

Download models
===============

As of v1.7.0, models for spaCy can be installed as **Python packages**.
This means that they're a component of your application, just like any
other module. They're versioned and can be defined as a dependency in your
``requirements.txt``. Models can be installed from a download URL or
a local directory, manually or via pip. Their data can be located anywhere on
your file system. To make a model available to spaCy, all you need to do is
create a "shortcut link", an internal alias that tells spaCy where to find the
data files for a specific model name.

======================= ===
`spaCy Models`_         Available models, latest releases and direct download.
`Models Documentation`_ Detailed usage instructions.
======================= ===

.. _spaCy Models: https://github.com/explosion/spacy-models/releases/
.. _Models Documentation: https://spacy.io/docs/usage/models

.. code:: bash

    # out-of-the-box: download best-matching default model
    python -m spacy download en

    # download best-matching version of specific model for your spaCy installation
    python -m spacy download en_core_web_md

    # pip install .tar.gz archive from path or URL
    pip install /Users/you/en_core_web_md-1.2.0.tar.gz
    pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-1.2.0/en_core_web_md-1.2.0.tar.gz

    # set up shortcut link to load installed package as "en_default"
    python -m spacy link en_core_web_md en_default

    # set up shortcut link to load local model as "my_amazing_model"
    python -m spacy link /Users/you/data my_amazing_model

Loading and using models
------------------------

To load a model, use ``spacy.load()`` with the model's shortcut link:

.. code:: python

    import spacy
    nlp = spacy.load('en_default')
    doc = nlp(u'This is a sentence.')

If you've installed a model via pip, you can also ``import`` it directly and
then call its ``load()`` method with no arguments. This should also work for
older models in previous versions of spaCy.

.. code:: python

    import spacy
    import en_core_web_md

    nlp = en_core_web_md.load()
    doc = nlp(u'This is a sentence.')

📖 **For more info and examples, check out the** `models documentation <https://spacy.io/docs/usage/models>`_.

Support for older versions
--------------------------

If you're using an older version (v1.6.0 or below), you can still download and
install the old models from within spaCy using ``python -m spacy.en.download all``
or ``python -m spacy.de.download all``. The ``.tar.gz`` archives are also
`attached to the v1.6.0 release <https://github.com/explosion/spaCy/tree/v1.6.0>`_.
To download and install the models manually, unpack the archive, drop the
contained directory into ``spacy/data`` and load the model via ``spacy.load('en')``
or ``spacy.load('de')``.

Compile from source
===================

The other way to install spaCy is to clone its
`GitHub repository <https://github.com/explosion/spaCy>`_ and build it from
source. That is the common way if you want to make changes to the code base.
You'll need to make sure that you have a development enviroment consisting of a
Python distribution including header files, a compiler,
`pip <https://pip.pypa.io/en/latest/installing/>`__, `virtualenv <https://virtualenv.pypa.io/>`_
and `git <https://git-scm.com>`_ installed. The compiler part is the trickiest.
How to do that depends on your system. See notes on Ubuntu, OS X and Windows for
details.

.. code:: bash

    # make sure you are using recent pip/virtualenv versions
    python -m pip install -U pip virtualenv
    git clone https://github.com/explosion/spaCy
    cd spaCy

    virtualenv .env
    source .env/bin/activate
    pip install -r requirements.txt
    pip install -e .

Compared to regular install via pip `requirements.txt <requirements.txt>`_
additionally installs developer dependencies such as Cython.

Instead of the above verbose commands, you can also use the following
`Fabric <http://www.fabfile.org/>`_ commands:

============= ===
``fab env``   Create ``virtualenv`` and delete previous one, if it exists.
``fab make``  Compile the source.
``fab clean`` Remove compiled objects, including the generated C++.
``fab test``  Run basic tests, aborting after first failure.
============= ===

All commands assume that your ``virtualenv`` is located in a directory ``.env``.
If you're using a different directory, you can change it via the environment
variable ``VENV_DIR``, for example:

.. code:: bash

    VENV_DIR=".custom-env" fab clean make

Ubuntu
------

Install system-level dependencies via ``apt-get``:

.. code:: bash

    sudo apt-get install build-essential python-dev git

macOS / OS X
------------

Install a recent version of `XCode <https://developer.apple.com/xcode/>`_,
including the so-called "Command Line Tools". macOS and OS X ship with Python
and git preinstalled.

Windows
-------

Install a version of `Visual Studio Express <https://www.visualstudio.com/vs/visual-studio-express/>`_
or higher that matches the version that was used to compile your Python
interpreter. For official distributions these are VS 2008 (Python 2.7),
VS 2010 (Python 3.4) and VS 2015 (Python 3.5).

Run tests
=========

spaCy comes with an `extensive test suite <spacy/tests>`_. First, find out where
spaCy is installed:

.. code:: bash

    python -c "import os; import spacy; print(os.path.dirname(spacy.__file__))"

Then run ``pytest`` on that directory. The flags ``--vectors``, ``--slow``
and ``--model`` are optional and enable additional tests:

.. code:: bash

    # make sure you are using recent pytest version
    python -m pip install -U pytest

    python -m pytest <spacy-directory> --vectors --models --slow

🛠 Changelog
============

=========== ============== ===========
Version     Date           Description
=========== ============== ===========
`v1.8.2`_   ``2017-04-26`` French model and small improvements
`v1.8.1`_   ``2017-04-23`` Saving, loading and training bug fixes
`v1.8.0`_   ``2017-04-16`` Better NER training, saving and loading
`v1.7.5`_   ``2017-04-07`` Bug fixes and new CLI commands
`v1.7.3`_   ``2017-03-26`` Alpha support for Hebrew, new CLI commands and bug fixes
`v1.7.2`_   ``2017-03-20`` Small fixes to beam parser and model linking
`v1.7.1`_   ``2017-03-19`` Fix data download for system installation
`v1.7.0`_   ``2017-03-18`` New 50 MB model, CLI, better downloads and lots of bug fixes
`v1.6.0`_   ``2017-01-16`` Improvements to tokenizer and tests
`v1.5.0`_   ``2016-12-27`` Alpha support for Swedish and Hungarian
`v1.4.0`_   ``2016-12-18`` Improved language data and alpha Dutch support
`v1.3.0`_   ``2016-12-03`` Improve API consistency
`v1.2.0`_   ``2016-11-04`` Alpha tokenizers for Chinese, French, Spanish, Italian and Portuguese
`v1.1.0`_   ``2016-10-23`` Bug fixes and adjustments
`v1.0.0`_   ``2016-10-18`` Support for deep learning workflows and entity-aware rule matcher
`v0.101.0`_ ``2016-05-10`` Fixed German model
`v0.100.7`_ ``2016-05-05`` German support
`v0.100.6`_ ``2016-03-08`` Add support for GloVe vectors
`v0.100.5`_ ``2016-02-07`` Fix incorrect use of header file
`v0.100.4`_ ``2016-02-07`` Fix OSX problem introduced in 0.100.3
`v0.100.3`_ ``2016-02-06`` Multi-threading, faster loading and bugfixes
`v0.100.2`_ ``2016-01-21`` Fix data version lock
`v0.100.1`_ ``2016-01-21`` Fix install for OSX
`v0.100`_   ``2016-01-19`` Revise setup.py, better model downloads, bug fixes
`v0.99`_    ``2015-11-08`` Improve span merging, internal refactoring
`v0.98`_    ``2015-11-03`` Smaller package, bug fixes
`v0.97`_    ``2015-10-23`` Load the StringStore from a json list, instead of a text file
`v0.96`_    ``2015-10-19`` Hotfix to .merge method
`v0.95`_    ``2015-10-18`` Bug fixes
`v0.94`_    ``2015-10-09`` Fix memory and parse errors
`v0.93`_    ``2015-09-22`` Bug fixes to word vectors
=========== ============== ===========

.. _v1.8.2: https://github.com/explosion/spaCy/releases/tag/v1.8.2
.. _v1.8.1: https://github.com/explosion/spaCy/releases/tag/v1.8.1
.. _v1.8.0: https://github.com/explosion/spaCy/releases/tag/v1.8.0
.. _v1.7.5: https://github.com/explosion/spaCy/releases/tag/v1.7.5
.. _v1.7.3: https://github.com/explosion/spaCy/releases/tag/v1.7.3
.. _v1.7.2: https://github.com/explosion/spaCy/releases/tag/v1.7.2
.. _v1.7.1: https://github.com/explosion/spaCy/releases/tag/v1.7.1
.. _v1.7.0: https://github.com/explosion/spaCy/releases/tag/v1.7.0
.. _v1.6.0: https://github.com/explosion/spaCy/releases/tag/v1.6.0
.. _v1.5.0: https://github.com/explosion/spaCy/releases/tag/v1.5.0
.. _v1.4.0: https://github.com/explosion/spaCy/releases/tag/v1.4.0
.. _v1.3.0: https://github.com/explosion/spaCy/releases/tag/v1.3.0
.. _v1.2.0: https://github.com/explosion/spaCy/releases/tag/v1.2.0
.. _v1.1.0: https://github.com/explosion/spaCy/releases/tag/v1.1.0
.. _v1.0.0: https://github.com/explosion/spaCy/releases/tag/v1.0.0
.. _v0.101.0: https://github.com/explosion/spaCy/releases/tag/0.101.0
.. _v0.100.7: https://github.com/explosion/spaCy/releases/tag/0.100.7
.. _v0.100.6: https://github.com/explosion/spaCy/releases/tag/0.100.6
.. _v0.100.5: https://github.com/explosion/spaCy/releases/tag/0.100.5
.. _v0.100.4: https://github.com/explosion/spaCy/releases/tag/0.100.4
.. _v0.100.3: https://github.com/explosion/spaCy/releases/tag/0.100.3
.. _v0.100.2: https://github.com/explosion/spaCy/releases/tag/0.100.2
.. _v0.100.1: https://github.com/explosion/spaCy/releases/tag/0.100.1
.. _v0.100: https://github.com/explosion/spaCy/releases/tag/0.100
.. _v0.99: https://github.com/explosion/spaCy/releases/tag/0.99
.. _v0.98: https://github.com/explosion/spaCy/releases/tag/0.98
.. _v0.97: https://github.com/explosion/spaCy/releases/tag/0.97
.. _v0.96: https://github.com/explosion/spaCy/releases/tag/0.96
.. _v0.95: https://github.com/explosion/spaCy/releases/tag/0.95
.. _v0.94: https://github.com/explosion/spaCy/releases/tag/0.94
.. _v0.93: https://github.com/explosion/spaCy/releases/tag/0.93
