.. spaCy documentation master file, created by
   sphinx-quickstart on Tue Aug 19 16:27:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

================================
spaCy: Industrial-strength NLP
================================

spaCy is a library for industrial-strength text processing in Python and Cython.
It features extremely efficient, up-to-date algorithms, and a rethink of how those
algorithms should be accessed.

A typical text-processing API looks something like this:

    >>> import nltk
    >>> nltk.pos_tag(nltk.word_tokenize('''Some string of language.'''))
    [('Some', 'DT'), ('string', 'VBG'), ('of', 'IN'), ('language', 'NN'), ('.', '.')]

This API often leaves you with a lot of busy-work.  If you're doing some machine
learning or information extraction, all the strings have to be mapped to integers,
and you have to save and load the mapping at training and runtime.  If you want
to display mark-up based on the annotation, you have to realign the tokens to your
original string.

I've been writing NLP systems for almost ten years now, so I've done these
things dozens of times.  When designing spaCy, I thought carefully about how to
make the right thing easy.  

We begin by initializing a global vocabulary store:

    >>> from spacy.en import EN
    >>> EN.load()

The vocabulary reads in a data file with all sorts of pre-computed lexical
features.  You can load anything you like here, but by default I give you:

* String IDs for the word's string, its prefix, suffix and "shape";
* Length (in unicode code-points)
* A cluster ID, representing distributional similarity;
* A cluster ID, representing its typical POS tag distribution;
* Good-turing smoothed unigram probability;
* 64 boolean features, for assorted orthographic and distributional features.

With so many features pre-computed, you usually don't have to do any string
processing at all.  You give spaCy your string, and tell it to give you either
a numpy array, or a counts dictionary:

    >>> from spacy.en import feature_names as fn
    >>> tokens = EN.tokenize(u'''Some string of language.''')
    >>> tokens.to_array((fn.WORD, fn.SUFFIX, fn.CLUSTER))
    ...
    >>> tokens.count_by(fn.WORD)

If you do need strings, you can simply iterate over the Tokens object:

    >>> for token in tokens:
    ...   

I mostly use this for debugging and testing.

spaCy returns these rich Tokens objects much faster than most other tokenizers
can give you a list of strings --- in fact, spaCy's POS tagger is *4 times
faster* than CoreNLP's tokenizer:

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




.. toctree::
    :hidden:
    :maxdepth: 3

    features.rst
    license_stories.rst 
