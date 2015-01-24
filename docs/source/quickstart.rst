Quick Start
===========


Install
-------

.. py:currentmodule:: spacy

.. code:: bash

    $ pip install spacy
    $ python -m spacy.en.download

The download command fetches and installs about 200mb of data, which it installs
within the spacy.en package directory.

Usage
-----

The main entry-point is :meth:`en.English.__call__`, which accepts a unicode string
as an argument, and returns a :py:class:`tokens.Tokens` object.  You can
iterate over it to get :py:class:`tokens.Token` objects, which provide
a convenient API:

    >>> from spacy.en import English
    >>> nlp = English()
    >>> tokens = nlp(u'I ate the pizza with anchovies.')
    >>> pizza = tokens[3]
    >>> (pizza.orth, pizza.orth_, pizza.head.lemma, pizza.head.lemma_)
    ... (14702, u'pizza', 14702, u'ate')

spaCy maps all strings to sequential integer IDs --- a common idiom in NLP.
If an attribute `Token.foo` is an integer ID, then `Token.foo_` is the string,
e.g. `pizza.orth_` and `pizza.orth` provide the integer ID and the string of
the original orthographic form of the word, with no string normalizations
applied.

  .. note::  en.English.__call__ is stateful --- it has an important **side-effect**.

    When it processes a previously unseen word, it increments the ID counter,
    assigns the ID to the string, and writes the mapping in
    :py:data:`English.vocab.strings` (instance of
    :py:class:`strings.StringStore`).
    Future releases will feature a way to reconcile  mappings, but for now, you
    should only work with one instance of the pipeline at a time.


(Most of the) API at a glance
-----------------------------

**Process the string:**

  .. py:class:: spacy.en.English(self, data_dir=join(dirname(__file__), 'data'))

    .. py:method:: __call__(self, text: unicode, tag=True, parse=False) --> Tokens 

    +-----------------+--------------+--------------+
    | Attribute       | Type         | Its API      |
    +=================+==============+==============+
    | vocab           | Vocab        | __getitem__  |
    +-----------------+--------------+--------------+
    | vocab.strings   | StingStore   | __getitem__  |
    +-----------------+--------------+--------------+
    | tokenizer       | Tokenizer    | __call__     |
    +-----------------+--------------+--------------+
    | tagger          | EnPosTagger  | __call__     |
    +-----------------+--------------+--------------+
    | parser          | GreedyParser | __call__     |
    +-----------------+--------------+--------------+

**Get dict or numpy array:**

    .. py:method:: tokens.Tokens.to_array(self, attr_ids: List[int]) --> ndarray[ndim=2, dtype=long]

    .. py:method:: tokens.Tokens.count_by(self, attr_id: int) --> Dict[int, int]

**Get Token objects**

  .. py:method:: tokens.Tokens.__getitem__(self, i) --> Token

  .. py:method:: tokens.Tokens.__iter__(self) --> Iterator[Token]

**Embedded word representenations**

  .. py:attribute:: tokens.Token.repvec
  
  .. py:attribute:: lexeme.Lexeme.repvec


**Navigate to tree- or string-neighbor tokens**

  .. py:method:: nbor(self, i=1) --> Token

  .. py:method:: child(self, i=1) --> Token

  .. py:method:: sibling(self, i=1) --> Token

  .. py:attribute:: head: Token

  .. py:attribute:: dep: int

**Align to original string**

  .. py:attribute:: string: unicode
    
    Padded with original whitespace.

  .. py:attribute:: length: int

    Length, in unicode code-points. Equal to len(self.orth_).
    
  .. py:attribute:: idx: int

    Starting offset of word in the original string.



Features
--------


**Boolean features**

    >>> lexeme = nlp.vocab[u'Apple']
    >>> lexeme.is_alpha, is_upper
    True, False
    >>> tokens = nlp(u'Apple computers')
    >>> tokens[0].is_alpha, tokens[0].is_upper
    >>> True, False
    >>> from spact.en.attrs import IS_ALPHA, IS_UPPER
    >>> tokens.to_array((IS_ALPHA, IS_UPPER))[0]
    array([1, 0])

  +----------+---------------------------------------------------------------+
  | is_alpha | :py:meth:`str.isalpha`                                        |
  +----------+---------------------------------------------------------------+
  | is_digit | :py:meth:`str.isdigit`                                        |
  +----------+---------------------------------------------------------------+
  | is_lower | :py:meth:`str.islower`                                        |
  +----------+---------------------------------------------------------------+
  | is_title | :py:meth:`str.istitle`                                        |
  +----------+---------------------------------------------------------------+
  | is_upper | :py:meth:`str.isupper`                                        |
  +----------+---------------------------------------------------------------+
  | is_ascii | all(ord(c) < 128 for c in string)                             |
  +----------+---------------------------------------------------------------+
  | is_punct | all(unicodedata.category(c).startswith('P') for c in string)  |
  +----------+---------------------------------------------------------------+
  | like_url | Using various heuristics, does the string resemble a URL?     |
  +----------+---------------------------------------------------------------+
  | like_num | "Two", "10", "1,000", "10.54", "1/2" etc all match            |
  +----------+---------------------------------------------------------------+

**String-transform Features**


  +----------+---------------------------------------------------------------+
  | orth     | The original string, unmodified.                              |
  +----------+---------------------------------------------------------------+
  | lower    | The original string, forced to lower-case                     |
  +----------+---------------------------------------------------------------+
  | norm     | The string after additional normalization                     |
  +----------+---------------------------------------------------------------+
  | shape    | Word shape, e.g. 10 --> dd, Garden --> Xxxx, Hi!5 --> Xx!d    |
  +----------+---------------------------------------------------------------+
  | prefix   | A short slice from the start of the string.                   |
  +----------+---------------------------------------------------------------+
  | suffix   | A short slice from the end of the string.                     |
  +----------+---------------------------------------------------------------+
  | lemma    | The word's lemma, i.e. morphological suffixes removed         |
  +----------+---------------------------------------------------------------+

**Syntactic labels**

  +----------+---------------------------------------------------------------+
  | pos      | The word's part-of-speech, from the Google Universal Tag Set  |
  +----------+---------------------------------------------------------------+
  | tag      | A fine-grained morphosyntactic tag, e.g. VBZ, NNS, etc        |
  +----------+---------------------------------------------------------------+
  | dep      | Dependency type label between word and its head, e.g. subj    |
  +----------+---------------------------------------------------------------+

**Distributional**

  +---------+-----------------------------------------------------------+
  | cluster | Brown cluster ID of the word                              |
  +---------+-----------------------------------------------------------+
  | prob    | Log probability of word, smoothed with Simple Good-Turing |
  +---------+-----------------------------------------------------------+

