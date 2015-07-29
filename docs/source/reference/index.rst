=============
Documentation
=============

The table below shows every class in spaCy: a link to its documentation, implementation,
and a small usage snippet.


 +----------------+--------------------------+--------------------------------+
 | Class name     | Usage                    | Implemention                   |
 +================+==========================+================================+
 | `English`_     | doc = English()          | `spacy/en/__init__.py`_        |
 +----------------+--------------------------+--------------------------------+
 | Data objects                                                               |
 +----------------+--------------------------+--------------------------------+
 | `Doc`_         | doc = nlp(text)          | `spacy/doc.pyx`_               |
 +----------------+--------------------------+--------------------------------+
 | `Token`_       | token = doc[10]          | `spacy/token.pyx`_             |
 +----------------+--------------------------+--------------------------------+
 | `Span`_        | sent = doc.sents.next()  | `spacy/span.pyx`_              |
 +----------------+--------------------------+--------------------------------+
 | `Lexeme`_      | lex = nlp.vocab[u'word'] | `spacy/lexeme.pyx`_            |
 +----------------+--------------------------+--------------------------------+
 | Lookup tables                                                              |
 +----------------+--------------------------+--------------------------------+
 | `Vocab`_       | nlp.vocab                | `spacy/vocab.pyx`_             |
 +----------------+--------------------------+--------------------------------+
 | `StringStore`_ | nlp.vocab.strings        | `spacy/strings.pyx`_           |
 +----------------+--------------------------+--------------------------------+
 | Processing modules                                                         |
 +----------------+--------------------------+--------------------------------+
 | `Tokenizer`_   | nlp.tokenizer            | `spacy/tokenizer.pyx`_         |
 +----------------+--------------------------+--------------------------------+
 | `EnPosTagger`_ | nlp.tagger               | `spacy/en/pos.pyx`_            |
 +----------------+--------------------------+--------------------------------+
 | `Parser`_      | nlp.parser               | `spacy/syntax/parser.pyx`_     |
 +----------------+--------------------------+--------------------------------+
 | Parser internals                                                           |
 +----------------+--------------------------+--------------------------------+
 | ArcEager       |                          | spacy/syntax/arc_eager.pyx     |
 +----------------+--------------------------+--------------------------------+
 | BiluoPushDown  |                          | spacy/syntax/ner.pyx           |
 +----------------+--------------------------+--------------------------------+
 | StateClass     |                          | spacy/syntax/stateclass.pyx    |
 +----------------+--------------------------+--------------------------------+
 | Research Utilities                                                         |
 +----------------+--------------------------+--------------------------------+
 | `GoldParse`_   |                          | `spacy/gold.pyx`_              |
 +----------------+--------------------------+--------------------------------+
 | `Scorer`_      |                          | `spacy/scorer.py`_             |
 +----------------+--------------------------+--------------------------------+


.. toctree::
    :maxdepth: 4

    loading.rst
    processing.rst
    using/document.rst
    using/span.rst
    using/token.rst
    using/lexeme.rst


.. _English: processing.html

.. _Doc: using/doc.html

.. _Token: using/token.html

.. _Span: using/span.html

.. _Lexeme: using/lexeme.html

.. _Vocab: lookup.html

.. _StringStore: lookup.html

.. _Tokenizer: processing.html

.. _EnPosTagger: processing.html

.. _Parser: processing.html

.. _Scorer: misc.html

.. _GoldParse:  misc.html


.. _spacy/en/__init__.py: https://github.com/honnibal/spaCy/tree/master/spacy/en/__init__.py

.. _spacy/doc.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/tokens.pyx

.. _spacy/token.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/tokens.pyx

.. _spacy/span.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/spans.pyx

.. _spacy/vocab.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/vocab.pyx

.. _spacy/strings.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/strings.pyx

.. _spacy/tokenizer.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/tokenizer.pyx

.. _spacy/en/pos.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/en/pos.pyx

.. _spacy/syntax/parser.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/syntax/parser.pyx

.. _spacy/lexeme.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/lexeme.pyx

.. _spacy/gold.pyx: https://github.com/honnibal/spaCy/tree/master/spacy/gold.pyx

.. _spacy/scorer.py: https://github.com/honnibal/spaCy/tree/master/spacy/scorer.py
