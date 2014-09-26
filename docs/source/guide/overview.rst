Don't Settle for a List of Strings
==================================


    *"Other NLP tokenizers return lists of strings, which is downright
    barbaric."* --- me


spaCy splits text into a list of lexical types, which come with a variety of
features pre-computed.  It's designed to **make the right thing easy**, where the right
thing is:

* A global vocabulary store;

* Cached orthographic features;

* Clever use of distributional data.
  
Let's say you're writing an entity tagger for English. Case distinctions are an
important feature here: you need to know whether the word you're tagging is
upper-cased, lower-cased, title-cased, non-alphabetic, etc.
The right thing is to call the string.isupper(), string.islower(), string.isalpha()
etc functions once for every *type* in your vocabulary, instead
of once for every *token* in the text you're tagging.
When you encounter a new word, you want to create a lexeme object, calculate its
features, and save it.

That's the *right* way to do it, so it's what spaCy does for you.

Other tokenizers give you a list of strings, which makes it really easy to do
the wrong thing. And the wrong thing isn't just a little bit worse: it's
**exponentially** worse, because of
`Zipf's law <http://en.wikipedia.org/wiki/Zipf's_law>`_. 

.. raw:: html

    <center>
    <figure>
      <embed 
        width="650em" height="auto"
        type="image/svg+xml" src="chart.svg"/>
    </figure>
    </center>

Over the Gigaword corpus, if you compute some feature on a per-token basis, you'll
make **500x more calls** to that function than if you had computed it on a per-token
basis.
(Mouse-over a line to see its value at that point. And yes, it's a bit snarky
to present the graph in a linear scale --- but it isn't misleading.)
  
Zipf's Law also makes distributional information a really powerful source of
type-based features. It's really handy to know where a word falls in the language's
frequency distribution, especially compared to variants of the word.  For instance,
we might be processing a Twitter comment that contains the string "nasa". We have
little hope of recognising this as an entity except by noting that the string "NASA"
is much more common, and that both strings are quite rare.

.. Each spaCy Lexeme comes with a rich, curated set of orthographic and
.. distributional features.  Different languages get a different set of features,
.. to take into account different orthographic conventions and morphological
.. complexity. It's also easy to define your own features.

.. And, of course, we take care to get the details right.  Indices into the original
.. text are always easy to calculate, so it's easy to, say, mark entities with in-line
.. mark-up. You'll also receive tokens for newlines, tabs and other non-space whitespace,
.. making it easy to do paragraph and sentence recognition.  And, of course, we deal
.. smartly with all the random unicode whitespace and punctuation characters you might
.. not have thought of.


Benchmarks
----------

We here ask two things:

1. How fast is the spaCy tokenizer itself, relative to other tokenizers?

2. How fast are applications using spaCy's pre-computed lexical features,
   compared to applications that re-compute their features on every token?

+--------+-------+--------------+--------------+
| System | Time	 | Words/second | Speed Factor |
+--------+-------+--------------+--------------+
| NLTK	 | 6m4s  | 89,000       | 1.00         |
+--------+-------+--------------+--------------+
| spaCy	 |       |           	|              |
+--------+-------+--------------+--------------+


spaCy uses more memory than a standard tokenizer, but is far more efficient. We
compare against the NLTK tokenizer and the Penn Treebank's tokenizer.sed script.
We also give the performance of Python's native string.split, for reference.


Pros and Cons
-------------

Pros:

- Stuff

Cons:

- It's new (released September 2014)
- Higher memory usage (up to 1gb)
- More complicated
