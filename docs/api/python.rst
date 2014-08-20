Python API
==========

.. py:currentmodule:: spacy.en

To and from unicode strings
---------------------------

.. autofunction:: tokenize
.. autofunction:: lookup
.. autofunction:: unhash

Access (Hashed) String Views
----------------------------

.. autofunction:: lex_of
.. autofunction:: norm_of
.. autofunction:: shape_of
.. autofunction:: last3_of

Access String Properties
------------------------

.. autofunction:: length_of
.. autofunction:: first_of

Check Orthographic Flags
-------------------------

.. autofunction:: is_alpha
.. autofunction:: is_digit
.. autofunction:: is_punct
.. autofunction:: is_space
.. autofunction:: is_lower
.. autofunction:: is_upper
.. autofunction:: is_title
.. autofunction:: is_ascii

Access Distributional Information
---------------------------------

.. autofunction:: prob_of
.. autofunction:: cluster_of
.. autofunction:: check_tag_flag
.. autofunction:: check_dist_flag
