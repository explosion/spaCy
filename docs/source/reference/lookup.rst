Lexical Lookup
--------------

Where possible, spaCy computes information over lexical *types*, rather than
*tokens*.  If you process a large batch of text, the number of unique types
you will see will grow exponentially slower than the number of tokens --- so
it's much more efficient to compute over types.  And, in small samples, we generally
want to know about the distribution of a word in the language at large ---
which again, is type-based information.

You can access the lexical features via the Token object, but you can also look them
up in the vocabulary directly:

    >>> from spacy.en import English
    >>> nlp = English()
    >>> lexeme = nlp.vocab[u'Amazon']

.. py:class:: vocab.Vocab(self, data_dir=None, lex_props_getter=None)

  .. py:method:: __len__(self) --> int

  .. py:method:: __getitem__(self, id: int) --> unicode

  .. py:method:: __getitem__(self, string: unicode) --> int

  .. py:method:: __setitem__(self, py_str: unicode, props: Dict[str, int[float]) --> None

  .. py:method:: dump(self, loc: unicode) --> None

  .. py:method:: load_lexemes(self, loc: unicode) --> None

  .. py:method:: load_vectors(self, loc: unicode) --> None


.. py:class:: strings.StringStore(self)

  .. py:method:: __len__(self) --> int

  .. py:method:: __getitem__(self, id: int) --> unicode

  .. py:method:: __getitem__(self, string: bytes) --> id

  .. py:method:: __getitem__(self, string: unicode) --> id

  .. py:method:: dump(self, loc: unicode) --> None

  .. py:method:: load(self, loc: unicode) --> None


