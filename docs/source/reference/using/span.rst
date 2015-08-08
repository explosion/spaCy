===============
The Span Object
===============

.. autoclass:: spacy.spans.Span

.. py:class:: Span


  .. py:method:: __getitem__

  .. py:method:: __iter__

  .. py:method:: __len__

  .. py:attribute:: root

    Syntactic head

  .. py:attribute:: lefts

    Tokens that are:

    1. To the left of the span;
    2. Syntactic children of words within the span

    i.e.

    .. code::

      lefts = [span.doc[i] for i in range(0, span.start) if span.doc[i].head in span]

  .. py:attribute:: rights

    Tokens that are:

    1. To the right of the span;
    2. Syntactic children of words within the span

    i.e.

    .. code::

      rights = [span.doc[i] for i in range(span.end, len(span.doc)) if span.doc[i].head in span]

    Tokens that are:

    1. To the right of the span;
    2. Syntactic children of words within the span


  .. py:attribute:: string

  .. py:attribute:: lemma / lemma\_

  .. py:attribute:: label / label\_

  .. py:attribute:: subtree
