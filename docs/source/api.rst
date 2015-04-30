===
API
===


.. autoclass:: spacy.en.English

  +------------+----------------------------------------+-------------+--------------------------+
  | Attribute  | Type                                   | Attr API    | Notes                    |
  +============+========================================+=============+==========================+
  | strings    | :py:class:`strings.StringStore`        | __getitem__ | string <-> int  mapping  |
  +------------+----------------------------------------+-------------+--------------------------+
  | vocab      | :py:class:`vocab.Vocab`                | __getitem__ | Look up Lexeme object    |
  +------------+----------------------------------------+-------------+--------------------------+
  | tokenizer  | :py:class:`tokenizer.Tokenizer`        | __call__    | Get Tokens given unicode |
  +------------+----------------------------------------+-------------+--------------------------+
  | tagger     | :py:class:`en.pos.EnPosTagger`         | __call__    | Set POS tags on Tokens   |
  +------------+----------------------------------------+-------------+--------------------------+
  | parser     | :py:class:`syntax.parser.GreedyParser` | __call__    | Set parse on Tokens      |
  +------------+----------------------------------------+-------------+--------------------------+
  | entity     | :py:class:`syntax.parser.GreedyParser` | __call__    | Set entities on Tokens   |
  +------------+----------------------------------------+-------------+--------------------------+
  | mwe_merger | :py:class:`multi_words.RegexMerger`    | __call__    | Apply regex for units    |
  +------------+----------------------------------------+-------------+--------------------------+


  .. automethod:: spacy.en.English.__call__


.. autoclass:: spacy.tokens.Tokens

  +---------------+-------------+-------------+
  | Attribute     | Type        | Attr API    |
  +===============+=============+=============+
  | vocab         | Vocab       | __getitem__ |
  +---------------+-------------+-------------+
  | vocab.strings | StringStore | __getitem__ |
  +---------------+-------------+-------------+


  Internals
    A Tokens instance stores the annotations in a C-array of `TokenC` structs.
    Each TokenC struct holds a const pointer to a LexemeC struct, which describes
    a vocabulary item.

    The Token objects are built lazily, from this underlying C-data.

    For faster access, the underlying C data can be accessed from Cython.  You
    can also export the data to a numpy array, via `Tokens.to_array`, if pure Python
    access is required, and you need slightly better performance.  However, this
    is both slower and has a worse API than Cython access.


.. autoclass:: spacy.tokens.Token

  Integer IDs are provided for all string features.  The (unicode) string is
  provided by an attribute of the same name followed by an underscore, e.g.
  token.orth is an integer ID, token.orth\_ is the unicode value.

  The only exception is the Token.string attribute, which is (unicode)
  string-typed.

  +--------------------------------------------------------------------------------+
  | **Context-independent Attributes** (calculated once per entry in vocab)        |
  +-----------------+-------------+-----------+------------------------------------+
  | Attribute       | Type        | Attribute | Type                               |
  +-----------------+-------------+-----------+------------------------------------+
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

  **String Features**

  string
    The form of the word as it appears in the string, include trailing
    whitespace.  This is useful when you need to use linguistic features to
    add inline mark-up to the string.

  orth
    The form of the word with no string normalization or processing, as it
    appears in the string, without trailing whitespace.

  lemma
    The "base" of the word, with no inflectional suffixes, e.g. the lemma of
    "developing" is "develop", the lemma of "geese" is "goose", etc.  Note that
    *derivational* suffixes are not stripped, e.g. the lemma of "instutitions"
    is "institution", not "institute".  Lemmatization is performed using the
    WordNet data, but extended to also cover closed-class words such as
    pronouns.  By default, the WN lemmatizer returns "hi" as the lemma of "his".
    We assign pronouns the lemma -PRON-.

  lower
    The form of the word, but forced to lower-case, i.e. lower = word.orth\_.lower()

  norm
    The form of the word, after language-specific normalizations have been
    applied.

  shape
    A transform of the word's string, to show orthographic features.  The
    characters a-z are mapped to x, A-Z is mapped to X, 0-9 is mapped to d.
    After these mappings, sequences of 4 or more of the same character are
    truncated to length 4.  Examples: C3Po --> XdXx, favorite --> xxxx,
    :) --> :)

  prefix
    A length-N substring from the start of the word.  Length may vary by
    language; currently for English n=1, i.e. prefix = word.orth\_[:1]

  suffix
    A length-N substring from the end of the word.  Length may vary by
    language; currently for English n=3, i.e. suffix = word.orth\_[-3:]

  **Distributional Features**

  prob
    The unigram log-probability of the word, estimated from counts from a
    large corpus, smoothed using Simple Good Turing estimation.

  cluster
    The Brown cluster ID of the word.  These are often useful features for
    linear models.  If you're using a non-linear model, particularly
    a neural net or random forest, consider using the real-valued word
    representation vector, in Token.repvec, instead.

  repvec
    A "word embedding" representation: a dense real-valued vector that supports
    similarity queries between words.  By default, spaCy currently loads
    vectors produced by the Levy and Goldberg (2014) dependency-based word2vec
    model.

  **Syntactic Features**

  tag
    A morphosyntactic tag, e.g. NN, VBZ, DT, etc.  These tags are
    language/corpus specific, and typically describe part-of-speech and some
    amount of morphological information.  For instance, in the Penn Treebank
    tag set, VBZ is assigned to a present-tense singular verb.

  pos
    A part-of-speech tag, from the Google Universal Tag Set, e.g. NOUN, VERB,
    ADV.  Constants for the 17 tag values are provided in spacy.parts\_of\_speech.

  dep
    The type of syntactic dependency relation between the word and its
    syntactic head.

  n_lefts
    The number of immediate syntactic children preceding the word in the
    string.

  n_rights
    The number of immediate syntactic children following the word in the
    string.

  **Navigating the Dependency Tree**

  head
    The Token that is the immediate syntactic head of the word.  If the word is
    the root of the dependency tree, the same word is returned.

  lefts
    An iterator for the immediate leftward syntactic children of the word.

  rights
    An iterator for the immediate rightward syntactic children of the word.

  children
    An iterator that yields from lefts, and then yields from rights.

  subtree
    An iterator for the part of the sentence syntactically governed by the
    word, including the word itself.


  **Named Entities**

  ent_type
    If the token is part of an entity, its entity type

  ent_iob
    The IOB (inside, outside, begin) entity recognition tag for the token

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
