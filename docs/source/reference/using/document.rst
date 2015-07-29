==============
The Doc Object
==============

.. autoclass:: spacy.tokens.Tokens

:code:`__getitem__`, :code:`__iter__`, :code:`__len__`
  The Tokens class behaves as a Python sequence, supporting the usual operators,
  len(), etc.  Negative indexing is supported. Slices are supported as of v0.89

  .. code::

    >>> tokens = nlp(u'Zero one two three four five six')
    >>> tokens[0].orth_
    u'Zero'
    >>> tokens[-1].orth_
    u'six'
    >>> span = tokens[0:4]
    >>> [w.orth_ for w in span]
    [u'Zero', u'one', u'two', u'three']
    >>> span.string
    u'Zero one two three'

:code:`sents`
  Iterate over sentences in the document. Each sentence is a Span object.

:code:`ents`
  Iterate over entities in the document. Each entity is a Span object.

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

:code:`to_bytes()`
  Get a byte-string representation of the document, i.e. serialize.

:code:`from_bytes(self, byte_string)`
  Load data from a byte-string, i.e. deserialize

:code:`Doc.read_bytes`
  A staticmethod, used to read bytes from a file.


Example of serialization:

::

    doc1 = EN(u'This is a simple test. With a couple of sentences.')
    doc2 = EN(u'This is another test document.')

    with open('/tmp/spacy_docs.bin', 'wb') as file_:
        file_.write(doc1.to_bytes())
        file_.write(doc2.to_bytes())

    with open('/tmp/spacy_docs.bin', 'rb') as file_:
        bytes1, bytes2 = Doc.read_bytes(file_)
        r1 = Doc(EN.vocab).from_bytes(bytes1)
        r2 = Doc(EN.vocab).from_bytes(bytes2)

    assert r1.string == doc1.string
    assert r2.string == doc2.string

    
Internals
  A Tokens instance stores the annotations in a C-array of `TokenC` structs.
  Each TokenC struct holds a const pointer to a LexemeC struct, which describes
  a vocabulary item.

  The Token objects are built lazily, from this underlying C-data.

  For faster access, the underlying C data can be accessed from Cython.  You
  can also export the data to a numpy array, via `Tokens.to_array`, if pure Python
  access is required, and you need slightly better performance. 
