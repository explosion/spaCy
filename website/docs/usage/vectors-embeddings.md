---
title: Vectors and Embeddings
menu:
  - ["What's a Word Vector?", 'whats-a-vector']
  - ['Using Word Vectors', 'usage']
  - ['Converting and Importing', 'converting']
next: /usage/transformers
---

Word vector tables (or "embeddings") let you find similar terms, and can improve
the accuracy of some of your components. You can even use word vectors as a
quick-and-dirty text-classification solution when you don't have any training data.
Word vector tables are included in some of the spaCy [model packages](/models)
we distribute, and you can easily create your own model packages with word
vectors you train or download yourself.

## What's a word vector? {#whats-a-vector}

For spaCy's purposes, a "word vector" is a 1-dimensional slice from a
2-dimensional **vectors table**, with a deterministic mapping from word types to
rows in the table.

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

An old idea in linguistics is that you can "know a word by the company it
keeps": that is, word meanings can be understood relationally, based on their
patterns of usage. This idea inspired a branch of NLP research known as
"distributional semantics" that has aimed to compute databases of lexical
knowledge automatically. The [Word2vec](https://en.wikipedia.org/wiki/Word2vec)
family of algorithms are a key milestone in this line of research. For
simplicity, we will refer to a distributional word representation as a "word
vector", and algorithms that computes word vectors (such as
[GloVe](https://nlp.stanford.edu/projects/glove/),
[FastText](https://fasttext.cc), etc.) as "Word2vec algorithms".

Word2vec algorithms try to produce vectors tables that let you estimate useful
relationships between words using simple linear algebra operations. For
instance, you can often find close synonyms of a word by finding the vectors
closest to it by cosine distance, and then finding the words that are mapped to
those neighboring vectors. Word vectors can also be useful as features in
statistical models.

### Word vectors vs. contextual language models {#vectors-vs-language-models}

The key difference between word vectors and contextual language models such
as [transformers](/usage/transformers)
is that word vectors model **lexical types**, rather than
_tokens_. If you have a list of terms with no context around them,
a transformer model like BERT can't really help you. BERT is designed to understand
language **in context**, which isn't what you have. A word vectors table will be
a much better fit for your task. However, if you do have words in context — whole
sentences or paragraphs of running text — word vectors will only provide a very
rough approximation of what the text is about.

Word vectors are also very computationally efficient, as they map a word to a
vector with a single indexing operation. Word vectors are therefore useful as a
way to **improve the accuracy** of neural network models, especially models that
are small or have received little or no pretraining. In spaCy, word vector
tables are only used as **static features**. spaCy does not backpropagate
gradients to the pretrained word vectors table. The static vectors table is
usually used in combination with a smaller table of learned task-specific
embeddings.

## Using word vectors {#usage}

spaCy stores word vector information in the
[`Vocab.vectors`](/api/vocab#attributes) attribute, so you can access the whole
vectors table from most spaCy objects. You can also access the vector for a
[`Doc`](/api/doc), [`Span`](/api/span), [`Token`](/api/token) or
[`Lexeme`](/api/lexeme) instance via the `vector` attribute. If your `Doc` or
`Span` has multiple tokens, the average of the word vectors will be returned,
excluding any "out of vocabulary" entries that have no vector available. If none
of the words have a vector, a zeroed vector will be returned.

The `vector` attribute is a **read-only** numpy or cupy array (depending on
whether you've configured spaCy to use GPU memory), with dtype `float32`. The
array is read-only so that spaCy can avoid unnecessary copy operations where
possible. You can modify the vectors via the `Vocab` or `Vectors` table.

### Word vectors and similarity

A common use-case of word vectors is to answer _similarity questions_. You can
ask how similar a `token`, `span`, `doc` or `lexeme` is to another object using
the `.similarity()` method. You can even check the similarity of mismatched
types, asking how similar a whole document is to a particular word, how similar
a span is to a document, etc. By default, the `.similarity()` method will use
return the cosine of the `.vector` attribute of the two objects being compared.
You can customize this behavior by setting one or more
[user hooks](/usage/processing-pipelines#custom-components-user-hooks) for the
types you want to customize.

Word vector similarity is a practical technique for many situations, especially
since it's easy to use and relatively efficient to compute. However, it's
important to maintain realistic expectations about what information it can
provide. Words can be related to each over in many ways, so a single
"similarity" score will always be a mix of different signals. The word vectors
model is also not trained for your specific use-case, so you have no way of
telling it which results are more or less useful for your purpose. These
problems are even more accute when you go from measuring the similarity of
single words to the similarity of spans or documents. The vector averaging
process is insensitive to the order of the words, so `doc1.similarity(doc2)`
will mostly be based on the overlap in lexical items between the two documents
objects. Two documents expressing the same meaning with dissimilar wording will
return a lower similarity score than two documents that happen to contain the
same words while expressing different meanings.

### Using word vectors in your models

Many neural network models are able to use word vector tables as additional
features, which sometimes results in significant improvements in accuracy.
spaCy's built-in embedding layer, `spacy.MultiHashEmbed.v1`, can be configured
to use word vector tables using the `also_use_static_vectors` flag. This
setting is also available on the `spacy.MultiHashEmbedCNN.v1` layer, which
builds the default token-to-vector encoding architecture.

```
[tagger.model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = 128
rows = 7000
also_embed_subwords = true
also_use_static_vectors = true
```

<Infobox title="How it works">
The configuration system will look up the string `spacy.MultiHashEmbed.v1`
in the `architectures` registry, and call the returned object with the
rest of the arguments from the block. This will result in a call to the
`spacy.ml.models.tok2vec.MultiHashEmbed` function, which will return
a Thinc model object with the type signature `Model[List[Doc],
List[Floats2d]]`. Because the embedding layer takes a list of `Doc` objects as
input, it does not need to store a copy of the vectors table. The vectors will
be retrieved from the `Doc` objects that are passed in, via the
`doc.vocab.vectors` attribute. This part of the process is handled by the
`spacy.ml.staticvectors.StaticVectors` layer.
</Infobox>

#### Creating a custom embedding layer

The `MultiHashEmbed` layer is spaCy's recommended strategy for constructing
initial word representations for your neural network models, but you can also
implement your own. You can register any function to a string name, and then
reference that function within your config (see the [training]("/usage/training")
section for more details). To try this out, you can save the following little
example to a new Python file:

```
from spacy.ml.staticvectors import StaticVectors
from spacy.util import registry

print("I was imported!")

@registry.architectures("my_example.MyEmbedding.v1")
def MyEmbedding(output_width: int) -> Model[List[Doc], List[Floats2d]]:
    print("I was called!")
    return StaticVectors(nO=output_width)
```

If you pass the path to your file to the `spacy train` command using the `-c`
argument, your file will be imported, which means the decorator registering the
function will be run. Your function is now on equal footing with any of spaCy's
built-ins, so you can drop it in instead of any other model with the same input
and output signature. For instance, you could use it in the tagger model as
follows:

```
[tagger.model.tok2vec.embed]
@architectures = "my_example.MyEmbedding.v1"
output_width = 128
```

Now that you have a custom function wired into the network, you can start
implementing the logic you're interested in. For example, let's say you want to
try a relatively simple embedding strategy that makes use of static word vectors,
but combines them via summation with a smaller table of learned embeddings.

```python
from thinc.api import add, chain, remap_ids, Embed
from spacy.ml.staticvectors import StaticVectors

@registry.architectures("my_example.MyEmbedding.v1")
def MyCustomVectors(
    output_width: int,
    vector_width: int,
    embed_rows: int,
    key2row: Dict[int, int]
) -> Model[List[Doc], List[Floats2d]]:
    return add(
        StaticVectors(nO=output_width),
        chain(
           FeatureExtractor(["ORTH"]),
           remap_ids(key2row),
           Embed(nO=output_width, nV=embed_rows)
        )
    )
```

#### When should you add word vectors to your model?
        
Word vectors are not compatible with most [transformer models](/usage/transformers),
but if you're training another type of NLP network, it's almost always worth
adding word vectors to your model. As well as improving your final accuracy,
word vectors often make experiments more consistent, as the accuracy you
reach will be less sensitive to how the network is randomly initialized. High
variance due to random chance can slow down your progress significantly, as you
need to run many experiments to filter the signal from the noise.

Word vector features need to be enabled prior to training, and the same word vectors
table will need to be available at runtime as well. You cannot add word vector
features once the model has already been trained, and you usually cannot
replace one word vectors table with another without causing a significant loss
of performance.

## Converting word vectors for use in spaCy {#converting}

Custom word vectors can be trained using a number of open-source libraries, such
as [Gensim](https://radimrehurek.com/gensim), [Fast Text](https://fasttext.cc),
or Tomas Mikolov's original
[Word2vec implementation](https://code.google.com/archive/p/word2vec/). Most
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
the vector of "leaving", which is identical. If you're using the
[`init-model`](/api/cli#init-model) command, you can set the `--prune-vectors`
option to easily reduce the size of the vectors as you add them to a spaCy
model:

```bash
$ python -m spacy init-model /tmp/la_vectors_web_md --vectors-loc la.300d.vec.tgz --prune-vectors 10000
```

This will create a spaCy model with vectors for the first 10,000 words in the
vectors model. All other words in the vectors model are mapped to the closest
vector among those retained.

### Adding vectors {#adding-vectors}

You can also add word vectors individually, using the method `vocab.set_vector`.
This is often the easiest approach if you have vectors in an arbitrary format,
as you can read in the vectors with your own logic, and just set them with
a simple loop. This method is likely to be slower than approaches that work
with the whole vectors table at once, but it's a great approach for once-off
conversions before you save out your model to disk.

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
