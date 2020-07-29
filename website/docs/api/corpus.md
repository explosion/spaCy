---
title: Corpus
teaser: An annotated corpus
tag: class
source: spacy/gold/corpus.py
new: 3
---

This class manages annotated corpora and can read training and development
datasets in the [DocBin](/api/docbin) (`.spacy`) format.

## Corpus.\_\_init\_\_ {#init tag="method"}

Create a `Corpus`. The input data can be a file or a directory of files.

> #### Example
>
> ```python
> from spacy.gold import Corpus
>
> corpus = Corpus("./train.spacy", "./dev.spacy")
> ```

| Name    | Type         | Description                                                      |
| ------- | ------------ | ---------------------------------------------------------------- |
| `train` | str / `Path` | Training data (`.spacy` file or directory of `.spacy` files).    |
| `dev`   | str / `Path` | Development data (`.spacy` file or directory of `.spacy` files). |
| `limit` | int          | Maximum number of examples returned. `0` for no limit (default). |

## Corpus.train_dataset {#train_dataset tag="method"}

Yield examples from the training data.

> #### Example
>
> ```python
> from spacy.gold import Corpus
> import spacy
>
> corpus = Corpus("./train.spacy", "./dev.spacy")
> nlp = spacy.blank("en")
> train_data = corpus.train_dataset(nlp)
> ```

| Name           | Type       | Description                                                                                                                                |
| -------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `nlp`          | `Language` | The current `nlp` object.                                                                                                                  |
| _keyword-only_ |            |                                                                                                                                            |
| `shuffle`      | bool       | Whether to shuffle the examples. Defaults to `True`.                                                                                       |
| `gold_preproc` | bool       | Whether to train on gold-standard sentences and tokens. Defaults to `False`.                                                               |
| `max_length`   | int        | Maximum document length. Longer documents will be split into sentences, if sentence boundaries are available. `0` for no limit (default).  |
| **YIELDS**     | `Example`  | The examples.                                                                                                                              |

## Corpus.dev_dataset {#dev_dataset tag="method"}

Yield examples from the development data.

> #### Example
>
> ```python
> from spacy.gold import Corpus
> import spacy
>
> corpus = Corpus("./train.spacy", "./dev.spacy")
> nlp = spacy.blank("en")
> dev_data = corpus.dev_dataset(nlp)
> ```

| Name           | Type       | Description                                                                  |
| -------------- | ---------- | ---------------------------------------------------------------------------- |
| `nlp`          | `Language` | The current `nlp` object.                                                    |
| _keyword-only_ |            |                                                                              |
| `gold_preproc` | bool       | Whether to train on gold-standard sentences and tokens. Defaults to `False`. |
| **YIELDS**     | `Example`  | The examples.                                                                |

## Corpus.count_train {#count_train tag="method"}

Get the word count of all training examples.

> #### Example
>
> ```python
> from spacy.gold import Corpus
> import spacy
>
> corpus = Corpus("./train.spacy", "./dev.spacy")
> nlp = spacy.blank("en")
> word_count = corpus.count_train(nlp)
> ```

| Name        | Type       | Description               |
| ----------- | ---------- | ------------------------- |
| `nlp`       | `Language` | The current `nlp` object. |
| **RETURNS** | int        | The word count.           |

<!-- TODO: document remaining methods? / decide which to document -->
