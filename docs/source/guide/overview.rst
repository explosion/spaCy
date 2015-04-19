Overview
========

What and Why
------------

spaCy is a lightning-fast, full-cream NLP tokenizer and lexicon.

Most tokenizers give you a sequence of strings. That's barbaric.
Giving you strings invites you to compute on every *token*, when what
you should be doing is computing on every *type*.  Remember
`Zipf's law <http://en.wikipedia.org/wiki/Zipf's_law>`_: you'll
see exponentially fewer types than tokens.

Instead of strings, spaCy gives you references to Lexeme objects, from which you
can access an excellent set of pre-computed orthographic and distributional features:

::

    >>> from spacy import en
    >>> apples, are, nt, oranges, dots = en.EN.tokenize(u"Apples aren't oranges...")
    >>> are.prob >= oranges.prob
    True
    >>> apples.check_flag(en.IS_TITLE)
    True
    >>> apples.check_flag(en.OFT_TITLE)
    False
    >>> are.check_flag(en.CAN_NOUN)
    False

spaCy makes it easy to write very efficient NLP applications, because your feature
functions have to do almost no work: almost every lexical property you'll want
is pre-computed for you.  See the tutorial for an example POS tagger.

Benchmark
---------

The tokenizer itself is also very efficient:

+--------+-------+--------------+--------------+
| System | Time	 | Words/second | Speed Factor |
+--------+-------+--------------+--------------+
| NLTK	 | 6m4s  | 89,000       | 1.00         |
+--------+-------+--------------+--------------+
| spaCy	 | 9.5s	 | 3,093,000	| 38.30        |
+--------+-------+--------------+--------------+

The comparison refers to 30 million words from the English Gigaword, on
a Maxbook Air.  For context, calling string.split() on the data completes in
about 5s.

Pros and Cons
-------------

Pros:

- All tokens come with indices into the original string
- Full unicode support
- Extensible to other languages
- Batch operations computed efficiently in Cython
- Cython API
- numpy interoperability

Cons:

- It's new (released September 2014)
- Security concerns, from memory management
- Higher memory usage (up to 1gb)
- More conceptually complicated
- Tokenization rules expressed in code, not as data
