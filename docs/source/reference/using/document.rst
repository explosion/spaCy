==============
The Doc Object
==============


.. py:class:: spacy.tokens.doc.Doc

  .. py:method:: __init__(self, Vocab vocab, orths_and_spaces=None)

    :param Vocab vocab: A vocabulary object.

    :param list orths_and_spaces=None: Defaults to None.

  .. py:method:: __getitem__(self, int i)
    
    :returns: Token

  .. py:method:: __getitem__(self, slice start_colon_end)

    :returns: Span

  .. py:method:: __iter__(self)

    Iterate over tokens
    
    .. code::

      >>> tokens = nlp(u'Zero one two three four five six')
      >>> tokens[0].orth_
      u'Zero'
      >>> tokens[-1].orth_
      u'six'

  .. py:method:: __len__(self)

    Number of tokens

  .. py:attribute:: sents
  
    Iterate over sentences in the document.

    :returns generator: Sentences

  .. py:attribute:: ents
    
    Iterate over named entities in the document.

    :returns tuple: Named Entities

  .. py:attribute:: noun_chunks

    :returns generator:

  .. py:method:: to_array(self, list attr_ids)

    Given a list of M attribute IDs, export the tokens to a numpy ndarray
    of shape N*M, where N is the length of the sentence.

    :param list[int] attr_ids: A list of attribute ID ints.

    :returns feat_array:
      A feature matrix, with one row per word, and one column per attribute
      indicated in the input attr_ids.

  .. py:method:: count_by(self, attr_id)

    Produce a dict of {attribute (int): count (ints)} frequencies, keyed
    by the values of the given attribute ID.

    .. code::
    
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

  .. py:method:: from_array(self, attrs, array)

  .. py:method:: to_bytes(self)

  .. py:method:: from_bytes(self)

  .. py:method:: read_bytes(self)

  .. py:method:: merge(self, int start_idx, int end_idx, unicode tag, unicode lemma, unicode ent_type)

    Merge a multi-word expression into a single token.  Currently
    experimental; API is likely to change.
