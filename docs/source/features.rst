Lexeme Features
===============

A lexeme is an entry in the lexicon --- the vocabulary --- for a word, punctuation
symbol, whitespace unit, etc.  Lexemes come with lots of pre-computed information,
that help you write good feature functions.  Features are integer-valued where
possible --- instead of strings, spaCy refers to strings by consecutive ID numbers,
which you can use to look up the string values if necessary.

String features
---------------

+---------+-------------------------------------------------------------------+
| SIC     | The word as it appeared in the sentence, unaltered.               |
+---------+-------------------------------------------------------------------+
| NORM    | For frequent words, case normalization is applied.                |
|         | Otherwise, back-off to SHAPE.                                     |
+---------+-------------------------------------------------------------------+
| SHAPE   | Remap the characters of the word as follows:                      |
|         |                                                                   |
|         | a-z --> x, A-Z --> X, 0-9 --> d, ,.;:"'?!$- --> self, other --> \*|
|         |                                                                   |
|         | Trim sequences of length 3+ to 3, e.g                             |
|         |                                                                   |
|         | apples --> xxx, Apples --> Xxxx, app9LES@ --> xxx9XXX*            |
+---------+-------------------------------------------------------------------+
| ASCIIED | Use unidecode.unidecode(sic) to approximate the word using the    |
|         | ascii characters.                                                 |
+---------+-------------------------------------------------------------------+
| PREFIX  | sic_unicode_string[:1]                                            |
+---------+-------------------------------------------------------------------+
| SUFFIX  | sic_unicode_string[-3:]                                           |
+---------+-------------------------------------------------------------------+


Integer features
----------------

+--------------+--------------------------------------------------------------+
| LENGTH       |  Length of the string, in unicode                            |
+--------------+--------------------------------------------------------------+
| CLUSTER      | Brown cluster                                                |
+--------------+--------------------------------------------------------------+
| POS_TYPE     | K-means cluster of word's tag affinities                     |
+--------------+--------------------------------------------------------------+
| SENSE_TYPE   | K-means cluster of word's sense affinities                   |
+--------------+--------------------------------------------------------------+

Boolean features
----------------

+-------------+--------------------------------------------------------------+
| IS_ALPHA    | The result of sic.isalpha()                                  |
+-------------+--------------------------------------------------------------+
| IS_ASCII    | Check whether all the word's characters are ascii characters |
+-------------+--------------------------------------------------------------+
| IS_DIGIT    | The result of sic.isdigit()                                  |
+-------------+--------------------------------------------------------------+
| IS_LOWER    | The result of sic.islower()                                  |
+-------------+--------------------------------------------------------------+
| IS_PUNCT    | Check whether all characters are in the class TODO           |
+-------------+--------------------------------------------------------------+
| IS_SPACE    | The result of sic.isspace()                                  |
+-------------+--------------------------------------------------------------+
| IS_TITLE    | The result of sic.istitle()                                  |
+-------------+--------------------------------------------------------------+
| IS_UPPER    | The result of sic.isupper()                                  |
+-------------+--------------------------------------------------------------+
| LIKE_URL    | Check whether the string looks like it could be a URL. Aims  |
|             | for low false negative rate.                                 |
+-------------+--------------------------------------------------------------+
| LIKE_NUMBER | Check whether the string looks like it could be a numeric    |
|             | entity, e.g. 10,000 10th .10 . Skews for low false negative  |
|             | rate.                                                        |
+-------------+--------------------------------------------------------------+
| IN_LIST     | Facility for loading arbitrary run-time word lists?          |
+-------------+--------------------------------------------------------------+
