.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

spaCy NLP Tokenizer and Lexicon
================================

spaCy splits a string of natural language into a list of references to lexical types:

    >>> from spacy.en import EN
    >>> tokens = EN.tokenize(u"Examples aren't easy, are they?")
    >>> type(tokens[0])
    spacy.word.Lexeme
    >>> tokens[1] is tokens[5]
    True

Other tokenizers return lists of strings, which is
`downright barbaric <guide/overview.html>`__.  If you get a list of strings,
you have to write all the features yourself, and you'll probably compute them
on a per-token basis, instead of a per-type basis.  At scale, that's very
inefficient.

spaCy's tokens come with the following orthographic and distributional features
pre-computed:

* Orthographic flags, such as is_alpha, is_digit, is_punct, is_title etc;

* Useful string transforms, such as canonical casing, word shape, ASCIIfied,
  etc;

* Unigram log probability;

* Brown cluster;

* can_noun, can_verb etc tag-dictionary;

* oft_upper, oft_title etc case-behaviour flags.

The features are up-to-date with current NLP research, but you can replace or
augment them if you need to.

.. toctree::
    :maxdepth: 3
    
    guide/overview.rst
    guide/install.rst

    api/index.rst

    modules/index.rst

License
=======

+------------------+------+
| Non-commercial   | $0   |
+------------------+------+
| Trial commercial | $0   |
+------------------+------+
| Full commercial  | $500 |
+------------------+------+

spaCy is non-free software. Its source is published, but the copyright is
retained by the author (Matthew Honnibal).  Licenses are currently under preparation.

There is currently a gap between the output of academic NLP researchers, and
the needs of a small software companiess. I left academia to try to correct this.
My idea is that non-commercial and trial commercial use should "feel" just like
free software. But, if you do use the code in a commercial product, a small
fixed license-fee will apply, in order to fund development. 

