spaCy: Industrial-strength NLP
******************************

spaCy is a library for advanced Natural Language Processing in Python and Cython.
It's built on the very latest research, and was designed from day one to be
used in real products. spaCy comes with
`pre-trained statistical models <https://spacy.io/models>`_ and word
vectors, and currently supports tokenization for **20+ languages**. It features
the **fastest syntactic parser** in the world, convolutional **neural network models**
for tagging, parsing and **named entity recognition** and easy **deep learning**
integration. It's commercial open-source software, released under the MIT license.

💫 **Version 2.0 out now!** `Check out the new features here. <https://spacy.io/usage/v2>`_

.. image:: https://img.shields.io/travis/explosion/spaCy/master.svg?style=flat-square
    :target: https://travis-ci.org/explosion/spaCy
    :alt: Build Status

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

===================  ===
`spaCy 101`_         New to spaCy? Here's everything you need to know!
`Usage Guides`_      How to use spaCy and its features.
`New in v2.0`_       New features, backwards incompatibilities and migration guide.
`API Reference`_     The detailed reference for spaCy's API.
`Models`_            Download statistical language models for spaCy.
`Resources`_         Libraries, extensions, demos, books and courses.
`Changelog`_         Changes and version history.
`Contribute`_        How to contribute to the spaCy project and code base.
===================  ===

.. _spaCy 101: https://spacy.io/usage/spacy-101
.. _New in v2.0: https://spacy.io/usage/v2#migrating
.. _Usage Guides: https://spacy.io/usage/
.. _API Reference: https://spacy.io/api/
.. _Models: https://spacy.io/models
.. _Resources: https://spacy.io/usage/resources
.. _Changelog: https://spacy.io/usage/#changelog
.. _Contribute: https://github.com/explosion/spaCy/blob/master/CONTRIBUTING.md

💬 Where to ask questions
==========================

The spaCy project is maintained by `@honnibal <https://github.com/honnibal>`_
and `@ines <https://github.com/ines>`_. Please understand that we won't be able
to provide individual support via email. We also believe that help is much more
valuable if it's shared publicly, so that more people can benefit from it.

====================== ===
**Bug Reports**        `GitHub Issue Tracker`_
**Usage Questions**    `StackOverflow`_, `Gitter Chat`_, `Reddit User Group`_
**General Discussion** `Gitter Chat`_, `Reddit User Group`_
====================== ===

.. _GitHub Issue Tracker: https://github.com/explosion/spaCy/issues
.. _StackOverflow: http://stackoverflow.com/questions/tagged/spacy
.. _Gitter Chat: https://gitter.im/explosion/spaCy
.. _Reddit User Group: https://www.reddit.com/r/spacynlp

Features
========

* **Fastest syntactic parser** in the world
* **Named entity** recognition
* Non-destructive **tokenization**
* Support for **20+ languages**
* Pre-trained `statistical models <https://spacy.io/models>`_ and word vectors
* Easy **deep learning** integration
* Part-of-speech tagging
* Labelled dependency parsing
* Syntax-driven sentence segmentation
* Built in **visualizers** for syntax and NER
* Convenient string-to-hash mapping
* Export to numpy data arrays
* Efficient binary serialization
* Easy **model packaging** and deployment
* State-of-the-art speed
* Robust, rigorously evaluated accuracy

📖  **For more details, see the** `facts, figures and benchmarks <https://spacy.io/usage/facts-figures>`_.

Install spaCy
=============

For detailed installation instructions, see
the `documentation <https://spacy.io/usage>`_.

==================== ===
**Operating system** macOS / OS X, Linux, Windows (Cygwin, MinGW, Visual Studio)
**Python version**   CPython 2.6, 2.7, 3.3+. Only 64 bit.
**Package managers** `pip`_ (source packages only), `conda`_ (via ``conda-forge``)
==================== ===

.. _pip: https://pypi.python.org/pypi/spacy
.. _conda: https://anaconda.org/conda-forge/spacy

pip
---

