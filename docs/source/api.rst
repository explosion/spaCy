=========
Reference
=========

Overview
--------

spaCy is a suite of natural language processing tools, arranged into
a pipeline.  It is substantially more opinionated than most similar libraries,
which often give users the choice of multiple models that compute the same annotation.
spaCy's philosophy is to just have one --- the best one.  Our perspective is that
the redundant options are really only useful to researchers, who need to replicate
some prior work exactly.

Being opinionated allows us to keep the library small, fast, and up-to-date.  It
also makes the API much simpler.  Normal usage proceeds in three steps:

1. Loading resources;
2. Processing text;
3. Accessing annotations.

This document is divided into three parts, to match these stages.  We focus here
on the library's API. See also: Installation, Annotation Standards, Algorithmic Details,
and Benchmarks.

Loading Resources
-----------------

99\% of the time, you will load spaCy's resources using a language pipeline class,
e.g. `spacy.en.English`. The pipeline class reads the data from disk, from a
specified directory.  By default, spaCy installs data into each language's
package directory, and loads it from there.

Usually, this is all you will need:

    >>> from spacy.en import English
    >>> nlp = English()

If you need to replace some of the components, you may want to just make your
own pipeline class --- the English class itself does almost no work; it just
applies the modules in order. You can also provide a function or class that
produces a tokenizer, tagger, parser or entity recognizer to :code:`English.__init__`,
to customize the pipeline:

    >>> from spacy.en import English
    >>> from my_module import MyTagger
    >>> nlp = English(Tagger=MyTagger)

In more detail:

.. code::

  class English(object):
      def __init__(self,
        data_dir=path.join(path.dirname(__file__), 'data'),
        Tokenizer=Tokenizer.from_dir,
        Tagger=EnPosTagger,
        Parser=Createarser(ArcEager),
        Entity=CreateParser(BiluoNER),
        load_vectors=True
      ):

:code:`data_dir`
  :code:`unicode path`

  The data directory.  May be None, to disable any data loading (including
  the vocabulary).

:code:`Tokenizer`
  :code:`(Vocab vocab, unicode data_dir)(unicode) --> Tokens`
  
  A class/function that creates the tokenizer.

:code:`Tagger` / :code:`Parser` / :code:`Entity`
  :code:`(Vocab vocab, unicode data_dir)(Tokens) --> None`
  
  A class/function that creates the part-of-speech tagger /
  syntactic dependency parser / named entity recogniser.
  May be None or False, to disable tagging.

:code:`load_vectors` (bool)
  A boolean value to control whether the word vectors are loaded.


Processing Text
---------------

The text processing API is very small and simple. Everything is a callable object,
and you will almost always apply the pipeline all at once.


.. py:method:: English.__call__(text, tag=True, parse=True, entity=True) --> Tokens


text (unicode)
  The text to be processed.  No pre-processing needs to be applied, and any
  length of text can be submitted.  Usually you will submit a whole document.
  Text may be zero-length. An exception is raised if byte strings are supplied.

tag (bool)
  Whether to apply the part-of-speech tagger.

parse (bool)
  Whether to apply the syntactic dependency parser.

entity (bool)
  Whether to apply the named entity recognizer.


Accessing Annotation
--------------------

spaCy provides a rich API for using the annotations it calculates.  It is arranged
into three data classes:

1. :code:`Tokens`: A container, which provides document-level access;
2. :code:`Span`: A (contiguous) sequence of tokens, e.g. a sentence, entity, etc
3. :code:`Token`: An individual token, and a node in a parse tree;


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

.. autoclass:: spacy.spans.Span

:code:`__getitem__`, :code:`__iter__`, :code:`__len__`
  Sequence API

:code:`head`
  Syntactic head, or None

:code:`left`
  Tokens to the left of the span

:code:`rights`
  Tokens to the left of the span

:code:`orth` / :code:`orth_`
  Orth string

:code:`lemma` / :code:`lemma_`
  Lemma string

:code:`string`
  String

:code:`label` / :code:`label_`
  Label

:code:`subtree`
  Lefts + [self] + Rights

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


Lexical Lookup
--------------

Where possible, spaCy computes information over lexical *types*, rather than
*tokens*.  If you process a large batch of text, the number of unique types
you will see will grow exponentially slower than the number of tokens --- so
it's much more efficient to compute over types.  And, in small samples, we generally
want to know about the distribution of a word in the language at large ---
which again, is type-based information.

You can access the lexical features via the Token object, but you can also look them
up in the vocabulary directly:

    >>> from spacy.en import English
    >>> nlp = English()
    >>> lexeme = nlp.vocab[u'Amazon']

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


