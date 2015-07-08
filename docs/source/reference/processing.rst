===============
Processing Text
===============

The text processing API is very small and simple. Everything is a callable object,
and you will almost always apply the pipeline all at once.

Applying a pipeline
-------------------


.. py:method:: English.__call__(text, tag=True, parse=True, entity=True) --> Tokens


text (unicode)
  The text to be processed.  No pre-processing needs to be applied, and any
  length of text can be submitted.  Usually you will submit a whole document.
  Text may be zero-length. An exception is raised if byte strings are supplied.

tag (bool)
  Whether to apply the part-of-speech tagger. Required for parsing and entity recognition.

parse (bool)
  Whether to apply the syntactic dependency parser.

entity (bool)
  Whether to apply the named entity recognizer.


**Examples**

    >>> from spacy.en import English
    >>> nlp = English()
    >>> doc = nlp(u'Some text.) # Applies tagger, parser, entity
    >>> doc = nlp(u'Some text.', parse=False) # Applies tagger and entity, not parser
    >>> doc = nlp(u'Some text.', entity=False) # Applies tagger and parser, not entity
    >>> doc = nlp(u'Some text.', tag=False) # Does not apply tagger, entity or parser
    >>> doc = nlp(u'') # Zero-length tokens, not an error
    >>> doc = nlp(b'Some text') # Error: need unicode
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "spacy/en/__init__.py", line 128, in __call__
      tokens = self.tokenizer(text)
    TypeError: Argument 'string' has incorrect type (expected unicode, got str)
    >>> doc = nlp(b'Some text'.decode('utf8')) # Encode to unicode first.
    >>>




Tokenizer
---------


.. autoclass:: spacy.tokenizer.Tokenizer
  :members:


Tagger
------

.. autoclass:: spacy.en.pos.EnPosTagger
  :members:

Parser and Entity Recognizer
----------------------------

.. autoclass:: spacy.syntax.parser.Parser
  :members:
