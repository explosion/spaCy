.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

spaCy NLP Tokenizer and Lexicon
================================

spaCy is a library for industrial strength NLP in Python and Cython.  Its core
values are efficiency, accuracy and minimalism.  

* Efficiency: spaCy is TODOx faster than the Stanford tools, and TODOx faster
  than NLTK.  You won't find faster NLP tools. Using spaCy will save you
  thousands in server costs, and will force you to make fewer compromises.

* Accuracy:  All spaCy tools are within 0.5% of the current published
  state-of-the-art, on both news and web text. NLP moves fast, so always check
  the numbers --- and don't settle for tools that aren't backed by
  rigorous recent evaluation. An algorithm that was "close enough to state-of-the-art"
  5 years ago is probably crap by today's standards.

* Minimalism:  This isn't a library that covers 43 known algorithms to do X. You
  get 1 --- the best one --- with a simple, low-level interface. This keeps the
  code-base small and concrete.  Our Python APIs use lists and
  dictionaries, and our C/Cython APIs use arrays and simple structs.
  

Comparison
----------
+-------------+-------------+---+-----------+--------------+
| POS taggers | Speed (w/s) | % Acc. (news) | % Acc. (web) |
+-------------+-------------+---------------+--------------+
| spaCy       |             |               |              |
+-------------+-------------+---------------+--------------+
| Stanford    | 16,000      |               |              |
+-------------+-------------+---------------+--------------+
| NLTK        |             |               |              |
+-------------+-------------+---------------+--------------+


.. toctree::
    :hidden:
    :maxdepth: 3
    
    what/index.rst
    why/index.rst
    how/index.rst
