===
API
===

.. warning:: The documentation is currently being rewritten.  I started out
  using Sphinx, but I've found it too limiting.

  For now, the docs here are incomplete and may even tell you lies (please
  report the lies).

.. py:currentmodule:: spacy

.. class:: en.English(self, data_dir=join(dirname(__file__, 'data')))
  :noindex:

  .. method:: __call__(self, unicode text, tag=True, parse=False) --> Tokens 

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

.. py:class:: tokens.Tokens(self, vocab: Vocab, string_length=0)

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

.. py:class:: tokens.Token(self, parent: Tokens, i: int)

  .. py:method:: __unicode__(self) --> unicode

  .. py:method:: __len__(self) --> int

  .. py:method:: nbor(self, i=1) --> Token
  
  .. py:method:: child(self, i=1) --> Token
  
  .. py:method:: sibling(self, i=1) --> Token

  .. py:attribute:: head: Token
  
  
  +-----------+------+-----------+---------+-----------+------------------------------------+
  | Attribute | Type | Attribute | Type    | Attribute | Type                               |
  +===========+======+===========+=========+===========+====================================+
  | orth      | int  | orth\_    | unicode | idx       | int                                |
  +-----------+------+-----------+---------+-----------+------------------------------------+
  | lemma     | int  | lemma\_   | unicode | cluster   | int                                |
  +-----------+------+-----------+---------+-----------+------------------------------------+
  | lower     | int  | lower\_   | unicode | length    | int                                |
  +-----------+------+-----------+---------+-----------+------------------------------------+
  | norm      | int  | norm\_    | unicode | prob      | float                              |
  +-----------+------+-----------+---------+-----------+------------------------------------+
  | shape     | int  | shape\_   | unicode | repvec    | ndarray(shape=(300,), dtype=float) |
  +-----------+------+-----------+---------+-----------+------------------------------------+
  | prefix    | int  | prefix\_  | unicode |                                                |
  +-----------+------+-----------+---------+------------------------------------------------+
  | suffix    | int  | suffix\_  | unicode |                                                |
  +-----------+------+-----------+---------+------------------------------------------------+
  | pos       | int  | pos\_     | unicode |                                                |
  +-----------+------+-----------+---------+------------------------------------------------+
  | tag       | int  | tag\_     | unicode |                                                |
  +-----------+------+-----------+---------+------------------------------------------------+
  | dep       | int  | dep\_     | unicode |                                                |
  +-----------+------+-----------+---------+------------------------------------------------+
  

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
