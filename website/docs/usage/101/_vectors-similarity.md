import Infobox from 'components/infobox'

Similarity is determined by comparing **word vectors** or "word embeddings",
multi-dimensional meaning representations of a word. Word vectors can be
generated using an algorithm like
[word2vec](https://en.wikipedia.org/wiki/Word2vec) and usually look like this:

```python
### banana.vector
array([2.02280000e-01,  -7.66180009e-02,   3.70319992e-01,
       3.28450017e-02,  -4.19569999e-01,   7.20689967e-02,
      -3.74760002e-01,   5.74599989e-02,  -1.24009997e-02,
       5.29489994e-01,  -5.23800015e-01,  -1.97710007e-01,
      -3.41470003e-01,   5.33169985e-01,  -2.53309999e-02,
       1.73800007e-01,   1.67720005e-01,   8.39839995e-01,
       5.51070012e-02,   1.05470002e-01,   3.78719985e-01,
       2.42750004e-01,   1.47449998e-02,   5.59509993e-01,
       1.25210002e-01,  -6.75960004e-01,   3.58420014e-01,
       # ... and so on ...
       3.66849989e-01,   2.52470002e-03,  -6.40089989e-01,
      -2.97650009e-01,   7.89430022e-01,   3.31680000e-01,
      -1.19659996e+00,  -4.71559986e-02,   5.31750023e-01], dtype=float32)
```

<Infobox title="Important note" variant="warning">

To make them compact and fast, spaCy's small [models](/models) (all packages
that end in `sm`) **don't ship with word vectors**, and only include
context-sensitive **tensors**. This means you can still use the `similarity()`
methods to compare documents, spans and tokens – but the result won't be as
good, and individual tokens won't have any vectors assigned. So in order to use
_real_ word vectors, you need to download a larger model:

```diff
- python -m spacy download en_core_web_sm
+ python -m spacy download en_core_web_lg
```

</Infobox>

Models that come with built-in word vectors make them available as the
[`Token.vector`](/api/token#vector) attribute. [`Doc.vector`](/api/doc#vector)
and [`Span.vector`](/api/span#vector) will default to an average of their token
vectors. You can also check if a token has a vector assigned, and get the L2
norm, which can be used to normalize vectors.

```python
### {executable="true"}
import spacy

nlp = spacy.load('en_core_web_md')
tokens = nlp(u'dog cat banana afskfsd')

for token in tokens:
    print(token.text, token.has_vector, token.vector_norm, token.is_oov)
```

> - **Text**: The original token text.
> - **has vector**: Does the token have a vector representation?
> - **Vector norm**: The L2 norm of the token's vector (the square root of the
>   sum of the values squared)
> - **OOV**: Out-of-vocabulary

The words "dog", "cat" and "banana" are all pretty common in English, so they're
part of the model's vocabulary, and come with a vector. The word "afskfsd" on
the other hand is a lot less common and out-of-vocabulary – so its vector
representation consists of 300 dimensions of `0`, which means it's practically
nonexistent. If your application will benefit from a **large vocabulary** with
more vectors, you should consider using one of the larger models or loading in a
full vector package, for example,
[`en_vectors_web_lg`](/models/en#en_vectors_web_lg), which includes over **1
million unique vectors**.

spaCy is able to compare two objects, and make a prediction of **how similar
they are**. Predicting similarity is useful for building recommendation systems
or flagging duplicates. For example, you can suggest a user content that's
similar to what they're currently looking at, or label a support ticket as a
duplicate if it's very similar to an already existing one.

Each `Doc`, `Span` and `Token` comes with a
[`.similarity()`](/api/token#similarity) method that lets you compare it with
another object, and determine the similarity. Of course similarity is always
subjective – whether "dog" and "cat" are similar really depends on how you're
looking at it. spaCy's similarity model usually assumes a pretty general-purpose
definition of similarity.

```python
### {executable="true"}
import spacy

nlp = spacy.load('en_core_web_md')  # make sure to use larger model!
tokens = nlp(u'dog cat banana')

for token1 in tokens:
    for token2 in tokens:
        print(token1.text, token2.text, token1.similarity(token2))
```

In this case, the model's predictions are pretty on point. A dog is very similar
to a cat, whereas a banana is not very similar to either of them. Identical
tokens are obviously 100% similar to each other (just not always exactly `1.0`,
because of vector math and floating point imprecisions).
