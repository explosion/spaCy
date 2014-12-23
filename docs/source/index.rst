.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===================================
spaCy: Text-processing for products
===================================

spaCy is a library for industrial-strength text processing in Python and Cython.
Its core values are efficiency, accuracy and minimalism: you get a fast pipeline of
state-of-the-art components, a nice API, and no clutter.

spaCy is particularly good for feature extraction, because it pre-loads lexical
resources, maps strings to integer IDs, and supports output of numpy arrays:

    >>> from spacy.en import English
    >>> nlp = English()
    >>> tokens = nlp(u'An example sentence', tag=True, parse=True)
    >>> from spacy.en import attrs
    >>> feats = tokens.to_array((attrs.LEMMA, attrs.POS, attrs.SHAPE, attrs.CLUSTER))
    >>> for lemma, pos, shape, cluster in feats:
    ...   print nlp.strings[lemma], nlp.tagger.tags[pos], nlp.strings[shape], cluster

spaCy also makes it easy to add in-line mark up. Let's say you want to mark all
adverbs in red:

    >>> from spacy.defs import ADVERB
    >>> color = lambda t: u'\033[91m' % t if t.pos == ADVERB else u'%s'
    >>> print u''.join(color(token) + unicode(token) for t in tokens)

Easy.  The trick here is that the Token objects know to pad themselves with
whitespace when you ask for their unicode representation, so you can always get
back the original string. 

spaCy is also very efficient --- much more efficient than any other language
processing tools available.  The table below compares the time to tokenize, POS
tag and parse 100m words of text; it also shows accuracy on the standard
evaluation, from the Wall Street Journal:


+----------+----------+---------------+----------+
| System   | Tokenize | POS Tag       |          |
+----------+----------+---------------+----------+
| spaCy    | 37s      | 98s           |          |
+----------+----------+---------------+----------+
| NLTK     | 626s     | 44,310s (12h) |          |
+----------+----------+---------------+----------+
| CoreNLP  | 420s     | 1,300s (22m)  |          |
+----------+----------+---------------+----------+
| ZPar     |          | ~1,500s       |          |
+----------+----------+---------------+----------+

spaCy completes its whole pipeline faster than some of the other libraries can
tokenize the text.  Its POS tag accuracy is as good as any system available.
For parsing, I chose an algorithm that sacrificed some accuracy, in favour of
efficiency.

I wrote spaCy so that startups and other small companies could take advantage
of the enormous progress being made by NLP academics.  Academia is competitive,
and what you're competing to do is write papers --- so it's very hard to write
software useful to non-academics. Seeing this gap, I resigned from my post-doc,
and wrote spaCy.

spaCy is dual-licensed: you can either use it under the GPL, or pay a one-time
fee of $5000 for a commercial license.  I think this is excellent value:
you'll find NLTK etc much more expensive, because what you save on license
cost, you'll lose many times over in lost productivity. $5000 does not buy you
much developer time.

.. toctree::
    :hidden:
    :maxdepth: 3

    features.rst
    license_stories.rst 
