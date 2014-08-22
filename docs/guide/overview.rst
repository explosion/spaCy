Overview
========

What and Why
------------

spaCy is a lightning-fast, full-cream NLP tokenizer, tightly coupled to a
global vocabulary store.

Most tokenizers give you a sequence of strings. That's barbaric.
Giving you strings invites you to compute on every *token*, when what
you should be doing is computing on every *type*.  Remember
`Zipf's law <http://en.wikipedia.org/wiki/Zipf's_law>`_: you'll
see exponentially fewer types than tokens.

Instead of strings, spacy gives you Lexeme IDs, from which you can access
an excellent set of pre-computed orthographic and distributional features:

::

    >>> from spacy import en
    >>> apples, are, not, oranges, dots = en.tokenize(u"Apples aren't oranges...")
    >>> en.is_lower(apples)
    False
    # Distributional features calculated from large corpora
    # Smoothed unigram log probability
    >>> en.prob_of(are) > en.prob_of(oranges)
    True
    # After POS tagging lots of text, is this word ever a noun?
    >>> en.can_tag(are, en.NOUN)
    False
    # Is this word always title-cased?
    >>> en.often_title(apples)
    False

Accessing these properties is essentially free: the Lexeme IDs are actually
memory addresses that point to structs --- so the only cost is the Python
function call overhead.  If you call the accessor functions from Cython,
there's no overhead at all.

Benchmark
---------

Because it exploits Zipf's law, spaCy is much more efficient than
regular-expression based tokenizers.  See Algorithm and Implementation Details
for an explanation of how this works.

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
- Higher memory usage (up to 1gb)
- More conceptually complicated
- Tokenization rules expressed in code, not as data

