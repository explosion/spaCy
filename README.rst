spaCy: Industrial-strength NLP
******************************

spaCy is a library for advanced natural language processing in Python and 
Cython. spaCy is built on  the very latest research, but it isn't researchware.  
It was designed from day 1 to be used in real products. It's commercial 
open-source software, released under the MIT license.

💫 **Version 1.5 out now!** `Read the release notes here. <https://github.com/explosion/spaCy/releases/>`_

.. image:: http://i.imgur.com/wFvLZyJ.png
    :target: https://travis-ci.org/explosion/spaCy
    :alt: spaCy on Travis CI
    
.. image:: https://travis-ci.org/explosion/spaCy.svg?branch=master
    :target: https://travis-ci.org/explosion/spaCy
    :alt: Build Status
    
.. image:: https://img.shields.io/github/release/explosion/spacy.svg
    :target: https://github.com/explosion/spaCy/releases   
    :alt: Current Release Version
    
.. image:: https://img.shields.io/pypi/v/spacy.svg   
    :target: https://pypi.python.org/pypi/spacy
    :alt: pypi Version

.. image:: https://badges.gitter.im/spaCy-users.png
    :target: https://gitter.im/explosion/spaCy
    :alt: spaCy on Gitter

📖 Documentation
================

+--------------------------------------------------------------------------------+---------------------------------------------------------+
| `Usage Workflows <https://spacy.io/docs/usage/>`_                              | How to use spaCy and its features.                      |
+--------------------------------------------------------------------------------+---------------------------------------------------------+
| `API Reference <https://spacy.io/docs/api/>`_                                  | The detailed reference for spaCy's API.                 |
+--------------------------------------------------------------------------------+---------------------------------------------------------+
| `Tutorials <https://spacy.io/docs/usage/tutorials>`_                           | End-to-end examples, with code you can modify and run.  |
+--------------------------------------------------------------------------------+---------------------------------------------------------+
| `Showcase & Demos <https://spacy.io/docs/usage/showcase>`_                     | Demos, libraries and products from the spaCy community. |
+--------------------------------------------------------------------------------+---------------------------------------------------------+
| `Contribute <https://github.com/explosion/spaCy/blob/master/CONTRIBUTING.md>`_ | How to contribute to the spaCy project and code base.   |
+--------------------------------------------------------------------------------+---------------------------------------------------------+

💬 Where to ask questions
==========================

+---------------------------+------------------------------------------------------------------------------------------------------------+
| **Bug reports**           | `GitHub Issue tracker <https://github.com/explosion/spaCy/issues>`_                                        |
+---------------------------+------------------------------------------------------------------------------------------------------------+
| **Usage questions**       | `StackOverflow <http://stackoverflow.com/questions/tagged/spacy>`_, `Reddit usergroup                      | 
|                           | <https://www.reddit.com/r/spacynlp>`_, `Gitter chat <https://gitter.im/explosion/spaCy>`_                  |
+---------------------------+------------------------------------------------------------------------------------------------------------+
| **General discussion**    |  `Reddit usergroup <https://www.reddit.com/r/spacynlp>`_,                                                  |
|                           | `Gitter chat <https://gitter.im/explosion/spaCy>`_                                                         |
+---------------------------+------------------------------------------------------------------------------------------------------------+
| **Commercial support**    |  contact@explosion.ai                                                                                      |
+---------------------------+------------------------------------------------------------------------------------------------------------+

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
* Statistical models for **English** and **German**
* State-of-the-art speed
* Robust, rigorously evaluated accuracy

See `facts, figures and benchmarks <https://spacy.io/docs/api/>`_.

Top Performance
==============

* Fastest in the world: <50ms per document.  No faster system has ever been
  announced.
* Accuracy within 1% of the current state of the art on all tasks performed
  (parsing, named entity recognition, part-of-speech tagging).  The only more
  accurate systems are an order of magnitude slower or more.

Supports
========

* CPython 2.6, 2.7, 3.3, 3.4, 3.5 (only 64 bit)
* macOS / OS X
* Linux
* Windows (Cygwin, MinGW, Visual Studio)

Install spaCy
=============

spaCy is compatible with 64-bit CPython 2.6+/3.3+ and runs on Unix/Linux, OS X 
and Windows. Source packages are available via 
`pip <https://pypi.python.org/pypi/spacy>`_. Please make sure that
you have a working build enviroment set up. See notes on Ubuntu, macOS/OS X and Windows
for details.

