---
title: Data formats
teaser: Details on spaCy's input and output data formats
menu:
  - ['Training data', 'training']
  - ['Vocabulary', 'vocab']
---

This section documents input and output formats of data used by spaCy, including
training data and lexical vocabulary data. For an overview of label schemes used
by the models, see the [models directory](/models). Each model documents the
label schemes used in its components, depending on the data it was trained on.

## Training data {#training}

### Binary training format {#binary-training new="3"}

<!-- TODO: document DocBin format -->

### JSON input format for training {#json-input}

spaCy takes training data in JSON format. The built-in
[`convert`](/api/cli#convert) command helps you convert the `.conllu` format
used by the
[Universal Dependencies corpora](https://github.com/UniversalDependencies) to
spaCy's training format. To convert one or more existing `Doc` objects to
spaCy's JSON format, you can use the
[`gold.docs_to_json`](/api/top-level#docs_to_json) helper.

> #### Annotating entities
>
> Named entities are provided in the
> [BILUO](/usage/linguistic-features#accessing-ner) notation. Tokens outside an
> entity are set to `"O"` and tokens that are part of an entity are set to the
> entity label, prefixed by the BILUO marker. For example `"B-ORG"` describes
> the first token of a multi-token `ORG` entity and `"U-PERSON"` a single token
> representing a `PERSON` entity. The
> [`biluo_tags_from_offsets`](/api/top-level#biluo_tags_from_offsets) function
> can help you convert entity offsets to the right format.

```python
### Example structure
[{
    "id": int,                      # ID of the document within the corpus
    "paragraphs": [{                # list of paragraphs in the corpus
        "raw": string,              # raw text of the paragraph
        "sentences": [{             # list of sentences in the paragraph
            "tokens": [{            # list of tokens in the sentence
                "id": int,          # index of the token in the document
                "dep": string,      # dependency label
                "head": int,        # offset of token head relative to token index
                "tag": string,      # part-of-speech tag
                "orth": string,     # verbatim text of the token
                "ner": string       # BILUO label, e.g. "O" or "B-ORG"
            }],
            "brackets": [{          # phrase structure (NOT USED by current models)
                "first": int,       # index of first token
                "last": int,        # index of last token
                "label": string     # phrase label
            }]
        }],
        "cats": [{                  # new in v2.2: categories for text classifier
            "label": string,        # text category label
            "value": float / bool   # label applies (1.0/true) or not (0.0/false)
        }]
    }]
}]
```

Here's an example of dependencies, part-of-speech tags and names entities, taken
from the English Wall Street Journal portion of the Penn Treebank:

```json
https://github.com/explosion/spaCy/tree/master/examples/training/training-data.json
```

## Lexical data for vocabulary {#vocab-jsonl new="2"}

To populate a model's vocabulary, you can use the
[`spacy init-model`](/api/cli#init-model) command and load in a
[newline-delimited JSON](http://jsonlines.org/) (JSONL) file containing one
lexical entry per line via the `--jsonl-loc` option. The first line defines the
language and vocabulary settings. All other lines are expected to be JSON
objects describing an individual lexeme. The lexical attributes will be then set
as attributes on spaCy's [`Lexeme`](/api/lexeme#attributes) object. The `vocab`
command outputs a ready-to-use spaCy model with a `Vocab` containing the lexical
data.

```python
### First line
{"lang": "en", "settings": {"oov_prob": -20.502029418945312}}
```

```python
### Entry structure
{
    "orth": string,     # the word text
    "id": int,          # can correspond to row in vectors table
    "lower": string,
    "norm": string,
    "shape": string
    "prefix": string,
    "suffix": string,
    "length": int,
    "cluster": string,
    "prob": float,
    "is_alpha": bool,
    "is_ascii": bool,
    "is_digit": bool,
    "is_lower": bool,
    "is_punct": bool,
    "is_space": bool,
    "is_title": bool,
    "is_upper": bool,
    "like_url": bool,
    "like_num": bool,
    "like_email": bool,
    "is_stop": bool,
    "is_oov": bool,
    "is_quote": bool,
    "is_left_punct": bool,
    "is_right_punct": bool
}
```

Here's an example of the 20 most frequent lexemes in the English training data:

```json
https://github.com/explosion/spaCy/tree/master/examples/training/vocab-data.jsonl
```
