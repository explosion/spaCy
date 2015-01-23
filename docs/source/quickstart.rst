Quick Start
===========


Install
-------

.. code:: bash

    $ pip install spacy
    $ python -m spacy.en.download

The download command fetches and installs the parser model and word representations,
which are too big to host on PyPi (about 100mb each).  The data is installed within
the spacy.en package directory.

Usage
-----

The main entry-point is :py:meth:`spacy.en.English.__call__`, which accepts a unicode string as an argument, and returns a :py:class:`spacy.tokens.Tokens` object:

    >>> from spacy.en import English
    >>> nlp = English()
    >>> tokens = nlp(u'A fine, very fine, example sentence', tag=True,
                     parse=True)

Calls to :py:meth:`English.__call__` has a side-effect: when a new
word is seen, it is added to the string-to-ID mapping table in
:py:class:`English.vocab.strings`.  Because of this, you will usually only want
to create one instance of the pipeline.  If you create two instances, and use
them to process different text, you'll probably get different string-to-ID
mappings.  You might choose to wrap the English class as a singleton to ensure
only one instance is created, but I've left that up to you.  I prefer to pass
the instance around as an explicit argument.

You shouldn't need to batch up your text or prepare it in any way.
Processing times are linear in the length of the string, with minimal per-call
overhead (apart from the first call, when the tagger and parser models are
lazy-loaded. This takes a few seconds on my machine.).

:py:meth:`English.__class__` returns a :py:class:`Tokens` object, through which
you'll access the processed text.  You can access the text in three ways:

Iteration
  :py:meth:`Tokens.__iter__` and :py:meth:`Tokens.__getitem__`

  - Most "Pythonic"

  - `spacy.tokens.Token` object, attribute access

  - Inefficient: New Token object created each time.

Export
  :py:meth:`Tokens.count_by` and :py:meth:`Tokens.to_array`

  - `count_by`: Efficient dictionary of counts, for bag-of-words model.

  - `to_array`: Export to numpy array. One row per word, one column per
     attribute.

  - Specify attributes with constants from `spacy.en.attrs`.

Cython
  :py:attr:`TokenC* Tokens.data`

  - Raw data is stored in contiguous array of structs

  - Good syntax, C speed

  - Documentation coming soon. In the meantime, see spacy/syntax/_parser.features.pyx
    or spacy/en/pos.pyx


(Most of the) API at a glance
-----------------------------

.. py:class:: spacy.en.English(self, data_dir=join(dirname(__file__), 'data'))

  .. py:method:: __call__(self, text: unicode, tag=True, parse=False) --> Tokens 

  .. py:method:: vocab.__getitem__(self, text: unicode) --> Lexeme
  
  .. py:method:: vocab.__getitem__(self, text: unicode) --> Lexeme

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


Features
--------

+--------------------------------------------------------------------------+
| Boolean Features                                                         |
+----------+---------------------------------------------------------------+
| IS_ALPHA | :py:meth:`str.isalpha`                                        |
+----------+---------------------------------------------------------------+
| IS_DIGIT | :py:meth:`str.isdigit`                                        |
+----------+---------------------------------------------------------------+
| IS_LOWER | :py:meth:`str.islower`                                        |
+----------+---------------------------------------------------------------+
| IS_SPACE | :py:meth:`str.isspace`                                        |
+----------+---------------------------------------------------------------+
| IS_TITLE | :py:meth:`str.istitle`                                        |
+----------+---------------------------------------------------------------+
| IS_UPPER | :py:meth:`str.isupper`                                        |
+----------+---------------------------------------------------------------+
| IS_ASCII | all(ord(c) < 128 for c in string)                             |
+----------+---------------------------------------------------------------+
| IS_PUNCT | all(unicodedata.category(c).startswith('P') for c in string)  |
+----------+---------------------------------------------------------------+
| LIKE_URL | Using various heuristics, does the string resemble a URL?     |
+----------+---------------------------------------------------------------+
| LIKE_NUM | "Two", "10", "1,000", "10.54", "1/2" etc all match            |
+----------+---------------------------------------------------------------+
| ID of string features                                                    |
+----------+---------------------------------------------------------------+
| SIC      | The original string, unmodified.                              |
+----------+---------------------------------------------------------------+
| NORM1    | The string after level 1 normalization: case, spelling        |
+----------+---------------------------------------------------------------+
| NORM2    | The string after level 2 normalization                        |
+----------+---------------------------------------------------------------+
| SHAPE    | Word shape, e.g. 10 --> dd, Garden --> Xxxx, Hi!5 --> Xx!d    |
+----------+---------------------------------------------------------------+
| PREFIX   | A short slice from the start of the string.                   |
+----------+---------------------------------------------------------------+
| SUFFIX   | A short slice from the end of the string.                     |
+----------+---------------------------------------------------------------+
| CLUSTER  | Brown cluster ID of the word                                  |
+----------+---------------------------------------------------------------+
| LEMMA    | The word's lemma, i.e. morphological suffixes removed         |
+----------+---------------------------------------------------------------+
| TAG      | The word's part-of-speech tag                                 |
+----------+---------------------------------------------------------------+
