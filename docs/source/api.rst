===============
Documentation
===============

Quick Ref
---------

.. class:: spacy.en.__init__.English(self, data_dir=join(dirname(__file__, 'data')))
  :noindex:

  .. method:: __call__(self, unicode text, tag=True, parse=False) --> Tokens 

  +-----------+--------------+--------------+
  | Attribute | Type         | Useful       |
  +===========+==============+==============+
  | strings   | StingStore   | __getitem__  |
  +-----------+--------------+--------------+
  | vocab     | Vocab        | __getitem__  |
  +-----------+--------------+--------------+
  | tokenizer | Tokenizer    | __call__     |
  +-----------+--------------+--------------+
  | tagger    | EnPosTagger  | __call__     |
  +-----------+--------------+--------------+
  | parser    | GreedyParser | __call__     |
  +-----------+--------------+--------------+

.. py:class:: spacy.tokens.Tokens(self, vocab: Vocab, string_length=0)

  .. py:method:: __getitem__(self, i) --> Token

  .. py:method:: __iter__(self) --> Iterator[Token]
  
  .. py:method:: __len__(self) --> int

  .. py:method:: to_array(self, attr_ids: List[int]) --> numpy.ndarray[ndim=2, dtype=int32]

  .. py:method:: count_by(self, attr_id: int) --> Dict[int, int]

  +---------------+-------------+-------------+
  | Attribute     | Type        | Useful      |
  +===============+=============+=============+
  | vocab         | Vocab       | __getitem__ |
  +---------------+-------------+-------------+
  | vocab.strings | StringStore | __getitem__ |
  +---------------+-------------+-------------+

.. py:class:: spacy.tokens.Token(self, parent: Tokens, i: int)

  .. py:method:: __unicode__(self) --> unicode

  .. py:method:: __len__(self) --> int

  .. py:method:: nbor(self, i=1) --> Token
  
  .. py:method:: child(self, i=1) --> Token
  
  .. py:method:: sibling(self, i=1) --> Token

  .. py:attribute:: head: Token
  
  .. py:method:: check_flag(self, attr_id: int) --> bool

  
  +-----------+------+-----------+---------+-----------+-------+
  | Attribute | Type | Attribute | Type    | Attribute | Type  |
  +===========+======+===========+=========+===========+=======+
  | sic       | int  | sic_      | unicode | idx       | int   |
  +-----------+------+-----------+---------+-----------+-------+
  | lemma     | int  | lemma_    | unicode | cluster   | int   |
  +-----------+------+-----------+---------+-----------+-------+
  | norm1     | int  | norm1_    | unicode | length    | int   |
  +-----------+------+-----------+---------+-----------+-------+
  | norm2     | int  | norm2_    | unicode | prob      | float |
  +-----------+------+-----------+---------+-----------+-------+
  | shape     | int  | shape_    | unicode | sentiment | float |
  +-----------+------+-----------+---------+-----------+-------+
  | prefix    | int  | prefix_   | unicode |                   |
  +-----------+------+-----------+---------+-------------------+
  | suffix    | int  | suffix_   | unicode |                   |
  +-----------+------+-----------+---------+-------------------+
  | pos       | int  | pos_      | unicode |                   |
  +-----------+------+-----------+---------+-------------------+
  | fine_pos  | int  | fine_pos_ | unicode |                   |
  +-----------+------+-----------+---------+-------------------+
  | dep_tag   | int  | dep_tag_  | unicode |                   |
  +-----------+------+-----------+---------+-------------------+
  

.. py:class:: spacy.vocab.Vocab(self, data_dir=None, lex_props_getter=None)

  .. py:method:: __len__(self) --> int
  
  .. py:method:: __getitem__(self, id: int) --> unicode
  
  .. py:method:: __getitem__(self, string: unicode) --> int
  
  .. py:method:: __setitem__(self, py_str: unicode, props: Dict[str, int|float]) --> None

  .. py:method:: dump(self, loc: unicode) --> None
  
  .. py:method:: load_lexemes(self, loc: unicode) --> None

  .. py:method:: load_vectors(self, loc: unicode) --> None

.. py:class:: spacy.strings.StringStore(self)

  .. py:method:: __len__(self) --> int

  .. py:method:: __getitem__(self, id: int) --> unicode
  
  .. py:method:: __getitem__(self, string: byts) --> id
  
  .. py:method:: __getitem__(self, string: unicode) --> id

  .. py:method:: dump(self, loc: unicode) --> None

  .. py:method:: load(self, loc: unicode) --> None

.. py:class:: spacy.tokenizer.Tokenizer(self, Vocab vocab, rules, prefix_re, suffix_re, infix_re, pos_tags, tag_names)

  .. py:method:: tokens_from_list(self, List[unicode]) --> spacy.tokens.Tokens

  .. py:method:: __call__(self, string: unicode) --> spacy.tokens.Tokens)

  .. py:attribute:: vocab: spacy.vocab.Vocab

.. py:class:: spacy.en.pos.EnPosTagger(self, strings: spacy.strings.StringStore, data_dir: unicode)

  .. py:method:: __call__(self, tokens: spacy.tokens.Tokens)

  .. py:method:: train(self, tokens: spacy.tokens.Tokens, List[int] golds) --> int

  .. py:method:: load_morph_exceptions(self, exc: Dict[unicode, Dict])

.. py:class:: GreedyParser(self, model_dir: unicode)

  .. py:method:: __call__(self, tokens: spacy.tokens.Tokens) --> None

  .. py:method:: train(self, spacy.tokens.Tokens) --> None



spaCy is designed to easily extend to multiple languages, although presently
only English components are implemented.  The components are organised into
a pipeline in the spacy.en.English class.

Usually, you will only want to create one spacy.en.English object, and pass it
around your application.  It manages the string-to-integers mapping, and you
will usually want only a single mapping for all strings.

English Pipeline
----------------

The spacy.en package exports a single class, English, and several constants,
under spacy.en.defs.

.. autoclass:: spacy.en.English
   :members:  

.. autommodule:: spacy.en.pos
   :members:

.. automodule:: spacy.en.attrs
   :members:
   :undoc-members:


Tokens
------

.. autoclass:: spacy.tokens.Tokens
   :members:

.. autoclass:: spacy.tokens.Token
   :members:

.. autoclass:: spacy.lexeme.Lexeme
   :members:

Lexicon
-------

.. automodule:: spacy.vocab
   :members:

.. automodule:: spacy.strings
   :members: 

Tokenizer
---------

.. automodule:: spacy.tokenizer
   :members:

Parser
------

.. automodule:: spacy.syntax.parser
   :members:

Utility Functions
-----------------

.. automodule:: spacy.orth
   :members:
