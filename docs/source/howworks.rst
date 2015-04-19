How spaCy Works
===============

The following are some hasty preliminary notes on how spaCy works.  The short
story is, there are no new killer algorithms.  The way that the tokenizer works
is novel and a bit neat, and the parser has a new feature set, but otherwise
the key algorithms are well known in the recent literature.

Some might also wonder how I get Python code to run so fast.  I don't --- spaCy
is written in `Cython`_, an optionally statically-typed language that compiles
to C or C++, which is then loaded as a C extension module.
This makes it `easy to achieve the performance of native C code`_, but allows the
use of Python language features, via the Python C API.  The Python unicode
library was particularly useful to me.  I think it would have been much more
difficult to write spaCy in another language.

.. _Cython: http://cython.org/

.. _easy to achieve the performance of native C code: https://honnibal.wordpress.com/2014/10/21/writing-c-in-cython/

Tokenizer and Lexicon
---------------------

Tokenization is the task of splitting a string into meaningful pieces, called
tokens, which you can then compute with.  In practice, the task is usually to
match the tokenization performed in some treebank, or other corpus.  If we want
to apply a tagger, entity recogniser, parser etc, then we want our run-time
text to match the training conventions.  If we want to use a model that's been
trained to expect "isn't" to be split into two tokens, ["is", "n't"], then that's
how we need to prepare our data.

In order to train spaCy's models with the best data available, I therefore
tokenize English according to the Penn Treebank scheme.  It's not perfect, but
it's what everybody is using, and it's good enough.

What we don't do
################

The Penn Treebank was distributed with a script called tokenizer.sed, which
tokenizes ASCII newswire text roughly according to the Penn Treebank standard.
Almost all tokenizers are based on these regular expressions, with various
updates to account for unicode characters, and the fact that it's no longer
1986 --- today's text has URLs, emails, emoji, etc.

Usually, the resulting regular expressions are applied in multiple passes, which
is quite inefficient.  Often no care is taken to preserve indices into the original
string.  If you lose these indices, it'll be difficult to calculate mark-up based
on your annotations.

Tokenizer Algorithm
###################

spaCy's tokenizer assumes that no tokens will cross whitespace --- there will
be no multi-word tokens.  If we want these, we can post-process the
token-stream later, merging as necessary.  This assumption allows us to deal
only with small chunks of text.  We can cache the processing of these, and
simplify our expressions somewhat.

Here is what the outer-loop would look like in Python. (You can see the
production implementation, in Cython, here.)

.. code:: python

    cache = {}
    def tokenize(text):
        tokens = []
        for substring in text.split(' '):
            if substring in cache:
                tokens.extend(cache[substring])
            else:
                subtokens = _tokenize_substring(substring)
                tokens.extend(subtokens)
                cache[substring] = subtokens
        return tokens

The actual work is performed in _tokenize_substring.  For this, I divide the
tokenization rules into three pieces:

1. A prefixes expression, which matches from the start of the string;
2. A suffixes expression, which matches from the end of the string;
3. A special-cases table, which matches the whole string.

The algorithm then proceeds roughly like this (consider this like pseudo-code;
this was written quickly and has not been executed):

.. code:: python

    # Tokens which can be attached at the beginning or end of another
    prefix_re = _make_re([",", '"', '(', ...])
    suffix_re = _make_re(s[",", "'", ":", "'s", ...])

    # Contractions etc are simply enumerated, since they're a finite set.  We
    # can also specify anything we like here, which is nice --- different data
    # has different quirks, so we want to be able to add ad hoc exceptions.
    special_cases = {
        "can't": ("ca", "n't"),
        "won't": ("wo", "n't"),
        "he'd've": ("he", "'d", "'ve"),
        ...
        ":)": (":)",) # We can add any arbitrary thing to this list.
    }

    def _tokenize_substring(substring):
        prefixes = []
        suffixes = []
        while substring not in special_cases:
            prefix, substring = _apply_re(substring, prefix_re)
            if prefix:
                prefixes.append(prefix)
            else:
                suffix, substring = _apply_re(substring, suffix_re)
                if suffix:
                    suffixes.append(suffix)
                else:
                    break


This procedure splits off tokens from the start and end of the string, at each
point checking whether the remaining string is in our special-cases table. If
it is, we stop splitting, and return the tokenization at that point.

The advantage of this design is that the prefixes, suffixes and special-cases
can be declared separately, in easy-to-understand files.  If a new entry is
added to the special-cases, you can be sure that it won't have some unforeseen
consequence to a complicated regular-expression grammar.

Coupling the Tokenizer and Lexicon
##################################

As mentioned above, the tokenizer is designed to support easy caching.  If all
we were caching were the matched substrings, this would not be so advantageous.
Instead, what we do is create a struct which houses all of our lexical
features, and cache *that*.  The tokens are then simply pointers to these rich
lexical types.

In a sample of text, vocabulary size grows exponentially slower than word
count.  So any computations we can perform over the vocabulary and apply to the
word count are very efficient.


Part-of-speech Tagger
---------------------

.. _how to write a good part of speech tagger: https://honnibal.wordpress.com/2013/09/11/a-good-part-of-speechpos-tagger-in-about-200-lines-of-python/ .

In 2013, I wrote a blog post describing `how to write a good part of speech
tagger`_.
My recommendation then was to use greedy decoding with the averaged perceptron.
I think this is still the best approach, so it's what I implemented in spaCy.

The tutorial also recommends the use of Brown cluster features, and case
normalization features, as these make the model more robust and domain
independent.  spaCy's tagger makes heavy use of these features.

Dependency Parser
-----------------

.. _2014 blog post: https://honnibal.wordpress.com/2013/12/18/a-simple-fast-algorithm-for-natural-language-dependency-parsing/

The parser uses the algorithm described in my `2014 blog post`_.
This algorithm, shift-reduce dependency parsing, is becoming widely adopted due
to its compelling speed/accuracy trade-off.

Some quick details about spaCy's take on this, for those who happen to know
these models well.  I'll write up a better description shortly.

1. I use greedy decoding, not beam search;
2. I use the arc-eager transition system;
3. I use the Goldberg and Nivre (2012) dynamic oracle.
4. I use the non-monotonic update from my CoNLL 2013 paper (Honnibal, Goldberg
   and Johnson 2013).

So far, this is exactly the configuration from the CoNLL 2013 paper, which
scored 91.0. So how have I gotten it to 92.4?  The following tweaks:

1. I use Brown cluster features --- these help a lot;
2. I redesigned the feature set. I've long known that the Zhang and Nivre
   (2011) feature set was suboptimal, but a few features don't make a very
   compelling publication.  Still, they're important.
3. When I do the dynamic oracle training, I also make
   the upate cost-sensitive: if the oracle determines that the move the parser
   took has a cost of N, then the weights for the gold class are incremented by
   +N, and the weights for the predicted class are incremented by -N.  This
   only made a small (0.1-0.2%) difference.

Implementation
##############

I don't do anything algorithmically novel to improve the efficiency of the
parser.  However, I was very careful in the implementation.

A greedy shift-reduce parser with a linear model boils down to the following
loop:

.. code:: python

    def parse(words, model, feature_funcs, n_classes):
        state = init_state(words)
        for _ in range(len(words) * 2):
            features = [templ(state) for templ in feature_funcs]
            scores = [0 for _ in range(n_classes)]
            for feat in features:
                weights = model[feat]
                for i, weight in enumerate(weights):
                    scores[i] += weight
            class_, score = max(enumerate(scores), key=lambda item: item[1])
            transition(state, class_)

The parser makes 2N transitions for a sentence of length N. In order to select
the transition, it extracts a vector of K features from the state. Each feature
is used as a key into a hash table managed by the model.  The features map to
a vector of weights, of length C.  We then dot product the feature weights to the
scores vector we are building for that instance.

The inner-most loop here is not so bad: we only have a few dozen classes, so
it's just a short dot product.  Both of the vectors are in the cache, so this
is a snack to a modern CPU.

The bottle-neck in this algorithm is the 2NK look-ups into the hash-table that
we must make, as these almost always have to hit main memory.  The feature-set
is enormously large, because all of our features are one-hot boolean
indicators.  Some of the features will be common, so they'll lurk around in the
CPU's cache hierarchy.  But a lot of them won't be, and accessing main memory
takes a lot of cycles.

.. _Jeff Preshing's excellent post: http://preshing.com/20130107/this-hash-table-is-faster-than-a-judy-array/ .

I used to use the Google dense_hash_map implementation.  This seemed a solid
choice: it came from a big brand, it was in C++, and it seemed very
complicated.  Later, I read `Jeff Preshing's excellent post`_ on open-addressing
with linear probing.
This really spoke to me.  I had assumed that a fast hash table implementation
would necessarily be very complicated, but no --- this is another situation
where the simple strategy wins.

I've packaged my Cython implementation separately from spaCy, in the package
`preshed`_ --- for "pre-hashed", but also as a nod to Preshing.  I've also taken
great care over the feature extraction and perceptron code, which I'm distributing
in a package named `thinc`_ (since it's for learning very sparse models with
Cython).

.. _preshed: https://github.com/syllog1sm/preshed

.. _thinc: https://github.com/honnibal/thinc

By the way: from comparing notes with a few people, it seems common to
implement linear models in a way that's suboptimal for multi-class
classification.  The mistake is to store in the hash-table one weight per
(feature, class) pair, rather than mapping the feature to a vector of weights,
for all of the classes.  This is bad because it means you need to hit the table
C times, one per class, as you always need to evaluate a feature against all of
the classes.  In the case of the parser, this means the hash table is accessed
2NKC times, instead of the 2NK times if you have a weights vector.  You should
also be careful to store the weights contiguously in memory --- you don't want
a linked list here.  I use a block-sparse format, because my problems tend to
have a few dozen classes.

I guess if I had to summarize my experience, I'd say that the efficiency of
these models is really all about the data structures.  We want to stay small,
and stay contiguous.  Minimize redundancy and minimize pointer chasing.
That's why Cython is so well suited to this: we get to lay out our data
structures, and manage the memory ourselves, with full C-level control.
