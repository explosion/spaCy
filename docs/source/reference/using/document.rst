===============
Doc Annotations
===============

.. autoclass:: spacy.tokens.Tokens

:code:`__getitem__`, :code:`__iter__`, :code:`__len__`
  The Tokens class behaves as a Python sequence, supporting the usual operators,
  len(), etc.  Negative indexing is supported. Slices are not yet.

  .. code::

    >>> tokens = nlp(u'Zero one two three four five six')
    >>> tokens[0].orth_
    u'Zero'
    >>> tokens[-1].orth_
    u'six'
    >>> tokens[0:4]
    Error

:code:`sents`
  Iterate over sentences in the document.

:code:`ents`
  Iterate over entities in the document.

:code:`to_array`
  Given a list of M attribute IDs, export the tokens to a numpy ndarray
  of shape N*M, where N is the length of the sentence.

    Arguments:
        attr_ids (list[int]): A list of attribute ID ints.

    Returns:
        feat_array (numpy.ndarray[long, ndim=2]):
        A feature matrix, with one row per word, and one column per attribute
        indicated in the input attr_ids.
 
:code:`count_by`
  Produce a dict of {attribute (int): count (ints)} frequencies, keyed
  by the values of the given attribute ID.

    >>> from spacy.en import English, attrs
    >>> nlp = English()
    >>> tokens = nlp(u'apple apple orange banana')
    >>> tokens.count_by(attrs.ORTH)
    {12800L: 1, 11880L: 2, 7561L: 1}
    >>> tokens.to_array([attrs.ORTH])
    array([[11880],
          [11880],
          [ 7561],
          [12800]])

:code:`merge`
  Merge a multi-word expression into a single token.  Currently
  experimental; API is likely to change.



Internals
  A Tokens instance stores the annotations in a C-array of `TokenC` structs.
  Each TokenC struct holds a const pointer to a LexemeC struct, which describes
  a vocabulary item.

  The Token objects are built lazily, from this underlying C-data.

  For faster access, the underlying C data can be accessed from Cython.  You
  can also export the data to a numpy array, via `Tokens.to_array`, if pure Python
  access is required, and you need slightly better performance.  However, this
  is both slower and has a worse API than Cython access.
