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

| Name        | Type         | Description                                                      |
| ----------- | ------------ | ---------------------------------------------------------------- |
| `train`     | str / `Path` | Training data (`.spacy` file or directory of `.spacy` files).    |
| `dev`       | str / `Path` | Development data (`.spacy` file or directory of `.spacy` files). |
| `limit`     | int          | Maximum number of examples returned.                             |
| **RETURNS** | `Corpus`     | The newly constructed object.                                    |

<!-- TODO: document remaining methods / decide which to document -->

## Corpus.walk_corpus {#walk_corpus tag="staticmethod"}

## Corpus.make_examples {#make_examples tag="method"}

## Corpus.make_examples_gold_preproc {#make_examples_gold_preproc tag="method"}

## Corpus.read_docbin {#read_docbin tag="method"}

## Corpus.count_train {#count_train tag="method"}

## Corpus.train_dataset {#train_dataset tag="method"}

## Corpus.dev_dataset {#dev_dataset tag="method"}
