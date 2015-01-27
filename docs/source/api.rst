===
API
===

.. warning:: The documentation here is currently being rewritten.  If something
  doesn't make sense, the docs might be simply wrong. If so, please report it.


.. autoclass:: spacy.en.English

  +-----------+----------------------------------------+-------------+--------------------------+
  | Attribute | Type                                   | Attr API    | NoteS                    |
  +===========+========================================+=============+==========================+
  | strings   | :py:class:`strings.StringStore`        | __getitem__ | string <-> int  mapping  |
  +-----------+----------------------------------------+-------------+--------------------------+
  | vocab     | :py:class:`vocab.Vocab`                | __getitem__ | Look up Lexeme object    |
  +-----------+----------------------------------------+-------------+--------------------------+
  | tokenizer | :py:class:`tokenizer.Tokenizer`        | __call__    | Get Tokens given unicode |
  +-----------+----------------------------------------+-------------+--------------------------+
  | tagger    | :py:class:`en.pos.EnPosTagger`         | __call__    | Set POS tags on Tokens   |
  +-----------+----------------------------------------+-------------+--------------------------+
  | parser    | :py:class:`syntax.parser.GreedyParser` | __call__    | Set parse on Tokens      |
  +-----------+----------------------------------------+-------------+--------------------------+


  .. automethod:: spacy.en.English.__call__


.. autoclass:: spacy.tokens.Tokens
  :members: 
  
  +---------------+-------------+-------------+
  | Attribute     | Type        | Useful      |
  +===============+=============+=============+
  | vocab         | Vocab       | __getitem__ |
  +---------------+-------------+-------------+
  | vocab.strings | StringStore | __getitem__ |
  +---------------+-------------+-------------+


Internals
  A Tokens instance stores the annotations in a C-array of TokenC structs.
  Each TokenC struct holds a const pointer to a LexemeC struct, which describes
  a vocabulary item.

  The Token objects are built lazily, from this underlying C-data.

  For faster access, the underlying C data can be accessed from Cython.  You
  can also export the data to a numpy array, via Tokens.to_array, if pure Python
  access is required, and you need slightly better performance.  However, this
  is both slower and has a worse API than Cython access.  

.. Once a Token object has been created, it is persisted internally in Tokens._py_tokens.


.. autoclass:: spacy.tokens.Token
  :members:

  +--------------------------------------------------------------------------------+
  | **Context-independent Attributes** (calculated once per orth-value in vocab)   |
  +-----------------+-------------+-----------+------------------------------------+
  | Attribute       | Type        | Attribute | Type                               |
  +=================+=============+===========+====================================+
  | orth/orth\_     | int/unicode | __len__   | int                                |
  +-----------------+-------------+-----------+------------------------------------+
  | lower/lower\_   | int/unicode | cluster   | int                                |
  +-----------------+-------------+-----------+------------------------------------+
  | norm/norm\_     | int/unicode | prob      | float                              |
  +-----------------+-------------+-----------+------------------------------------+
  | shape/shape\_   | int/unicode | repvec    | ndarray(shape=(300,), dtype=float) |
  +-----------------+-------------+-----------+------------------------------------+
  | prefix/prefix\_ | int/unicode |           |                                    |
  +-----------------+-------------+-----------+------------------------------------+
  | suffix/suffix\_ | int/unicode |           |                                    |
  +-----------------+-------------+-----------+------------------------------------+
  | **Context-dependent Attributes** (calculated once per token in input)          |
  +-----------------+-------------+-----------+------------------------------------+
  | Attribute       | Type        | Attribute | Type                               |
  +-----------------+-------------+-----------+------------------------------------+
  | whitespace\_    | unicode     | string    | unicode                            |
  +-----------------+-------------+-----------+------------------------------------+
  | pos/pos\_       | int/unicode | dep/dep\_ | int/unicode                        |
  +-----------------+-------------+-----------+------------------------------------+
  | tag/tag\_       | int/unicode |           |                                    |
  +-----------------+-------------+-----------+------------------------------------+
  | lemma/lemma\_   | int/unicode |           |                                    |
  +-----------------+-------------+-----------+------------------------------------+
  

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

.. py:class:: tokenizer.Tokenizer(self, Vocab vocab, rules, prefix_re, suffix_re, infix_re, pos_tags, tag_names)

  .. py:method:: tokens_from_list(self, List[unicode]) --> spacy.tokens.Tokens

  .. py:method:: __call__(self, string: unicode) --> spacy.tokens.Tokens)

  .. py:attribute:: vocab: spacy.vocab.Vocab

.. py:class:: en.pos.EnPosTagger(self, strings: spacy.strings.StringStore, data_dir: unicode)

  .. py:method:: __call__(self, tokens: spacy.tokens.Tokens)

  .. py:method:: train(self, tokens: spacy.tokens.Tokens, List[int] golds) --> int

  .. py:method:: load_morph_exceptions(self, exc: Dict[unicode, Dict])

.. py:class:: syntax.parser.GreedyParser(self, model_dir: unicode)

  .. py:method:: __call__(self, tokens: spacy.tokens.Tokens) --> None

  .. py:method:: train(self, spacy.tokens.Tokens) --> None
