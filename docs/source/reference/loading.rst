=================
Loading Resources
=================
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



