====================
Annotation Standards
====================

This document describes the target annotations spaCy is trained to predict.

This is currently a work in progress. Please ask questions on the issue tracker,
so that the answers can be integrated here to improve the documentation.

https://github.com/honnibal/spaCy/issues

English
=======

Tokenization
------------

Tokenization standards are based on the OntoNotes 5 corpus.

The tokenizer differs from most by including tokens for significant whitespace.
Any sequence of whitespace characters beyond a single space (' ') is included
as a token. For instance:

    >>> from spacy.en import English
    >>> nlp = English(parse=False)
    >>> tokens = nlp(u'Some\nspaces  and\ttab characters')
    >>> print [t.orth_ for t in tokens]
    [u'Some', u'\n', u'spaces', u' ', u'and', u'\t', u'tab', u'characters']

The whitespace tokens are useful for much the same reason punctuation is --- it's
often an important delimiter in the text.  By preserving it in the token output,
we are able to maintain a simple alignment between the tokens and the original
string, and we ensure that the token stream does not lose information.

Sentence boundary detection
---------------------------

Sentence boundaries are calculated from the syntactic parse tree, so features
such as punctuation and capitalisation play an important but non-decisive role
in determining the sentence boundaries.  Usually this means that the sentence
boundaries will at least coincide with clause boundaries, even given poorly
punctuated text.

Part-of-speech Tagging
----------------------

The part-of-speech tagger uses the OntoNotes 5 version of the Penn Treebank
tag set.  We also map the tags to the simpler Google Universal POS Tag set.

Details here: https://github.com/honnibal/spaCy/blob/master/spacy/en/pos.pyx#L124

Lemmatization
-------------

A "lemma" is the uninflected form of a word. In English, this means:

* Adjectives: The form like "happy", not "happier" or "happiest"
* Adverbs: The form like "badly", not "worse" or "worst"
* Nouns: The form like "dog", not "dogs"; like "child", not "children"
* Verbs: The form like "write", not "writes", "writing", "wrote" or "written" 

The lemmatization data is taken from WordNet. However, we also add a special
case for pronouns: all pronouns are lemmatized to the special token -PRON-.

Syntactic Dependency Parsing
----------------------------

The parser is trained on data produced by the ClearNLP converter. Details of
the annotation scheme can be found here: 

http://www.mathcs.emory.edu/~choi/doc/clear-dependency-2012.pdf

Named Entity Recognition
------------------------

 +--------------+-----------------------------------------------------+
 | PERSON       | People, including fictional                         |
 +--------------+-----------------------------------------------------+
 | NORP         | Nationalities or religious or political groups      |
 +--------------+-----------------------------------------------------+
 | FACILITY     | Buildings, airports, highways, bridges, etc.        |
 +--------------+-----------------------------------------------------+
 | ORGANIZATION | Companies, agencies, institutions, etc.             |
 +--------------+-----------------------------------------------------+
 | GPE          | Countries, cities, states                           |
 +--------------+-----------------------------------------------------+
 | LOCATION     | Non-GPE locations, mountain ranges, bodies of water |
 +--------------+-----------------------------------------------------+
 | PRODUCT      | Vehicles, weapons, foods, etc. (Not services)       |
 +--------------+-----------------------------------------------------+
 | EVENT        | Named hurricanes, battles, wars, sports events, etc.|
 +--------------+-----------------------------------------------------+
 | WORK OF ART  | Titles of books, songs, etc.                        |
 +--------------+-----------------------------------------------------+
 | LAW          | Named documents made into laws                      |
 +--------------+-----------------------------------------------------+
 | LANGUAGE     | Any named language                                  |
 +--------------+-----------------------------------------------------+

The following values are also annotated in a style similar to names:

 +--------------+---------------------------------------------+
 | DATE         | Absolute or relative dates or periods       |
 +--------------+---------------------------------------------+
 | TIME         | Times smaller than a day                    |
 +--------------+---------------------------------------------+
 | PERCENT      | Percentage (including “%”)                  |
 +--------------+---------------------------------------------+
 | MONEY        | Monetary values, including unit             |
 +--------------+---------------------------------------------+
 | QUANTITY     | Measurements, as of weight or distance      |
 +--------------+---------------------------------------------+
 | ORDINAL      | "first", "second"                           |
 +--------------+---------------------------------------------+
 | CARDINAL     | Numerals that do not fall under another type|
 +--------------+---------------------------------------------+
