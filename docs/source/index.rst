.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===================================
spaCy: Text-processing for products
===================================

spaCy is a library for industrial-strength text processing in Python and Cython.
Its core values are efficiency, accuracy and minimalism: you get a fast pipeline of
state-of-the-art components, a nice API, and no clutter:

    >>> from spacy.en import English
    >>> nlp = English()
    >>> tokens = nlp(u'An example sentence', tag=True, parse=True)
    >>> for token in tokens:
    ...   print token.lemma, token.pos, bin(token.cluster)
    an DT Xx 0b111011110
    example NN xxxx 0b111110001
    sentence NN xxxx 0b1101111110010
 
spaCy is particularly good for feature extraction, because it pre-loads lexical
resources, maps strings to integer IDs, and supports output of numpy arrays:

    >>> from spacy.en import attrs
    >>> tokens.to_array((attrs.LEMMA, attrs.POS, attrs.SHAPE, attrs.CLUSTER))
    array([[ 1265,    14,    76,   478],
       [ 1545,    24,   262,   497],
       [ 3385,    24,   262, 14309]])

spaCy also makes it easy to add in-line mark up. Let's say you're convinced by
Stephen King's advice that `adverbs are not your friend <http://www.brainpickings.org/2013/03/13/stephen-king-on-adverbs/>`_, so you want to mark
them in red. We'll use one of the examples he finds particularly egregious:

    >>> tokens = nlp(u"‘Give it back,’ he pleaded abjectly, ‘it’s mine.’")
    >>> red = lambda string: u'\033[91m{0}\033[0m'.format(string)
    >>> red = lambda string: unicode(string).upper() # TODO -- make red work on website...
    >>> print u''.join(red(t) if t.is_adverb else unicode(t) for t in tokens)
    ‘Give it BACK,’ he pleaded ABJECTLY, ‘it’s mine.’


Easy --- except, "back" isn't the sort of word we're looking for, even though
it's undeniably an adverb.  Let's search refine the logic a little, and only
highlight adverbs that modify verbs:

    >>> print u''.join(red(t) if t.is_adverb and t.head.is_verb else unicode(t) for t in tokens)
    ‘Give it back,’ he pleaded ABJECTLY, ‘it’s mine.’

spaCy is also very efficient --- much more efficient than any other language
processing tools available.  The table below compares the time to tokenize, POS
tag and parse a document (amortized over 100k samples).  It also shows accuracy
on the standard evaluation, from the Wall Street Journal:

+----------+----------+---------+----------+----------+------------+
| System   | Tokenize | POS Tag | Parse    | POS Acc. | Parse Acc. |
+----------+----------+---------+----------+----------+------------+
| spaCy    | 0.37ms   | 0.98ms  | 10ms     | 97.3%    | 92.4%      |
+----------+----------+---------+----------+----------+------------+
| NLTK     | 6.2ms    | 443ms   | n/a      | 94.0%    | n/a        |
+----------+----------+---------+----------+----------+------------+
| CoreNLP  | 4.2ms    | 13ms    | todo     | 96.97%   | 92.2%      |
+----------+----------+---------+----------+----------+------------+
| ZPar     | n/a      | 15ms    | 850ms    | 97.3%    | 92.9%      |
+----------+----------+---------+----------+----------+------------+

(The CoreNLP results refer to their recently published shift-reduce neural
network parser.)

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
    api.rst
