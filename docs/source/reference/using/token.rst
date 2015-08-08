================
The Token Object
================

A Token represents a single word, punctuation or significant whitespace symbol.

Integer IDs are provided for all string features.  The (unicode) string is
provided by an attribute of the same name followed by an underscore, e.g.
token.orth is an integer ID, token.orth\_ is the unicode value.

The only exception is the Token.string attribute, which is (unicode)
string-typed.


.. py:class:: Token

  .. py:method:: __init__(self, Vocab vocab, Doc doc, int offset)

  **String Views**

  .. py:attribute:: orth / orth\_

    The form of the word with no string normalization or processing, as it
    appears in the string, without trailing whitespace.

  .. py:attribute:: lemma / lemma\_

    The "base" of the word, with no inflectional suffixes, e.g. the lemma of
    "developing" is "develop", the lemma of "geese" is "goose", etc.  Note that
    *derivational* suffixes are not stripped, e.g. the lemma of "instutitions"
    is "institution", not "institute".  Lemmatization is performed using the
    WordNet data, but extended to also cover closed-class words such as
    pronouns.  By default, the WN lemmatizer returns "hi" as the lemma of "his".
    We assign pronouns the lemma -PRON-.

  .. py:attribute:: lower / lower\_

    The form of the word, but forced to lower-case, i.e. lower = word.orth\_.lower()

  .. py:attribute:: norm / norm\_

    The form of the word, after language-specific normalizations have been
    applied.

  .. py:attribute:: shape / shape\_

    A transform of the word's string, to show orthographic features.  The
    characters a-z are mapped to x, A-Z is mapped to X, 0-9 is mapped to d.
    After these mappings, sequences of 4 or more of the same character are
    truncated to length 4.  Examples: C3Po --> XdXx, favorite --> xxxx,
    :) --> :)

  .. py:attribute:: prefix / prefix\_

    A length-N substring from the start of the word.  Length may vary by
    language; currently for English n=1, i.e. prefix = word.orth\_[:1]

  .. py:attribute:: suffix / suffix\_

    A length-N substring from the end of the word.  Length may vary by
    language; currently for English n=3, i.e. suffix = word.orth\_[-3:]

  .. py:attribute:: lex_id

  **Alignment and Output**

  .. py:attribute:: idx

  .. py:method:: __len__(self)

  .. py:method:: __unicode__(self)

  .. py:method:: __str__(self)

  .. py:attribute:: string

    The form of the word as it appears in the string, **including trailing
    whitespace**.  This is useful when you need to use linguistic features to
    add inline mark-up to the string.

  .. py:method:: nbor(self, int i=1)

  **Distributional Features**

  .. py:attribute:: repvec

    A "word embedding" representation: a dense real-valued vector that supports
    similarity queries between words.  By default, spaCy currently loads
    vectors produced by the Levy and Goldberg (2014) dependency-based word2vec
    model.

  .. py:attribute:: cluster

    The Brown cluster ID of the word.  These are often useful features for
    linear models.  If you're using a non-linear model, particularly
    a neural net or random forest, consider using the real-valued word
    representation vector, in Token.repvec, instead.

  .. py:attribute:: prob

    The unigram log-probability of the word, estimated from counts from a
    large corpus, smoothed using Simple Good Turing estimation.

  **Navigating the Dependency Tree**

  .. py:attribute:: pos / pos\_

    A part-of-speech tag, from the Google Universal Tag Set, e.g. NOUN, VERB,
    ADV.  Constants for the 17 tag values are provided in spacy.parts\_of\_speech.

  .. py:attribute:: tag / tag\_

    A morphosyntactic tag, e.g. NN, VBZ, DT, etc.  These tags are
    language/corpus specific, and typically describe part-of-speech and some
    amount of morphological information.  For instance, in the Penn Treebank
    tag set, VBZ is assigned to a present-tense singular verb.

  .. py:attribute:: dep / dep\_

    The type of syntactic dependency relation between the word and its
    syntactic head.

  .. py:attribute:: head

    The Token that is the immediate syntactic head of the word.  If the word is
    the root of the dependency tree, the same word is returned.

  .. py:attribute:: lefts

    An iterator for the immediate leftward syntactic children of the word.

  .. py:attribute:: rights

    An iterator for the immediate rightward syntactic children of the word.

  .. py:attribute:: n_lefts

    The number of immediate syntactic children preceding the word in the
    string.

  .. py:attribute:: n_rights

    The number of immediate syntactic children following the word in the
    string.

  .. py:attribute:: children

    An iterator that yields from lefts, and then yields from rights.

  .. py:attribute:: subtree

    An iterator for the part of the sentence syntactically governed by the
    word, including the word itself.

  .. py:attribute:: left_edge

  .. py:attribute:: right_edge

  .. py:attribute:: conjuncts

  **Named Entities**

  .. py:attribute:: ent_type

    If the token is part of an entity, its entity type

  .. py:attribute:: ent_iob

    The IOB (inside, outside, begin) entity recognition tag for the token

  **Lexeme Flags**

  .. py:method:: check_flag(self, attr_id_t flag_id)

  .. py:attribute:: is_oov

  .. py:attribute:: is_alpha

  .. py:attribute:: is_ascii

  .. py:attribute:: is_digit

  .. py:attribute:: is_lower

  .. py:attribute:: is_title

  .. py:attribute:: is_punct

  .. py:attribute:: is_space

  .. py:attribute:: like_url

  .. py:attribute:: like_num

  .. py:attribute:: like_email
