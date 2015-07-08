=========
Reference
=========

Below is a summary table showing every class in spaCy, where it is implemented,
the basic usage, and a link to its documentation.


 +----------------+--------------------------------+--------------------------+
 | Class name     | Implemention                   | Usage                    |
 +================+================================+==========================+
 | `English`_     | `spacy/en/__init__.py`_        | doc = English()          |
 +----------------+--------------------------------+--------------------------+
 | `Doc`_         | `spacy/doc.pyx`_               | doc = nlp(text)          |
 +----------------+--------------------------------+--------------------------+
 | `Token`_       | `spacy/token.pyx`_             | token = doc[10]          |
 +----------------+--------------------------------+--------------------------+
 | `Span`_        | `spacy/span.pyx`_              | sent = doc.sents.next()  |
 +----------------+--------------------------------+--------------------------+
 | `Vocab`_       | `spacy/vocab.pyx`_             | nlp.vocab                |
 +----------------+--------------------------------+--------------------------+
 | `StringStore`_ | `spacy/strings.pyx`_           | nlp.vocab.strings        |
 +----------------+--------------------------------+--------------------------+
 | `Tokenizer`_   | `spacy/tokenizer.pyx`_         | nlp.tokenizer            |
 +----------------+--------------------------------+--------------------------+
 | `EnPosTagger`_ | `spacy/en/pos.pyx`_            | nlp.tagger               |
 +----------------+--------------------------------+--------------------------+
 | `Parser`_      | `spacy/syntax/parser.pyx`_     | nlp.parser               |
 +----------------+--------------------------------+--------------------------+
 | `Lexeme`_      | `spacy/lexeme.pyx`_            | lex = nlp.vocab[u'word'] |
 +----------------+--------------------------------+--------------------------+
 | `GoldParse`_   | `spacy/gold.pyx`_              |                          |
 +----------------+--------------------------------+--------------------------+
 | `Scorer`_      | `spacy/scorer.py`_             |                          |
 +----------------+--------------------------------+--------------------------+


 .. _English: processing.html

.. _Doc: using/doc.html

.. _Token: using/token.html

.. _Span: using/span.html

.. _Vocab: lookup.html

.. _StringStore: lookup.html

.. _Tokenizer: processing.html

.. _EnPosTagger: processing.html

.. _Parser: processing.html

.. _Lexeme: lookup.html

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