pip
---

When using pip it is generally recommended to install packages in a virtualenv to
avoid modifying system state:

.. code:: bash

    pip install spacy

Python packaging is awkward at the best of times, and it's particularly tricky with
C extensions, built via Cython, requiring large data files. So, please report issues
as you encounter them.

Install model
=============

After installation you need to download a language model. Currently only models for 
English and German, named ``en`` and ``de``, are available.

.. code:: bash

    python -m spacy.en.download all
    python -m spacy.de.download all

The download command fetches about 1 GB of data which it installs 
within the ``spacy`` package directory.

Upgrading spaCy
===============

To upgrade spaCy to the latest release:

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
    git clone https://github.com/explosion/spaCy.git

    cd spaCy
    virtualenv .env && source .env/bin/activate
    pip install -r requirements.txt
    pip install -e .
    
Compared to regular install via pip `requirements.txt <requirements.txt>`_ 
additionally installs developer dependencies such as cython.

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

Download model to custom location
=================================

You can specify where ``spacy.en.download`` and ``spacy.de.download`` download the language model
to using the ``--data-path`` or ``-d`` argument:

.. code:: bash
    
    python -m spacy.en.download all --data-path /some/dir


If you choose to download to a custom location, you will need to tell spaCy where to load the model
from in order to use it. You can do this either by calling ``spacy.util.set_data_path()`` before
calling ``spacy.load()``, or by passing a ``path`` argument to the ``spacy.en.English`` or
``spacy.de.German`` constructors.

Changelog
=========

2016-12-27 `v1.5.0 <https://github.com/explosion/spaCy/releases>`_: *Alpha support for Swedish and Hungarian*
-------------------------------------------------------------------------------------------------------------

**✨ Major features and improvements**

* **NEW:** Alpha support for Swedish tokenization.
* **NEW:** Alpha support for Hungarian tokenization.
* Update language data for Spanish tokenization.
* Speed up tokenization when no data is preloaded by caching the first 10,000 vocabulary items seen.

**🔴 Bug fixes**

* List the ``language_data`` package in the ``setup.py``.
* Fix missing ``vec_path`` declaration that was failing if ``add_vectors`` was set.
* Allow ``Vocab`` to load without ``serializer_freqs``.

**📖 Documentation and examples**

* **NEW:** `spaCy Jupyter notebooks <https://github.com/explosion/spacy-notebooks>`_ repo: ongoing collection of easy-to-run spaCy examples and tutorials.
* Fix issue `#657 <https://github.com/explosion/spaCy/issues/657>`_: Generalise dependency parsing `annotation specs <https://spacy.io/docs/api/annotation>`_ beyond English.
* Fix various typos and inconsistencies.

**👥  Contributors**

Thanks to `@oroszgy <https://github.com/oroszgy>`_, `@magnusburton <https://github.com/magnusburton>`_, `@jmizgajski <https://github.com/jmizgajski>`_, `@aikramer2 <https://github.com/aikramer2>`_, `@fnorf <https://github.com/fnorf>`_ and `@bhargavvader <https://github.com/bhargavvader>`_ for the pull requests!

2016-12-18 `v1.4.0 <https://github.com/explosion/spaCy/releases/tag/v1.4.0>`_: *Improved language data and alpha Dutch support*
-------------------------------------------------------------------------------------------------------------------------------

**✨ Major features and improvements**

* **NEW:** Alpha support for Dutch tokenization.
* Reorganise and improve format for language data.
* Add shared tag map, entity rules, emoticons and punctuation to language data.
* Convert entity rules, morphological rules and lemmatization rules from JSON to Python.
* Update language data for English, German, Spanish, French, Italian and Portuguese.

**🔴 Bug fixes**

