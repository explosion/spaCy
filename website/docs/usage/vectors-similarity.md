---
title: Word Vectors and Semantic Similarity
menu:
  - ['Basics', 'basics']
  - ['Custom Vectors', 'custom']
  - ['GPU Usage', 'gpu']
---

## Basics {#basics hidden="true"}

> #### Training word vectors
>
> Dense, real valued vectors representing distributional similarity information
> are now a cornerstone of practical NLP. The most common way to train these
> vectors is the [Word2vec](https://en.wikipedia.org/wiki/Word2vec) family of
> algorithms. If you need to train a word2vec model, we recommend the
> implementation in the Python library
> [Gensim](https://radimrehurek.com/gensim/).

import Vectors101 from 'usage/101/\_vectors-similarity.md'

<Vectors101 />

## Customizing word vectors {#custom}

Word vectors let you import knowledge from raw text into your model. The
knowledge is represented as a table of numbers, with one row per term in your
vocabulary. If two terms are used in similar contexts, the algorithm that learns
the vectors should assign them **rows that are quite similar**, while words that
are used in different contexts will have quite different values. This lets you
use the row-values assigned to the words as a kind of dictionary, to tell you
some things about what the words in your text mean.

Word vectors are particularly useful for terms which **aren't well represented
in your labelled training data**. For instance, if you're doing named entity
recognition, there will always be lots of names that you don't have examples of.
For instance, imagine your training data happens to contain some examples of the
term "Microsoft", but it doesn't contain any examples of the term "Symantec". In
your raw text sample, there are plenty of examples of both terms, and they're
used in similar contexts. The word vectors make that fact available to the
entity recognition model. It still won't see examples of "Symantec" labelled as
a company. However, it'll see that "Symantec" has a word vector that usually
corresponds to company terms, so it can **make the inference**.

In order to make best use of the word vectors, you want the word vectors table
to cover a **very large vocabulary**. However, most words are rare, so most of
the rows in a large word vectors table will be accessed very rarely, or never at
all. You can usually cover more than **95% of the tokens** in your corpus with
just **a few thousand rows** in the vector table. However, it's those **5% of
rare terms** where the word vectors are **most useful**. The problem is that
increasing the size of the vector table produces rapidly diminishing returns in
coverage over these rare terms.

### Converting word vectors for use in spaCy {#converting new="2.0.10"}

Custom word vectors can be trained using a number of open-source libraries, such
as [Gensim](https://radimrehurek.com/gensim), [Fast Text](https://fasttext.cc),
or Tomas Mikolov's original
[word2vec implementation](https://code.google.com/archive/p/word2vec/). Most
word vector libraries output an easy-to-read text-based format, where each line
consists of the word followed by its vector. For everyday use, we want to
convert the vectors model into a binary format that loads faster and takes up
less space on disk. The easiest way to do this is the
[`init-model`](/api/cli#init-model) command-line utility:

```bash
wget https://s3-us-west-1.amazonaws.com/fasttext-vectors/word-vectors-v2/cc.la.300.vec.gz
python -m spacy init-model en /tmp/la_vectors_wiki_lg --vectors-loc cc.la.300.vec.gz
```

This will output a spaCy model in the directory `/tmp/la_vectors_wiki_lg`,
giving you access to some nice Latin vectors 😉 You can then pass the directory
path to [`spacy.load()`](/api/top-level#spacy.load).

```python
nlp_latin = spacy.load("/tmp/la_vectors_wiki_lg")
doc1 = nlp_latin(u"Caecilius est in horto")
doc2 = nlp_latin(u"servus est in atrio")
doc1.similarity(doc2)
```

The model directory will have a `/vocab` directory with the strings, lexical
entries and word vectors from the input vectors model. The
[`init-model`](/api/cli#init-model) command supports a number of archive formats
for the word vectors: the vectors can be in plain text (`.txt`), zipped
(`.zip`), or tarred and zipped (`.tgz`).

### Optimizing vector coverage {#custom-vectors-coverage new="2"}

To help you strike a good balance between coverage and memory usage, spaCy's
[`Vectors`](/api/vectors) class lets you map **multiple keys** to the **same
row** of the table. If you're using the
[`spacy init-model`](/api/cli#init-model) command to create a vocabulary,
pruning the vectors will be taken care of automatically if you set the
`--prune-vectors` flag. You can also do it manually in the following steps:

1. Start with a **word vectors model** that covers a huge vocabulary. For
   instance, the [`en_vectors_web_lg`](/models/en#en_vectors_web_lg) model
   provides 300-dimensional GloVe vectors for over 1 million terms of English.
2. If your vocabulary has values set for the `Lexeme.prob` attribute, the
   lexemes will be sorted by descending probability to determine which vectors
   to prune. Otherwise, lexemes will be sorted by their order in the `Vocab`.
3. Call [`Vocab.prune_vectors`](/api/vocab#prune_vectors) with the number of
   vectors you want to keep.

```python
nlp = spacy.load('en_vectors_web_lg')
n_vectors = 105000  # number of vectors to keep
removed_words = nlp.vocab.prune_vectors(n_vectors)

assert len(nlp.vocab.vectors) <= n_vectors  # unique vectors have been pruned
assert nlp.vocab.vectors.n_keys > n_vectors  # but not the total entries
```

[`Vocab.prune_vectors`](/api/vocab#prune_vectors) reduces the current vector
table to a given number of unique entries, and returns a dictionary containing
the removed words, mapped to `(string, score)` tuples, where `string` is the
entry the removed word was mapped to, and `score` the similarity score between
the two words.

```python
### Removed words
{
    "Shore": ("coast", 0.732257),
    "Precautionary": ("caution", 0.490973),
    "hopelessness": ("sadness", 0.742366),
    "Continous": ("continuous", 0.732549),
    "Disemboweled": ("corpse", 0.499432),
    "biostatistician": ("scientist", 0.339724),
    "somewheres": ("somewheres", 0.402736),
    "observing": ("observe", 0.823096),
    "Leaving": ("leaving", 1.0),
}
```

In the example above, the vector for "Shore" was removed and remapped to the
vector of "coast", which is deemed about 73% similar. "Leaving" was remapped to
the vector of "leaving", which is identical.

If you're using the [`init-model`](/api/cli#init-model) command, you can set the
`--prune-vectors` option to easily reduce the size of the vectors as you add
them to a spaCy model:

```bash
$ python -m spacy init-model /tmp/la_vectors_web_md --vectors-loc la.300d.vec.tgz --prune-vectors 10000
```

This will create a spaCy model with vectors for the first 10,000 words in the
vectors model. All other words in the vectors model are mapped to the closest
vector among those retained.

### Adding vectors {#custom-vectors-add new="2"}

spaCy's new [`Vectors`](/api/vectors) class greatly improves the way word
vectors are stored, accessed and used. The data is stored in two structures:

- An array, which can be either on CPU or [GPU](#gpu).
- A dictionary mapping string-hashes to rows in the table.

Keep in mind that the `Vectors` class itself has no
[`StringStore`](/api/stringstore), so you have to store the hash-to-string
mapping separately. If you need to manage the strings, you should use the
`Vectors` via the [`Vocab`](/api/vocab) class, e.g. `vocab.vectors`. To add
vectors to the vocabulary, you can use the
[`Vocab.set_vector`](/api/vocab#set_vector) method.

```python
### Adding vectors
from spacy.vocab import Vocab

vector_data = {u"dog": numpy.random.uniform(-1, 1, (300,)),
               u"cat": numpy.random.uniform(-1, 1, (300,)),
               u"orange": numpy.random.uniform(-1, 1, (300,))}

vocab = Vocab()
for word, vector in vector_data.items():
    vocab.set_vector(word, vector)
```

### Loading GloVe vectors {#custom-loading-glove new="2"}

spaCy comes with built-in support for loading
[GloVe](https://nlp.stanford.edu/projects/glove/) vectors from a directory. The
[`Vectors.from_glove`](/api/vectors#from_glove) method assumes a binary format,
the vocab provided in a `vocab.txt`, and the naming scheme of
`vectors.{size}.[fd`.bin]. For example:

```yaml
### Directory structure
└── vectors
    ├── vectors.128.f.bin  # vectors file
    └── vocab.txt          # vocabulary
```

| File name           | Dimensions | Data type        |
| ------------------- | ---------- | ---------------- |
| `vectors.128.f.bin` | 128        | float32          |
| `vectors.300.d.bin` | 300        | float64 (double) |

```python
nlp = spacy.load("en_core_web_sm")
nlp.vocab.vectors.from_glove("/path/to/vectors")
```

If your instance of `Language` already contains vectors, they will be
overwritten. To create your own GloVe vectors model package like spaCy's
[`en_vectors_web_lg`](/models/en#en_vectors_web_lg), you can call
[`nlp.to_disk`](/api/language#to_disk), and then package the model using the
[`package`](/api/cli#package) command.

### Using custom similarity methods {#custom-similarity}

By default, [`Token.vector`](/api/token#vector) returns the vector for its
underlying [`Lexeme`](/api/lexeme), while [`Doc.vector`](/api/doc#vector) and
[`Span.vector`](/api/span#vector) return an average of the vectors of their
tokens. You can customize these behaviors by modifying the `doc.user_hooks`,
`doc.user_span_hooks` and `doc.user_token_hooks` dictionaries.

<Infobox title="📖 Custom user hooks">

For more details on **adding hooks** and **overwriting** the built-in `Doc`,
`Span` and `Token` methods, see the usage guide on
[user hooks](/usage/processing-pipelines#user-hooks).

</Infobox>

## Storing vectors on a GPU {#gpu}

If you're using a GPU, it's much more efficient to keep the word vectors on the
device. You can do that by setting the [`Vectors.data`](/api/vectors#attributes)
attribute to a `cupy.ndarray` object if you're using spaCy or
[Chainer]("https://chainer.org"), or a `torch.Tensor` object if you're using
[PyTorch]("http://pytorch.org"). The `data` object just needs to support
`__iter__` and `__getitem__`, so if you're using another library such as
[TensorFlow]("https://www.tensorflow.org"), you could also create a wrapper for
your vectors data.

```python
### spaCy, Thinc or Chainer
import cupy.cuda
from spacy.vectors import Vectors

vector_table = numpy.zeros((3, 300), dtype="f")
vectors = Vectors([u"dog", u"cat", u"orange"], vector_table)
with cupy.cuda.Device(0):
    vectors.data = cupy.asarray(vectors.data)
```

```python
### PyTorch
import torch
from spacy.vectors import Vectors

vector_table = numpy.zeros((3, 300), dtype="f")
vectors = Vectors([u"dog", u"cat", u"orange"], vector_table)
vectors.data = torch.Tensor(vectors.data).cuda(0)
```
