---
title: Word Vectors and Embeddings
menu:
  - ['Word Vectors', 'vectors']
  - ['Other Embeddings', 'embeddings']
---

## Word vectors and similarity

An old idea in linguistics is that you can "know a word by the company it
keeps": that is, word meanings can be understood relationally, based on their
patterns of usage. This idea inspired a branch of NLP research known as
"distributional semantics" that has aimed to compute databases of lexical knowledge
automatically. The [Word2vec](https://en.wikipedia.org/wiki/Word2vec) family of
algorithms are a key milestone in this line of research. For simplicity, we
will refer to a distributional word representation as a "word vector", and
algorithms that computes word vectors (such as GloVe, FastText, etc) as
"word2vec algorithms".

Word vector tables are included in some of the spaCy model packages we
distribute, and you can easily create your own model packages with word vectors
you train or download yourself. In some cases you can also add word vectors to
an existing pipeline, although each pipeline can only have a single word
vectors table, and a model package that already has word vectors is unlikely to
work correctly if you replace the vectors with new ones.

## What's a word vector?

For spaCy's purposes, a "word vector" is a 1-dimensional slice from
a 2-dimensional _vectors table_, with a deterministic mapping from word types
to rows in the table. 

```python
def what_is_a_word_vector(
    word_id: int,
    key2row: Dict[int, int],
    vectors_table: Floats2d,
    *,
    default_row: int=0
) -> Floats1d:
    return vectors_table[key2row.get(word_id, default_row)]
```

word2vec algorithms try to produce vectors tables that let you estimate useful
relationships between words using simple linear algebra operations. For
instance, you can often find close synonyms of a word by finding the vectors
closest to it by cosine distance, and then finding the words that are mapped to
those neighboring vectors. Word vectors can also be useful as features in
statistical models.

The key difference between word vectors and contextual language models such as
ElMo, BERT and GPT-2 is that word vectors model _lexical types_, rather than 
_tokens_. If you have a list of terms with no context around them, a model like
BERT can't really help you. BERT is designed to understand language in context,
which isn't what you have. A word vectors table will be a much better fit for
your task. However, if you do have words in context --- whole sentences or
paragraphs of running text --- word vectors will only provide a very rough
approximation of what the text is about.

Word vectors are also very computationally efficient, as they map a word to a
vector with a single indexing operation. Word vectors are therefore useful as a
way to  improve the accuracy of neural network models, especially models that
are small or have received little or no pretraining. In spaCy, word vector
tables are only used as static features. spaCy does not backpropagate gradients
to the pretrained word vectors table. The static vectors table is usually used
in combination with a smaller table of learned task-specific embeddings.

## Using word vectors directly

spaCy stores word vector information in the `vocab.vectors` attribute, so you
can access the whole vectors table from most spaCy objects. You can also access
the vector for a `Doc`, `Span`, `Token` or `Lexeme` instance via the `vector`
attribute. If your `Doc` or `Span` has multiple tokens, the average of the
word vectors will be returned, excluding any "out of vocabulary" entries that
have no vector available. If none of the words have a vector, a zeroed vector
will be returned.

The `vector` attribute is a read-only numpy or cupy array (depending on whether
you've configured spaCy to use GPU memory), with dtype `float32`. The array is
read-only so that spaCy can avoid unnecessary copy operations where possible.
You can modify the vectors via the `Vocab` or `Vectors` table.

### Converting word vectors for use in spaCy

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
doc1 = nlp_latin("Caecilius est in horto")
doc2 = nlp_latin("servus est in atrio")
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
   instance, the [`en_vectors_web_lg`](/models/en-starters#en_vectors_web_lg)
   model provides 300-dimensional GloVe vectors for over 1 million terms of
   English.
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

### Adding vectors

```python
### Adding vectors
from spacy.vocab import Vocab

vector_data = {"dog": numpy.random.uniform(-1, 1, (300,)),
               "cat": numpy.random.uniform(-1, 1, (300,)),
               "orange": numpy.random.uniform(-1, 1, (300,))}
vocab = Vocab()
for word, vector in vector_data.items():
    vocab.set_vector(word, vector)
```

### Using custom similarity methods {#custom-similarity}

By default, [`Token.vector`](/api/token#vector) returns the vector for its
underlying [`Lexeme`](/api/lexeme), while [`Doc.vector`](/api/doc#vector) and
[`Span.vector`](/api/span#vector) return an average of the vectors of their
tokens. You can customize these behaviors by modifying the `doc.user_hooks`,
`doc.user_span_hooks` and `doc.user_token_hooks` dictionaries.

<Infobox title="Custom user hooks" emoji="📖">

For more details on **adding hooks** and **overwriting** the built-in `Doc`,
`Span` and `Token` methods, see the usage guide on
[user hooks](/usage/processing-pipelines#custom-components-user-hooks).

</Infobox>

### Storing vectors on a GPU {#gpu}