* Fix issue `#649 <https://github.com/explosion/spaCy/issues/649>`_: Update and reorganise stop lists.
* Fix issue `#672 <https://github.com/explosion/spaCy/issues/672>`_: Make ``token.ent_iob_`` return unicode.
* Fix issue `#674 <https://github.com/explosion/spaCy/issues/674>`_: Add missing lemmas for contracted forms of "be" to ``TOKENIZER_EXCEPTIONS``.
* Fix issue `#683 <https://github.com/explosion/spaCy/issues/683>`_ ``Morphology`` class now supplies tag map value for the special space tag if it's missing.
* Fix issue `#684 <https://github.com/explosion/spaCy/issues/684>`_: Ensure ``spacy.en.English()`` loads the Glove vector data if available. Previously was inconsistent with behaviour of ``spacy.load('en')``.
* Fix issue `#685 <https://github.com/explosion/spaCy/issues/685>`_: Expand ``TOKENIZER_EXCEPTIONS`` with unicode apostrophe (``’``).
* Fix issue `#689 <https://github.com/explosion/spaCy/issues/689>`_: Correct typo in ``STOP_WORDS``.
* Fix issue `#691 <https://github.com/explosion/spaCy/issues/691>`_: Add tokenizer exceptions for "gonna" and "Gonna".

**⚠️  Backwards incompatibilities**

No changes to the public, documented API, but the previously undocumented language data and model initialisation processes have been refactored and reorganised. If you were relying on the ``bin/init_model.py`` script, see the new `spaCy Developer Resources <https://github.com/explosion/spacy-dev-resources>`_ repo. Code that references internals of the ``spacy.en`` or ``spacy.de`` packages should also be reviewed before updating to this version.

**📖 Documentation and examples**

* **NEW:** `"Adding languages" <https://spacy.io/docs/usage/adding-languages>`_ workflow.
* **NEW:** `"Part-of-speech tagging" <https://spacy.io/docs/usage/pos-tagging>`_ workflow.
* **NEW:** `spaCy Developer Resources <https://github.com/explosion/spacy-dev-resources>`_ repo – scripts, tools and resources for developing spaCy.
* Fix various typos and inconsistencies.

**👥  Contributors**

Thanks to `@dafnevk <https://github.com/dafnevk>`_, `@jvdzwaan <https://github.com/jvdzwaan>`_, `@RvanNieuwpoort <https://github.com/RvanNieuwpoort>`_, `@wrvhage <https://github.com/wrvhage>`_, `@jaspb <https://github.com/jaspb>`_, `@savvopoulos <https://github.com/savvopoulos>`_ and `@davedwards <https://github.com/davedwards>`_ for the pull requests!

2016-12-03 `v1.3.0 <https://github.com/explosion/spaCy/releases/tag/v1.3.0>`_: *Improve API consistency*
--------------------------------------------------------------------------------------------------------

**✨ API improvements**

* Add ``Span.sentiment`` attribute.
* `#658 <https://github.com/explosion/spaCy/pull/658>`_: Add ``Span.noun_chunks`` iterator (thanks `@pokey <https://github.com/pokey>`_).
* `#642 <https://github.com/explosion/spaCy/pull/642>`_: Let ``--data-path`` be specified when running download.py scripts (thanks `@ExplodingCabbage <https://github.com/ExplodingCabbage>`_).
* `#638 <https://github.com/explosion/spaCy/pull/638>`_: Add German stopwords (thanks `@souravsingh <https://github.com/souravsingh>`_).
* `#614 <https://github.com/explosion/spaCy/pull/614>`_: Fix ``PhraseMatcher`` to work with new ``Matcher`` (thanks `@sadovnychyi <https://github.com/sadovnychyi>`_).

**🔴 Bug fixes**

* Fix issue `#605 <https://github.com/explosion/spaCy/issues/605>`_: ``accept`` argument to ``Matcher`` now rejects matches as expected.
* Fix issue `#617 <https://github.com/explosion/spaCy/issues/617>`_: ``Vocab.load()`` now works with string paths, as well as ``Path`` objects.
* Fix issue `#639 <https://github.com/explosion/spaCy/issues/639>`_: Stop words in ``Language`` class now used as expected.
* Fix issues `#656 <https://github.com/explosion/spaCy/issues/656>`_, `#624 <https://github.com/explosion/spaCy/issues/624>`_: ``Tokenizer`` special-case rules now support arbitrary token attributes.


**📖 Documentation and examples**

* Add `"Customizing the tokenizer" <https://spacy.io/docs/usage/customizing-tokenizer>`_ workflow.
* Add `"Training the tagger, parser and entity recognizer" <https://spacy.io/docs/usage/training>`_ workflow.
* Add `"Entity recognition" <https://spacy.io/docs/usage/entity-recognition>`_ workflow.
* Fix various typos and inconsistencies.

**👥  Contributors**

