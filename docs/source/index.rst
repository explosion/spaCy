.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================
spaCy: Industrial-strength NLP
==============================

`spaCy`_ is a library for building tomorrow's language technology products.
It's like Stanford's CoreNLP for Python, but with a fundamentally different
objective.  While CoreNLP is primarily built for conducting research, spaCy is
designed for application.

If you're a small company doing NLP, I think spaCy will seem like a minor miracle.
It's by far the fastest NLP software ever released.
The full processing pipeline completes in under 50ms per document, including accurate
tagging, entity recognition and parsing.  All strings are mapped to integer IDs,
tokens are linked to embedded word representations, and a range of useful features
are pre-calculated and cached.  The full analysis can be exported to numpy
arrays, or losslessly serialized into binary data smaller than the raw text.

If none of that made any sense to you, here's the gist of it.  Computers don't
understand text.  This is unfortunate, because that's what the web almost entirely
consists of.  We want to recommend people text based on other text they liked.
We want to shorten text to display it on a mobile screen.  We want to aggregate
it, link it, filter it, categorise it, generate it and correct it.

spaCy provides a library of utility functions that help programmers build such
products.  It's commercial open source software: you can either use it under
the AGPL, or you can `buy a commercial license`_ for a one-time fee.


.. _spaCy: https://github.com/honnibal/spaCy/

.. _Issue Tracker: https://github.com/honnibal/spaCy/issues

**2015-07-08**: `Version 0.89 released`_

.. _Version 0.89 released: updates.html

.. _buy a commercial license: license.html

.. toctree::
    :maxdepth: 4
    :hidden:

    quickstart.rst
    reference/index.rst
    license.rst
    updates.rst
