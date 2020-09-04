---
title: Corpus
teaser: An annotated corpus
tag: class
source: spacy/gold/corpus.py
new: 3
---

This class manages annotated corpora and can be used for training and
development datasets in the [DocBin](/api/docbin) (`.spacy`) format. To
customize the data loading during training, you can register your own
[data readers and batchers](/usage/training#custom-code-readers-batchers).

## Config and implementation {#config}

`spacy.Corpus.v1` is a registered function that creates a `Corpus` of training
or evaluation data. It takes the same arguments as the `Corpus` class and
returns a callable that yields [`Example`](/api/example) objects. You can
replace it with your own registered function in the
[`@readers` registry](/api/top-level#registry) to customize the data loading and
streaming.

> #### Example config
>
> ```ini
> [paths]
> train = "corpus/train.spacy"
>
> [training.train_corpus]
> @readers = "spacy.Corpus.v1"
> path = ${paths.train}
> gold_preproc = false
> max_length = 0
> limit = 0
> ```

| Name            | Description                                                                                                                                              |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`          | The directory or filename to read from. Expects data in spaCy's binary [`.spacy` format](/api/data-formats#binary-training). ~~Path~~                    |
|  `gold_preproc` | Whether to set up the Example object with gold-standard sentences and tokens for the predictions. See [`Corpus`](/api/corpus#init) for details. ~~bool~~ |
| `max_length`    | Maximum document length. Longer documents will be split into sentences, if sentence boundaries are available. Defaults to `0` for no limit. ~~int~~      |
| `limit`         | Limit corpus to a subset of examples, e.g. for debugging. Defaults to `0` for no limit. ~~int~~                                                          |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/gold/corpus.py
```

## Corpus.\_\_init\_\_ {#init tag="method"}

Create a `Corpus` for iterating [Example](/api/example) objects from a file or
directory of [`.spacy` data files](/api/data-formats#binary-training). The
`gold_preproc` setting lets you specify whether to set up the `Example` object
with gold-standard sentences and tokens for the predictions. Gold preprocessing
helps the annotations align to the tokenization, and may result in sequences of
more consistent length. However, it may reduce runtime accuracy due to
train/test skew.

> #### Example
>
> ```python
> from spacy.gold import Corpus
>
> # With a single file
> corpus = Corpus("./data/train.spacy")
>
> # With a directory
> corpus = Corpus("./data", limit=10)
> ```

| Name            | Description                                                                                                                                         |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`          | The directory or filename to read from. ~~Union[str, Path]~~                                                                                        |
| _keyword-only_  |                                                                                                                                                     |
|  `gold_preproc` | Whether to set up the Example object with gold-standard sentences and tokens for the predictions. Defaults to `False`. ~~bool~~                     |
| `max_length`    | Maximum document length. Longer documents will be split into sentences, if sentence boundaries are available. Defaults to `0` for no limit. ~~int~~ |
| `limit`         | Limit corpus to a subset of examples, e.g. for debugging. Defaults to `0` for no limit. ~~int~~                                                     |

## Corpus.\_\_call\_\_ {#call tag="method"}

Yield examples from the data.

> #### Example
>
> ```python
> from spacy.gold import Corpus
> import spacy
>
> corpus = Corpus("./train.spacy")
> nlp = spacy.blank("en")
> train_data = corpus(nlp)
> ```

| Name       | Description                            |
| ---------- | -------------------------------------- |
| `nlp`      | The current `nlp` object. ~~Language~~ |
| **YIELDS** | The examples. ~~Example~~              |