Thanks to `@pokey <https://github.com/pokey>`_, `@ExplodingCabbage <https://github.com/ExplodingCabbage>`_, `@souravsingh <https://github.com/souravsingh>`_, `@sadovnychyi <https://github.com/sadovnychyi>`_, `@manojsakhwar <https://github.com/manojsakhwar>`_, `@TiagoMRodrigues <https://github.com/TiagoMRodrigues>`_, `@savkov <https://github.com/savkov>`_, `@pspiegelhalter <https://github.com/pspiegelhalter>`_, `@chenb67 <https://github.com/chenb67>`_, `@kylepjohnson <https://github.com/kylepjohnson>`_, `@YanhaoYang <https://github.com/YanhaoYang>`_, `@tjrileywisc <https://github.com/tjrileywisc>`_, `@dechov <https://github.com/dechov>`_, `@wjt <https://github.com/wjt>`_, `@jsmootiv <https://github.com/jsmootiv>`_ and `@blarghmatey <https://github.com/blarghmatey>`_ for the pull requests!

2016-11-04 `v1.2.0 <https://github.com/explosion/spaCy/releases/tag/v1.2.0>`_: *Alpha tokenizers for Chinese, French, Spanish, Italian and Portuguese*
------------------------------------------------------------------------------------------------------------------------------------------------------

**✨ Major features and improvements**

* **NEW:** Support Chinese tokenization, via `Jieba <https://github.com/fxsjy/jieba>`_.
* **NEW:** Alpha support for French, Spanish, Italian and Portuguese tokenization.

**🔴 Bug fixes**

* Fix issue `#376 <https://github.com/explosion/spaCy/issues/376>`_: POS tags for "and/or" are now correct.
* Fix issue `#578 <https://github.com/explosion/spaCy/issues578/>`_: ``--force`` argument on download command now operates correctly.
* Fix issue `#595 <https://github.com/explosion/spaCy/issues/595>`_: Lemmatization corrected for some base forms.
* Fix issue `#588 <https://github.com/explosion/spaCy/issues/588>`_: `Matcher` now rejects empty patterns.
* Fix issue `#592 <https://github.com/explosion/spaCy/issues/592>`_: Added exception rule for tokenization of "Ph.D."
* Fix issue `#599 <https://github.com/explosion/spaCy/issues/599>`_: Empty documents now considered tagged and parsed.
* Fix issue `#600 <https://github.com/explosion/spaCy/issues/600>`_: Add missing ``token.tag`` and ``token.tag_`` setters.
* Fix issue `#596 <https://github.com/explosion/spaCy/issues/596>`_: Added missing unicode import when compiling regexes that led to incorrect tokenization.
* Fix issue `#587 <https://github.com/explosion/spaCy/issues/587>`_: Resolved bug that caused ``Matcher`` to sometimes segfault.
* Fix issue `#429 <https://github.com/explosion/spaCy/issues/429>`_: Ensure missing entity types are added to the entity recognizer.

2016-10-23 `v1.1.0 <https://github.com/explosion/spaCy/releases/tag/v1.1.0>`_: *Bug fixes and adjustments*
----------------------------------------------------------------------------------------------------------

* Rename new ``pipeline`` keyword argument of ``spacy.load()`` to ``create_pipeline``.
* Rename new ``vectors`` keyword argument of ``spacy.load()`` to ``add_vectors``.

**🔴 Bug fixes**

* Fix issue `#544 <https://github.com/explosion/spaCy/issues/544>`_: Add ``vocab.resize_vectors()`` method, to support changing to vectors of different dimensionality.
* Fix issue `#536 <https://github.com/explosion/spaCy/issues/536>`_: Default probability was incorrect for OOV words.
* Fix issue `#539 <https://github.com/explosion/spaCy/issues/539>`_: Unspecified encoding when opening some JSON files.
* Fix issue `#541 <https://github.com/explosion/spaCy/issues/541>`_: GloVe vectors were being loaded incorrectly.
* Fix issue `#522 <https://github.com/explosion/spaCy/issues/522>`_: Similarities and vector norms were calculated incorrectly.
* Fix issue `#461 <https://github.com/explosion/spaCy/issues/461>`_: ``ent_iob`` attribute was incorrect after setting entities via ``doc.ents``
* Fix issue `#459 <https://github.com/explosion/spaCy/issues/459>`_: Deserialiser failed on empty doc
* Fix issue `#514 <https://github.com/explosion/spaCy/issues/514>`_: Serialization failed after adding a new entity label.