Using pip, spaCy releases are currently only available as source packages.

.. code:: bash

    pip install spacy

When using pip it is generally recommended to install packages in a virtual
environment to avoid modifying system state:

.. code:: bash

    venv .env
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

Updating spaCy
--------------

Some updates to spaCy may require downloading new statistical models. If you're
running spaCy v2.0 or higher, you can use the ``validate`` command to check if
your installed models are compatible and if not, print details on how to update
them:

.. code:: bash

    pip install -U spacy
    spacy validate

If you've trained your own models, keep in mind that your training and runtime
inputs must match. After updating spaCy, we recommend **retraining your models**
with the new version.

📖  **For details on upgrading from spaCy 1.x to spaCy 2.x, see the**
`migration guide <https://spacy.io/usage/v2#migrating>`_.

Download models
===============

As of v1.7.0, models for spaCy can be installed as **Python packages**.
This means that they're a component of your application, just like any
other module. Models can be installed using spaCy's ``download`` command,
or manually by pointing pip to a path or URL.

======================= ===
`Available Models`_     Detailed model descriptions, accuracy figures and benchmarks.
`Models Documentation`_ Detailed usage instructions.
======================= ===

.. _Available Models: https://spacy.io/models
.. _Models Documentation: https://spacy.io/docs/usage/models

.. code:: bash

    # out-of-the-box: download best-matching default model
    python -m spacy download en

    # download best-matching version of specific model for your spaCy installation
    python -m spacy download en_core_web_lg

    # pip install .tar.gz archive from path or URL
    pip install /Users/you/en_core_web_sm-2.0.0.tar.gz

Loading and using models
------------------------

To load a model, use ``spacy.load()`` with the model's shortcut link:

.. code:: python

    import spacy
    nlp = spacy.load('en')
    doc = nlp(u'This is a sentence.')

If you've installed a model via pip, you can also ``import`` it directly and
then call its ``load()`` method:

.. code:: python

    import spacy
    import en_core_web_sm

    nlp = en_core_web_.load()
    doc = nlp(u'This is a sentence.')

📖 **For more info and examples, check out the**
`models documentation <https://spacy.io/docs/usage/models>`_.

Support for older versions
--------------------------

If you're using an older version (``v1.6.0`` or below), you can still download
and install the old models from within spaCy using ``python -m spacy.en.download all``
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
You'll need to make sure that you have a development environment consisting of a
Python distribution including header files, a compiler,
`pip <https://pip.pypa.io/en/latest/installing/>`__, `virtualenv <https://virtualenv.pypa.io/>`_
and `git <https://git-scm.com>`_ installed. The compiler part is the trickiest.
How to do that depends on your system. See notes on Ubuntu, OS X and Windows for
details.

.. code:: bash

    # make sure you are using recent pip/virtualenv versions
    python -m pip install -U pip venv
    git clone https://github.com/explosion/spaCy
    cd spaCy

    venv .env
    source .env/bin/activate
    export PYTHONPATH=`pwd`
    pip install -r requirements.txt
    python setup.py build_ext --inplace

Compared to regular install via pip, `requirements.txt <requirements.txt>`_
additionally installs developer dependencies such as Cython. For more details
and instructions, see the documentation on
`compiling spaCy from source <https://spacy.io/usage/#source>`_ and the
`quickstart widget <https://spacy.io/usage/#section-quickstart>`_ to get
the right commands for your platform and Python version.

Instead of the above verbose commands, you can also use the following
`Fabric <http://www.fabfile.org/>`_ commands. All commands assume that your
virtual environment is located in a directory ``.env``. If you're using a
different directory, you can change it via the environment variable ``VENV_DIR``,
for example ``VENV_DIR=".custom-env" fab clean make``.

============= ===
``fab env``   Create virtual environment and delete previous one, if it exists.
``fab make``  Compile the source.
``fab clean`` Remove compiled objects, including the generated C++.
``fab test``  Run basic tests, aborting after first failure.
============= ===

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
    python -m pytest <spacy-directory>
