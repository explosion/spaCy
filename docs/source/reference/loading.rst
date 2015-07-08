=================
Loading Resources
=================

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

In more detail:

.. code::

  class English(object):
      def __init__(self,
        data_dir=path.join(path.dirname(__file__), 'data'),
        Tokenizer=Tokenizer.from_dir,
        Tagger=EnPosTagger,
        Parser=Createarser(ArcEager),
        Entity=CreateParser(BiluoNER),
        load_vectors=True
      ):

:code:`data_dir`
  :code:`unicode path`

  The data directory.  May be None, to disable any data loading (including
  the vocabulary).

:code:`Tokenizer`
  :code:`(Vocab vocab, unicode data_dir)(unicode) --> Doc`
  
  A class/function that creates the tokenizer.

:code:`Tagger` / :code:`Parser` / :code:`Entity`
  :code:`(Vocab vocab, unicode data_dir)(Doc) --> None`
  
  A class/function that creates the part-of-speech tagger /
  syntactic dependency parser / named entity recogniser.
  May be None or False, to disable tagging.

:code:`load_vectors`
  :code:`bool`
  A boolean value to control whether the word vectors are loaded.



