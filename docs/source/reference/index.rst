=========
Reference
=========

spaCy is a suite of natural language processing tools, arranged into
a pipeline.  It is substantially more opinionated than most similar libraries,
which often give users the choice of multiple models that compute the same annotation.
spaCy's philosophy is to just have one --- the best one.  Our perspective is that
the redundant options are really only useful to researchers, who need to replicate
some prior work exactly.

Being opinionated allows us to keep the library small, fast, and up-to-date.
Below is a summary table showing every class in spaCy, where it is implemented,
the basic usage, and a link to its documentation.

 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Class name  | Implemented in           | Getting                   | Using                        | Documentation    |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | English     | spacy/en/__init__.py     | nlp = English()           | tokens = nlp(u'Some text')   | processing.rst   |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Doc         | spacy/doc.pyx            | doc = nlp(text)           | token = doc[10]              | accessing/doc.rst|
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Token       | spacy/token.pyx          | token = doc[10]           | token.head.repvec            | accessing.rst    |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Span        | spacy/span.pyx           | sent = list(doc.sents)[0] | token = sent[0]              | accessing.rst    |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Vocab       | spacy/vocab.pyx          | nlp.vocab                 | nlp.vocab[u'word']           | lookup/vocab.rst |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | StringStore | spacy/strings.pyx        | nlp.vocab.strings         | nlp.vocab.strings[u'word']   | lookup/token.rst |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Tokenizer   | spacy/tokenizer.pyx      | nlp.tokenizer             | tokens = nlp.tokenizer(text) | processing.rst   |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | EnPosTagger | spacy/en/pos.pyx         | nlp.tagger                | nlp.tagger(tokens)           | processing.rst   |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Parser      | spacy/syntax/parser.pyx  | nlp.parser                | nlp.parser(tokens)           | processing.rst   |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Lexeme      | spacy/lexeme.pyx         | lex = nlp.vocab[u'word']  | lex.repvec                   | lookup.rst       |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Lemmatizer  | spacy/en/lemmatizer.py   |                           |                              | misc.rst         |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | GoldParse   | spacy/gold.pyx           |                           |                              | misc.rst         |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
 | Scorer      | spacy/scorer.py          |                           |                              |                  |
 +-------------+--------------------------+---------------------------+------------------------------+------------------+
