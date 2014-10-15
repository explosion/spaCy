.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

spaCy NLP Tokenizer and Lexicon
================================

spaCy is an industrial-strength multi-language tokenizer, bristling with features
you never knew you wanted. You do want these features though --- your current
tokenizer has been doing it wrong.
Where other tokenizers give you a list of strings, spaCy gives you references
to rich lexical types, for easy, excellent and efficient feature extraction.

* **Easy**: Tokenizer returns a sequence of rich lexical types, with features
  pre-computed:

    >>> from spacy.en import EN
    >>> for w in EN.tokenize(string):
    ...   print w.sic, w.shape, w.cluster, w.oft_title, w.can_verb

Check out the tutorial and API docs.

* **Excellent**: Distributional and orthographic features are crucial to robust
  NLP. Without them, models can only learn from tiny annotated training
  corpora.  Read more.
  
* **Efficient**: spaCy serves you rich lexical objects faster than most
  tokenizers can give you a list of strings.  

+--------+-------+--------------+--------------+
| System | Time	 | Words/second | Speed Factor |
+--------+-------+--------------+--------------+
| NLTK	 | 6m4s  | 89,000       | 1.00         |
+--------+-------+--------------+--------------+
| spaCy	 | 9.5s	 | 3,093,000	| 38.30        |
+--------+-------+--------------+--------------+



.. toctree::
    :hidden:
    :maxdepth: 3
    
    what/index.rst
    why/index.rst
    how/index.rst
