.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

spaCy NLP Tokenizer and Lexicon
================================

spaCy is a library for industrial strength NLP in Python and Cython.  Its core
values are efficiency, accuracy and minimalism.  

* Efficiency: spaCy is 

It does not attempt to be comprehensive,
or to provide lavish syntactic sugar.  This isn't a library that covers 43 known
algorithms to do X. You get 1 --- the best one --- with a simple, low-level interface. 
For commercial users, the code is free but the data isn't.  For researchers, both
are free and always will be.

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
