.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================
spaCy: Industrial-strength NLP
==============================

spaCy is a library for industrial-strength text processing in Python and Cython.
It is commercial open source software, with a dual (AGPL or commercial)
license.

If you're a small company doing NLP, spaCy might seem like a minor miracle.
It's by far the fastest NLP software available.  The full processing pipeline
completes in 7ms, including state-of-the-art part-of-speech tagging and
dependency parsing.  All strings are mapped to integer IDs, tokens
are linked to word vectors and other lexical resources, and a range of useful
features are pre-calculated and cached.

If none of that made any sense to you, here's the gist of it.  Computers don't
understand text. This is unfortunate, because that's what the web almost entirely
consists of.  We want to recommend people text based on other text they liked.
We want to shorten text to display it on a mobile screen.  We want to aggregate
it, link it, filter it, categorise it, generate it and correct it.

spaCy provides a set of utility functions that help programmers build such
products.  It's an NLP engine, analogous to the 3d engines commonly licensed
for game development.

Example functionality
---------------------

Let's say you're developing a proofreading tool, or possibly an IDE for
writers.  You're convinced by Stephen King's advice that `adverbs are not your
friend <http://www.brainpickings.org/2013/03/13/stephen-king-on-adverbs/>`_, so
you want to **mark adverbs in red**.  We'll use one of the examples he finds
particularly egregious:

    >>> import spacy.en
    >>> from spacy.enums import ADVERB
    >>> # Load the pipeline, and call it with some text.
    >>> nlp = spacy.en.English()
    >>> tokens = nlp("‘Give it back,’ he pleaded abjectly, ‘it’s mine.’",
                     tag=True, parse=True)
    >>> output = ''
    >>> for tok in tokens:
    ...     # Token.string preserves whitespace, making it easy to
    ...     # reconstruct the original string.
    ...     output += tok.string.upper() if tok.is_pos(ADVERB) else tok.string
    >>> print(output)
    ‘Give it BACK,’ he pleaded ABJECTLY, ‘it’s mine.’


Easy enough --- but the problem is that we've also highlighted "back", when probably
we only wanted to highlight "abjectly". This is undoubtedly an adverb, but it's
not the sort of adverb King is talking about.  This is a persistent problem when
dealing with linguistic categories: the prototypical examples, the ones whic
spring to your mind, are often not the most common cases.

There are lots of ways we might refine our logic, depending on just what words
we want to flag.  The simplest way to filter out adverbs like "back" and "not"
is by word frequency: these words are much more common than the manner adverbs
the style guides are worried about.

The prob attribute of a Lexeme or Token object gives a log probability estimate
of the word, based on smoothed counts from a 3bn word corpus:

   >>> nlp.vocab[u'back'].prob
   -7.403977394104004
   >>> nlp.vocab[u'not'].prob
   -5.407193660736084
   >>> nlp.vocab[u'quietly'].prob
   -11.07155704498291

So we can easily exclude the N most frequent words in English from our adverb
marker.  Let's try N=1000 for now:

    >>> import spacy.en
    >>> from spacy.enums import ADVERB
    >>> nlp = spacy.en.English()
    >>> # Find log probability of Nth most frequent word
    >>> probs = [lex.prob for lex in nlp.vocab]
    >>> is_adverb = lambda tok: tok.is_pos(ADVERB) and tok.prob < probs[-1000]
    >>> tokens = nlp("‘Give it back,’ he pleaded abjectly, ‘it’s mine.’",
                     tag=True, parse=True)
    >>> print(''.join(tok.string.upper() if is_adverb(tok) else tok.string))
    ‘Give it back,’ he pleaded ABJECTLY, ‘it’s mine.’

