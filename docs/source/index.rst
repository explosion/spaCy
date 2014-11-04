.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

spaCy NLP Tokenizer and Lexicon
================================

spaCy is a library for industrial strength NLP in Python.  Its core
values are:

* **Efficiency**: You won't find faster NLP tools. For shallow analysis, it's 10x
  faster than Stanford Core NLP, and over 200x faster than NLTK.  Its parser is
  over 100x faster than Stanford's.

* **Accuracy**:  All spaCy tools are within 0.5% of the current published
  state-of-the-art, on both news and web text. NLP moves fast, so always check
  the numbers --- and don't settle for tools that aren't backed by
  rigorous recent evaluation.

* **Minimalism**:  This isn't a library that covers 43 known algorithms to do X. You
  get 1 --- the best one --- with a simple, low-level interface. This keeps the
  code-base small and concrete.  Our Python APIs use lists and
  dictionaries, and our C/Cython APIs use arrays and simple structs.
  

Comparison
----------

+----------------+-------------+--------+---------------+--------------+
| Tokenize & Tag | Speed (w/s) | Memory | % Acc. (news) | % Acc. (web) |
+----------------+-------------+--------+---------------+--------------+
| spaCy          | 107,000     |  1.3gb | 96.7          |              |
+----------------+-------------+--------+---------------+--------------+
| Stanford       | 8,000       |  1.5gb | 96.7          |              |
+----------------+-------------+--------+---------------+--------------+
| NLTK           | 543         |  61mb  | 94.0          |              |
+----------------+-------------+--------+---------------+--------------+


.. toctree::
    :hidden:
    :maxdepth: 3
    
    what/index.rst
    why/index.rst
    how/index.rst