2016-10-18 `v1.0.0 <https://github.com/explosion/spaCy/releases/tag/v1.0.0>`_: *Support for deep learning workflows and entity-aware rule matcher*
--------------------------------------------------------------------------------------------------------------------------------------------------

**✨ Major features and improvements**

* **NEW:** `custom processing pipelines <https://spacy.io/docs/usage/customizing-pipeline>`_, to support deep learning workflows
* **NEW:** `Rule matcher <https://spacy.io/docs/usage/rule-based-matching>`_ now supports entity IDs and attributes
* **NEW:** Official/documented `training APIs <https://github.com/explosion/spaCy/tree/master/examples/training>`_ and `GoldParse` class
* Download and use GloVe vectors by default
* Make it easier to load and unload word vectors
* Improved rule matching functionality
* Move basic data into the code, rather than the json files. This makes it simpler to use the tokenizer without the models installed, and makes adding new languages much easier.
* Replace file-system strings with ``Path`` objects. You can now load resources over your network, or do similar trickery, by passing any object that supports the ``Path`` protocol.

**⚠️  Backwards incompatibilities**

* The data_dir keyword argument of ``Language.__init__`` (and its subclasses ``English.__init__`` and ``German.__init__``) has been renamed to ``path``.
* Details of how the Language base-class and its sub-classes are loaded, and how defaults are accessed, have been heavily changed. If you have your own subclasses, you should review the changes.
* The deprecated ``token.repvec`` name has been removed.
* The ``.train()`` method of Tagger and Parser has been renamed to ``.update()``
* The previously undocumented ``GoldParse`` class has a new ``__init__()`` method. The old method has been preserved in ``GoldParse.from_annot_tuples()``.
* Previously undocumented details of the ``Parser`` class have changed.
* The previously undocumented ``get_package`` and ``get_package_by_name`` helper functions have been moved into a new module, ``spacy.deprecated``, in case you still need them while you update.

**🔴  Bug fixes**

* Fix ``get_lang_class`` bug when GloVe vectors are used.
* Fix Issue `#411 <https://github.com/explosion/spaCy/issues/411>`_: ``doc.sents`` raised IndexError on empty string.
* Fix Issue `#455 <https://github.com/explosion/spaCy/issues/455>`_: Correct lemmatization logic
* Fix Issue `#371 <https://github.com/explosion/spaCy/issues/371>`_: Make ``Lexeme`` objects hashable
* Fix Issue `#469 <https://github.com/explosion/spaCy/issues/469>`_: Make ``noun_chunks`` detect root NPs

**👥  Contributors**

Thanks to `@daylen <https://github.com/daylen>`_, `@RahulKulhari <https://github.com/RahulKulhari>`_, `@stared <https://github.com/stared>`_, `@adamhadani <https://github.com/adamhadani>`_, `@izeye <https://github.com/adamhadani>`_ and `@crawfordcomeaux <https://github.com/adamhadani>`_ for the pull requests!

2016-05-10 `v0.101.0 <https://github.com/explosion/spaCy/releases/tag/0.101.0>`_: *Fixed German model*
------------------------------------------------------------------------------------------------------

* Fixed bug that prevented German parses from being deprojectivised.
* Bug fixes to sentence boundary detection.
* Add rich comparison methods to the Lexeme class.
* Add missing ``Doc.has_vector`` and ``Span.has_vector`` properties.
* Add missing ``Span.sent`` property.

2016-05-05 `v0.100.7 <https://github.com/explosion/spaCy/releases/tag/0.100.7>`_: *German!*
-------------------------------------------------------------------------------------------

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

2016-03-08 `v0.100.6 <https://github.com/explosion/spaCy/releases/tag/0.100.6>`_: *Add support for GloVe vectors*
-----------------------------------------------------------------------------------------------------------------

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

2016-02-07 `v0.100.5 <https://github.com/explosion/spaCy/releases/tag/0.100.5>`_
--------------------------------------------------------------------------------

Fix incorrect use of header file, caused from problem with thinc

2016-02-07 `v0.100.4 <https://github.com/explosion/spaCy/releases/tag/0.100.4>`_: *Fix OSX problem introduced in 0.100.3*
-------------------------------------------------------------------------------------------------------------------------

Small correction to right_edge calculation

2016-02-06 `v0.100.3 <https://github.com/explosion/spaCy/releases/tag/0.100.3>`_
--------------------------------------------------------------------------------