There are lots of ways to refine the logic, depending on just what words we
want to flag.  Let's define this narrowly, and only flag adverbs applied to
verbs of communication or perception:

    >>> from spacy.enums import VERB, WN_V_COMMUNICATION, WN_V_COGNITION
    >>> def is_say_verb(tok):
    ...   return tok.is_pos(VERB) and (tok.check_flag(WN_V_COMMUNICATION) or
                                       tok.check_flag(WN_V_COGNITION))
    >>> print(''.join(tok.string.upper() if is_adverb(tok) and is_say_verb(tok.head)
                      else tok.string))
    ‘Give it back,’ he pleaded ABJECTLY, ‘it’s mine.’

The two flags refer to the 45 top-level categories in the WordNet ontology.
spaCy stores membership in these categories as a bit set, because
words can have multiple senses.  We only need one 64
bit flag variable per word in the vocabulary, so this useful data requires only
2.4mb of memory.

spaCy packs all sorts of other goodies into its lexicon.
Words are mapped to one these rich lexical types immediately, during
tokenization --- and spaCy's tokenizer is *fast*.

Efficiency
----------

.. table:: Efficiency comparison. See `Benchmarks`_ for details.

  +--------------+---------------------------+--------------------------------+
  |              | Absolute (ms per doc)     | Relative (to spaCy)            |
  +--------------+----------+--------+-------+----------+---------+-----------+
  | System       | Tokenize | Tag    | Parse | Tokenize | Tag     | Parse     |
  +--------------+----------+--------+-------+----------+---------+-----------+
  | spaCy        | 0.2ms    | 1ms    | 7ms   | 1x       | 1x      | 1x        |
  +--------------+----------+--------+-------+----------+---------+-----------+
  | CoreNLP      | 2ms      | 10ms   | 49ms  | 10x      | 10x     | 7x        |
  +--------------+----------+--------+-------+----------+---------+-----------+
  | ZPar         | 1ms      | 8ms    | 850ms | 5x       | 8x      | 121x      |
  +--------------+----------+--------+-------+----------+---------+-----------+
  | NLTK         | 4ms      | 443ms  | n/a   | 20x      | 443x    |  n/a      |
  +--------------+----------+--------+-------+----------+---------+-----------+


Efficiency is a major concern for NLP applications.  It is very common to hear
people say that they cannot afford more detailed processing, because their
datasets are too large.  This is a bad position to be in.  If you can't apply
detailed processing, you generally have to cobble together various heuristics.
This normally takes a few iterations, and what you come up with will usually be
brittle and difficult to reason about.

spaCy's parser is faster than most taggers, and its tokenizer is fast enough
for truly web-scale processing.  And the tokenizer doesn't just give you a list
of strings.  A spaCy token is a pointer to a Lexeme struct, from which you can
access a wide range of pre-computed features.

.. I wrote spaCy because I think existing commercial NLP engines are crap.
  Alchemy API are a typical example.  Check out this part of their terms of
  service:
  publish or perform any benchmark or performance tests or analysis relating to
  the Service or the use thereof without express authorization from AlchemyAPI;

.. Did you get that? You're not allowed to evaluate how well their system works,
  unless you're granted a special exception.  Their system must be pretty
  terrible to motivate such an embarrassing restriction.
  They must know this makes them look bad, but they apparently believe allowing
  you to evaluate their product would make them look even worse!

.. spaCy is based on science, not alchemy.  It's open source, and I am happy to
  clarify any detail of the algorithms I've implemented.
  It's evaluated against the current best published systems, following the standard
  methodologies.  These evaluations show that it performs extremely well.  

Accuracy
--------

.. table:: Accuracy comparison, on the standard benchmark data from the Wall Street Journal. See `Benchmarks`_ for details.

  +--------------+----------+------------+
  | System       | POS acc. | Parse acc. |
  +--------------+----------+------------+
  | spaCy        | 97.2     | 92.4       |
  +--------------+----------+------------+
  | CoreNLP      | 96.9     | 92.2       | 
  +--------------+----------+------------+
  | ZPar         | 97.3     | 92.9       |
  +--------------+----------+------------+
  | NLTK         | 94.3     | n/a        |
  +--------------+----------+------------+



.. toctree::
    :maxdepth: 3

    license.rst 
    quickstart.rst
    features.rst
    api.rst
