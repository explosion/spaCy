Quick Start
===========


Install
-------

    $ pip install spacy
    $ python -m spacy.en.download

The download command fetches the parser model, which is too big to host on PyPi
(about 100mb).  The data is installed within the spacy.en package.

Usage
-----

The main entry-point is spacy.en.English.__call__, which you use to turn
a unicode string into a Tokens object:

    >>> from spacy.en import English
    >>> nlp = English()
    >>> tokens = nlp(u'A fine, very fine, example sentence')

You shouldn't need to batch up your text or prepare it in any way.
Processing times are linear in the length of the string, with minimal per-call
overhead (apart from the first call, when the tagger and parser are lazy-loaded).

Usually, you will only want to create one instance of the pipeline, and pass it
around.  Each instance maintains its own string-to-id mapping table, so if you
process a new word, it is likely to be assigned different integer IDs by the
two different instances.

The Tokens object has a sequences interface, which you can use to get
individual tokens:

   >>> print tokens[0].lemma
   'a'
   >>> for token in tokens:
   ...   print token.sic, token.pos

For feature extraction, you can select a number of features to export to
a numpy.ndarray:

    >>> from spacy.en import enums
    >>> tokens.to_array([enums.LEMMA, enums.SIC])

Another common operation is to export the embeddings vector to a numpy array:

    >>> tokens.to_vec()

Create a bag-of-words representation:

    >>> tokens.count_by(enums.LEMMA)



(Most of the) API at a glance
-----------------------------

.. py:class:: spacy.en.English(self, data_dir=join(dirname(__file__), 'data'))

  .. py:method:: __call__(self, text: unicode, tag=True, parse=False) --> Tokens 

.. py:class:: spacy.tokens.Tokens via English.__call__

  .. py:method:: __getitem__(self, i) --> Token

  .. py:method:: __iter__(self) --> Iterator[Token]

  .. py:method:: to_array(self, attr_ids: List[int]) --> numpy.ndarray[ndim=2, dtype=int32]

  .. py:method:: count_by(self, attr_id: int) --> Dict[int, int]

.. py:class:: spacy.tokens.Token via Tokens.__iter__, Tokens.__getitem__

  .. py:method:: __unicode__(self) --> unicode

  .. py:method:: __len__(self) --> int

  .. py:method:: nbor(self, i=1) --> Token
  
  .. py:method:: child(self, i=1) --> Token
  
  .. py:method:: sibling(self, i=1) --> Token

  .. py:method:: check_flag(self, attr_id: int) --> bool
  
  

  .. py:attribute:: cluster: int

  .. py:attribute:: string: unicode
  
  .. py:attribute:: string: unicode

  .. py:attribute:: lemma: unicode
  
  .. py:attribute:: dep_tag: unicode
  
  .. py:attribute:: pos: unicode
  
  .. py:attribute:: fine_pos: unicode
  
  .. py:attribute:: sic: unicode
  
  .. py:attribute:: head: Token



