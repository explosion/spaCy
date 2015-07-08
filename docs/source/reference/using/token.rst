================
The Token Object
================

A Token represents a single word, punctuation or significant whitespace symbol.

Integer IDs are provided for all string features.  The (unicode) string is
provided by an attribute of the same name followed by an underscore, e.g.
token.orth is an integer ID, token.orth\_ is the unicode value.

The only exception is the Token.string attribute, which is (unicode)
string-typed.

**String Features**

:code:`string`
  The form of the word as it appears in the string, include trailing
  whitespace.  This is useful when you need to use linguistic features to
  add inline mark-up to the string.

:code:`orth` / :code:`orth_`
  The form of the word with no string normalization or processing, as it
  appears in the string, without trailing whitespace.

:code:`lemma` / :code:`lemma_`
  The "base" of the word, with no inflectional suffixes, e.g. the lemma of
  "developing" is "develop", the lemma of "geese" is "goose", etc.  Note that
  *derivational* suffixes are not stripped, e.g. the lemma of "instutitions"
  is "institution", not "institute".  Lemmatization is performed using the
  WordNet data, but extended to also cover closed-class words such as
  pronouns.  By default, the WN lemmatizer returns "hi" as the lemma of "his".
  We assign pronouns the lemma -PRON-.

:code:`lower` / :code:`lower_`
  The form of the word, but forced to lower-case, i.e. lower = word.orth\_.lower()

:code:`norm` / :code:`norm_`
  The form of the word, after language-specific normalizations have been
  applied.

:code:`shape` / :code:`shape_`
  A transform of the word's string, to show orthographic features.  The
  characters a-z are mapped to x, A-Z is mapped to X, 0-9 is mapped to d.
  After these mappings, sequences of 4 or more of the same character are
  truncated to length 4.  Examples: C3Po --> XdXx, favorite --> xxxx,
  :) --> :)

:code:`prefix` / :code:`prefix_`
  A length-N substring from the start of the word.  Length may vary by
  language; currently for English n=1, i.e. prefix = word.orth\_[:1]

:code:`suffix` / :code:`suffix_`
  A length-N substring from the end of the word.  Length may vary by
  language; currently for English n=3, i.e. suffix = word.orth\_[-3:]

**Distributional Features**

:code:`prob`
  The unigram log-probability of the word, estimated from counts from a
  large corpus, smoothed using Simple Good Turing estimation.

:code:`cluster`
  The Brown cluster ID of the word.  These are often useful features for
  linear models.  If you're using a non-linear model, particularly
  a neural net or random forest, consider using the real-valued word
  representation vector, in Token.repvec, instead.

:code:`repvec`
  A "word embedding" representation: a dense real-valued vector that supports
  similarity queries between words.  By default, spaCy currently loads
  vectors produced by the Levy and Goldberg (2014) dependency-based word2vec
  model.

**Syntactic Features**

:code:`tag`
  A morphosyntactic tag, e.g. NN, VBZ, DT, etc.  These tags are
  language/corpus specific, and typically describe part-of-speech and some
  amount of morphological information.  For instance, in the Penn Treebank
  tag set, VBZ is assigned to a present-tense singular verb.

:code:`pos`
  A part-of-speech tag, from the Google Universal Tag Set, e.g. NOUN, VERB,
  ADV.  Constants for the 17 tag values are provided in spacy.parts\_of\_speech.

:code:`dep`
  The type of syntactic dependency relation between the word and its
  syntactic head.

:code:`n_lefts`
  The number of immediate syntactic children preceding the word in the
  string.

:code:`n_rights`
  The number of immediate syntactic children following the word in the
  string.

**Navigating the Dependency Tree**

:code:`head`
  The Token that is the immediate syntactic head of the word.  If the word is
  the root of the dependency tree, the same word is returned.

:code:`lefts`
  An iterator for the immediate leftward syntactic children of the word.

:code:`rights`
  An iterator for the immediate rightward syntactic children of the word.

:code:`children`
  An iterator that yields from lefts, and then yields from rights.

:code:`subtree`
  An iterator for the part of the sentence syntactically governed by the
  word, including the word itself.


**Named Entities**

:code:`ent_type`
  If the token is part of an entity, its entity type

:code:`ent_iob`
  The IOB (inside, outside, begin) entity recognition tag for the token
