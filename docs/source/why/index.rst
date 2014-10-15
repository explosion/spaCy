Why
===

Benchmarks
----------

Efficiency
----------

+--------+-------+--------------+--------------+
| System | Time	 | Words/second | Speed Factor |
+--------+-------+--------------+--------------+
| NLTK	 | 6m4s  | 89,000       | 1.00         |
+--------+-------+--------------+--------------+
| spaCy	 | 9.5s	 | 3,093,000	| 38.30        |
+--------+-------+--------------+--------------+


Accuracy
--------

The comparison refers to 30 million words from the English Gigaword, on
a Maxbook Air.  For context, calling string.split() on the data completes in
about 5s.

Pros and Cons
-------------

