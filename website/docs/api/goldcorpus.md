---
title: GoldCorpus
teaser: An annotated corpus, using the JSON file format
tag: class
source: spacy/gold.pyx
new: 2
---

This class manages annotations for tagging, dependency parsing and NER.

## GoldCorpus.\_\_init\_\_ {#init tag="method"}

Create a `GoldCorpus`. IF the input data is an iterable, each item should be a
`(text, paragraphs)` tuple, where each paragraph is a tuple
`(sentences, brackets)`, and each sentence is a tuple
`(ids, words, tags, heads, ner)`. See the implementation of
[`gold.read_json_file`](https://github.com/explosion/spaCy/tree/master/spacy/gold.pyx)
for further details.

| Name        | Type                        | Description                                                  |
| ----------- | --------------------------- | ------------------------------------------------------------ |
| `train`     | unicode / `Path` / iterable | Training data, as a path (file or directory) or iterable.    |
| `dev`       | unicode / `Path` / iterable | Development data, as a path (file or directory) or iterable. |
| **RETURNS** | `GoldCorpus`                | The newly constructed object.                                |