Support multi-threading, via the ``.pipe`` method. spaCy now releases the GIL around the
parser and entity recognizer, so systems that support OpenMP should be able to do
shared memory parallelism at close to full efficiency.

We've also greatly reduced loading time, and fixed a number of bugs.

2016-01-21 `v0.100.2 <https://github.com/explosion/spaCy/releases/tag/0.100.2>`_
--------------------------------------------------------------------------------

Fix data version lock that affected v0.100.1

2016-01-21 `v0.100.1 <https://github.com/explosion/spaCy/releases/tag/0.100.1>`_: *Fix install for OSX*
-------------------------------------------------------------------------------------------------------

v0.100 included header files built on Linux that caused installation to fail on OSX.
This should now be corrected. We also update the default data distribution, to
include a small fix to the tokenizer.

2016-01-19 `v0.100 <https://github.com/explosion/spaCy/releases/tag/0.100>`_: *Revise setup.py, better model downloads, bug fixes*
----------------------------------------------------------------------------------------------------------------------------------

* Redo setup.py, and remove ugly headers_workaround hack. Should result in fewer install problems.
* Update data downloading and installation functionality, by migrating to the Sputnik data-package manager. This will allow us to offer finer grained control of data installation in future.
* Fix bug when using custom entity types in ``Matcher``. This should work by default when using the
  ``English.__call__`` method of running the pipeline. If invoking ``Parser.__call__`` directly to do NER,
  you should call the ``Parser.add_label()`` method to register your entity type.
* Fix head-finding rules in ``Span``.
* Fix problem that caused ``doc.merge()`` to sometimes hang
* Fix problems in handling of whitespace

2015-11-08 `v0.99 <https://github.com/explosion/spaCy/releases/tag/0.99>`_: *Improve span merging, internal refactoring*
------------------------------------------------------------------------------------------------------------------------

* Merging multi-word tokens into one, via the ``doc.merge()`` and ``span.merge()`` methods, no longer invalidates existing ``Span`` objects. This makes it much easier to merge multiple spans, e.g. to merge all named entities, or all base noun phrases. Thanks to @andreasgrv for help on this patch.
* Lots of internal refactoring, especially around the machine learning module, thinc. The thinc API has now been improved, and the spacy._ml wrapper module is no longer necessary.
* The lemmatizer now lower-cases non-noun, noun-verb and non-adjective words.
* A new attribute, ``.rank``, is added to Token and Lexeme objects, giving the frequency rank of the word.

2015-11-03 `v0.98 <https://github.com/explosion/spaCy/releases/tag/0.98>`_: *Smaller package, bug fixes*
---------------------------------------------------------------------------------------------------------

* Remove binary data from PyPi package.
* Delete archive after downloading data
* Use updated cymem, preshed and thinc packages
* Fix information loss in deserialize
* Fix ``__str__`` methods for Python2

2015-10-23 `v0.97 <https://github.com/explosion/spaCy/releases/tag/0.97>`_: *Load the StringStore from a json list, instead of a text file*
-------------------------------------------------------------------------------------------------------------------------------------------

* Fix bugs in download.py
* Require ``--force`` to over-write the data directory in download.py
* Fix bugs in ``Matcher`` and ``doc.merge()``

2015-10-19 `v0.96 <https://github.com/explosion/spaCy/releases/tag/0.96>`_: *Hotfix to .merge method*
-----------------------------------------------------------------------------------------------------

* Fix bug that caused text to be lost after ``.merge``
* Fix bug in Matcher when matched entities overlapped

2015-10-18 `v0.95 <https://github.com/explosion/spaCy/releases/tag/0.95>`_: *Bugfixes*
--------------------------------------------------------------------------------------

* Reform encoding of symbols
* Fix bugs in ``Matcher``
* Fix bugs in ``Span``
* Add tokenizer rule to fix numeric range tokenization
* Add specific string-length cap in Tokenizer
* Fix ``token.conjuncts``

2015-10-09 `v0.94 <https://github.com/explosion/spaCy/releases/tag/0.94>`_
--------------------------------------------------------------------------

* Fix memory error that caused crashes on 32bit platforms
* Fix parse errors caused by smart quotes and em-dashes

2015-09-22 `v0.93 <https://github.com/explosion/spaCy/releases/tag/0.93>`_
--------------------------------------------------------------------------

Bug fixes to word vectors
