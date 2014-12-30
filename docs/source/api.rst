===============
API Reference
===============

spaCy provides a number of text-processing components, which can be arranged
into text-processing pipelines.  The pipeline should first construct a Tokens
object, which will then be enhanced with various information by subsequent
components.  Access is then 

Most users will want to use a pre-prepared pipeline for a given language.  This
page first lists these pipelines and their relevant APIs, before listing the
APIs for the individual components.

English Pipeline
----------------

The spacy.en package exports a single class, English, and several constants,
under spacy.en.defs.

.. autoclass:: spacy.en.English
   :members:  

.. autommodule:: spacy.en.pos
   :members:

.. automodule:: spacy.en.attrs
   :members:
   :undoc-members:

The Tokens Class
----------------


.. autoclass:: spacy.tokens.Tokens
   :members:

.. autoclass:: spacy.tokens.Token
   :members:

Generic Classes
---------------

.. automodule:: spacy.vocab
   :members:

.. automodule:: spacy.tokenizer
   :members:

.. automodule:: spacy.tagger
   :members:

.. automodule:: spacy.syntax.parser
   :members:

Utility Functions
-----------------

.. automodule:: spacy.orth
   :members:


