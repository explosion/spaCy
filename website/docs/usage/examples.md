---
title: Examples
teaser: Full code examples you can modify and run
menu:
  - ['Information Extraction', 'information-extraction']
  - ['Pipeline', 'pipeline']
  - ['Training', 'training']
  - ['Vectors & Similarity', 'vectors']
  - ['Deep Learning', 'deep-learning']
---

## Information Extraction {#information-extraction hidden="true"}

### Using spaCy's phrase matcher {#phrase-matcher new="2"}

This example shows how to use the new [`PhraseMatcher`](/api/phrasematcher) to
efficiently find entities from a large terminology list.

```python
https://github.com/explosion/spaCy/tree/master/examples/information_extraction/phrase_matcher.py
```

### Extracting entity relations {#entity-relations}

A simple example of extracting relations between phrases and entities using
spaCy's named entity recognizer and the dependency parse. Here, we extract money
and currency values (entities labelled as `MONEY`) and then check the dependency
tree to find the noun phrase they are referring to – for example:
`"$9.4 million"` → `"Net income"`.

```python
https://github.com/explosion/spaCy/tree/master/examples/information_extraction/entity_relations.py
```

### Navigating the parse tree and subtrees {#subtrees}

This example shows how to navigate the parse tree including subtrees attached to
a word.

```python
https://github.com/explosion/spaCy/tree/master/examples/information_extraction/parse_subtrees.py
```

## Pipeline {#pipeline hidden="true"}

### Custom pipeline components and attribute extensions {#custom-components-entities new="2"}

This example shows the implementation of a pipeline component that sets entity
annotations based on a list of single or multiple-word company names, merges
entities into one token and sets custom attributes on the `Doc`, `Span` and
`Token`.

```python
https://github.com/explosion/spaCy/tree/master/examples/pipeline/custom_component_entities.py
```

### Custom pipeline components and attribute extensions via a REST API {#custom-components-api new="2"}

This example shows the implementation of a pipeline component that fetches
country meta data via the [REST Countries API](https://restcountries.eu) sets
entity annotations for countries, merges entities into one token and sets custom
attributes on the `Doc`, `Span` and `Token` – for example, the capital,
latitude/longitude coordinates and the country flag.

```python
https://github.com/explosion/spaCy/tree/master/examples/pipeline/custom_component_countries_api.py
```

### Custom method extensions {#custom-components-attr-methods new="2"}

A collection of snippets showing examples of extensions adding custom methods to
the `Doc`, `Token` and `Span`.

```python
https://github.com/explosion/spaCy/tree/master/examples/pipeline/custom_attr_methods.py
```

### Multi-processing with Joblib {#multi-processing}

This example shows how to use multiple cores to process text using spaCy and
[Joblib](https://joblib.readthedocs.io/en/latest/). We're exporting
part-of-speech-tagged, true-cased, (very roughly) sentence-separated text, with
each "sentence" on a newline, and spaces between tokens. Data is loaded from the
IMDB movie reviews dataset and will be loaded automatically via Thinc's built-in
dataset loader.

```python
https://github.com/explosion/spaCy/tree/master/examples/pipeline/multi_processing.py
```

## Training {#training hidden="true"}

### Training spaCy's Named Entity Recognizer {#training-ner}

This example shows how to update spaCy's entity recognizer with your own
examples, starting off with an existing, pre-trained model, or from scratch
using a blank `Language` class.

```python
https://github.com/explosion/spaCy/tree/master/examples/training/train_ner.py
```

### Training an additional entity type {#new-entity-type}

This script shows how to add a new entity type to an existing pre-trained NER
model. To keep the example short and simple, only four sentences are provided as
examples. In practice, you'll need many more — a few hundred would be a good
start.

```python
https://github.com/explosion/spaCy/tree/master/examples/training/train_new_entity_type.py
```

### Training spaCy's Dependency Parser {#parser}

This example shows how to update spaCy's dependency parser, starting off with an
existing, pre-trained model, or from scratch using a blank `Language` class.

```python
https://github.com/explosion/spaCy/tree/master/examples/training/train_parser.py
```

### Training spaCy's Part-of-speech Tagger {#tagger}

In this example, we're training spaCy's part-of-speech tagger with a custom tag
map, mapping our own tags to the mapping those tags to the
[Universal Dependencies scheme](http://universaldependencies.github.io/docs/u/pos/index.html).

```python
https://github.com/explosion/spaCy/tree/master/examples/training/train_tagger.py
```

### Training a custom parser for chat intent semantics {#intent-parser}

spaCy's parser component can be used to trained to predict any type of tree
structure over your input text. You can also predict trees over whole documents
or chat logs, with connections between the sentence-roots used to annotate
discourse structure. In this example, we'll build a message parser for a common
"chat intent": finding local businesses. Our message semantics will have the
following types of relations: `ROOT`, `PLACE`, `QUALITY`, `ATTRIBUTE`, `TIME`
and `LOCATION`.

```python
https://github.com/explosion/spaCy/tree/master/examples/training/train_intent_parser.py
```

### Training spaCy's text classifier {#textcat new="2"}

This example shows how to train a multi-label convolutional neural network text
classifier on IMDB movie reviews, using spaCy's new
[`TextCategorizer`](/api/textcategorizer) component. The dataset will be loaded
automatically via Thinc's built-in dataset loader. Predictions are available via
[`Doc.cats`](/api/doc#attributes).

```python
https://github.com/explosion/spaCy/tree/master/examples/training/train_textcat.py
```

## Vectors {#vectors hidden="true"}

### Visualizing spaCy vectors in TensorBoard {#tensorboard}

This script lets you load any spaCy model containing word vectors into
[TensorBoard](https://projector.tensorflow.org/) to create an
[embedding visualization](https://www.tensorflow.org/versions/r1.1/get_started/embedding_viz).

```python
https://github.com/explosion/spaCy/tree/master/examples/vectors_tensorboard.py
```

## Deep Learning {#deep-learning hidden="true"}

### Text classification with Keras {#keras}

This example shows how to use a [Keras](https://keras.io) LSTM sentiment
classification model in spaCy. spaCy splits the document into sentences, and
each sentence is classified using the LSTM. The scores for the sentences are
then aggregated to give the document score. This kind of hierarchical model is
quite difficult in "pure" Keras or TensorFlow, but it's very effective. The
Keras example on this dataset performs quite poorly, because it cuts off the
documents so that they're a fixed size. This hurts review accuracy a lot,
because people often summarize their rating in the final sentence.

```python
https://github.com/explosion/spaCy/tree/master/examples/deep_learning_keras.py
```
