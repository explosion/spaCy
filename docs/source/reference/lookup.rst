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

  .. py:method:: __len__(self)

    :returns: number of words in the vocabulary
    :rtype: int

  .. py:method:: __getitem__(self, key_int)

    :param int key:
      Integer ID

    :returns: A Lexeme object

  .. py:method:: __getitem__(self, key_str)

    :param unicode key_str:
      A string in the vocabulary

    :rtype: Lexeme


  .. py:method:: __setitem__(self, orth_str, props)

    :param unicode orth_str:
      The orth key

    :param dict props:
      A props dictionary

    :returns: None

  .. py:method:: dump(self, loc)

    :param unicode loc:
      Path where the vocabulary should be saved

  .. py:method:: load_lexemes(self, loc)

    :param unicode loc:
      Path to load the lexemes.bin file from

  .. py:method:: load_vectors(self, loc)

    :param unicode loc:
      Path to load the vectors.bin from


.. py:class:: strings.StringStore(self)

  .. py:method:: __len__(self)

    :returns:
      Number of strings in the string-store

  .. py:method:: __getitem__(self, key_int)

    :param int key_int: An integer key

    :returns:
      The string that the integer key maps to

      :rtype: unicode

  .. py:method:: __getitem__(self, key_unicode)

    :param int key_unicode:
      A key, as a unicode string

    :returns:
      The integer ID of the string.

    :rtype: int

  .. py:method:: __getitem__(self, key_utf8_bytes)

    :param int key_utf8_bytes:
      A key, as a UTF-8 encoded byte-string

    :returns:
      The integer ID of the string.

    :rtype:
      int

  .. py:method:: dump(self, loc)

    :param loc:
      File path to save the strings.txt to.

  .. py:method:: load(self, loc)

    :param loc:
      File path to load the strings.txt from.
