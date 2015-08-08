================
spacy.en.English
================


99\% of the time, you will load spaCy's resources using a language pipeline class,
e.g. `spacy.en.English`. The pipeline class reads the data from disk, from a
specified directory.  By default, spaCy installs data into each language's
package directory, and loads it from there.

Usually, this is all you will need:

    >>> from spacy.en import English
    >>> nlp = English()

If you need to replace some of the components, you may want to just make your
own pipeline class --- the English class itself does almost no work; it just
applies the modules in order. You can also provide a function or class that
produces a tokenizer, tagger, parser or entity recognizer to :code:`English.__init__`,
to customize the pipeline:

    >>> from spacy.en import English
    >>> from my_module import MyTagger
    >>> nlp = English(Tagger=MyTagger)

The text processing API is very small and simple. Everything is a callable object,
and you will almost always apply the pipeline all at once.


.. py:class:: spacy.en.English
  
  .. py:method:: __init__(self, data_dir=..., Tokenizer=..., Tagger=..., Parser=..., Entity=..., Matcher=..., Packer=None, load_vectors=True)

    :param unicode data_dir:
      The data directory.  May be None, to disable any data loading (including
      the vocabulary).

    :param Tokenizer:
      A class/function that creates the tokenizer.

    :param Tagger:
      A class/function that creates the part-of-speech tagger.

    :param Parser:
      A class/function that creates the dependency parser.

    :param Entity:
      A class/function that creates the named entity recogniser.

    :param bool load_vectors:
      A boolean value to control whether the word vectors are loaded.

  .. py:method:: __call__(text, tag=True, parse=True, entity=True) --> Doc

    :param unicode text:
      The text to be processed.  No pre-processing needs to be applied, and any
      length of text can be submitted.  Usually you will submit a whole document.
      Text may be zero-length. An exception is raised if byte strings are supplied.

    :param bool tag:
      Whether to apply the part-of-speech tagger. Required for parsing and entity
      recognition.

    :param bool parse:
      Whether to apply the syntactic dependency parser.

    :param bool entity:
      Whether to apply the named entity recognizer.

    :return: A document
    :rtype: :py:class:`spacy.tokens.Doc`

    :Example:

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
