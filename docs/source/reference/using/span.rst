================
Span Annotations
================

.. autoclass:: spacy.spans.Span

:code:`__getitem__`, :code:`__iter__`, :code:`__len__`
  Sequence API

:code:`head`
  Syntactic head, or None

:code:`left`
  Tokens to the left of the span

:code:`rights`
  Tokens to the left of the span

:code:`orth` / :code:`orth_`
  Orth string

:code:`lemma` / :code:`lemma_`
  Lemma string

:code:`string`
  String

:code:`label` / :code:`label_`
  Label

:code:`subtree`
  Lefts + [self] + Rights
