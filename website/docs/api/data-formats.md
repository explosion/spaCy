---
title: Data formats
teaser: Details on spaCy's input and output data formats
menu:
  - ['Training Data', 'training']
  - ['Pretraining Data', 'pretraining']
  - ['Training Config', 'config']
  - ['Vocabulary', 'vocab']
---

This section documents input and output formats of data used by spaCy, including
training data and lexical vocabulary data. For an overview of label schemes used
by the models, see the [models directory](/models). Each model documents the
label schemes used in its components, depending on the data it was trained on.

## Training data {#training}

### Binary training format {#binary-training new="3"}

The built-in [`convert`](/api/cli#convert) command helps you convert the
`.conllu` format used by the
[Universal Dependencies corpora](https://github.com/UniversalDependencies) as
well as spaCy's previous [JSON format](#json-input).

<!-- TODO: document DocBin format -->

### JSON training format {#json-input tag="deprecated"}

<Infobox variant="warning" title="Changed in v3.0">

As of v3.0, the JSON input format is deprecated and is replaced by the
[binary format](#binary-training). Instead of converting [`Doc`](/api/doc)
objects to JSON, you can now now serialize them directly using the
[`DocBin`](/api/docbin) container and then use them as input data.

[`spacy convert`](/api/cli) lets you convert your JSON data to the new `.spacy`
format:

```bash
$ python -m spacy convert ./data.json ./output
```

</Infobox>

> #### Annotating entities {#biluo}
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

<Accordion title="Sample JSON data" spaced>

Here's an example of dependencies, part-of-speech tags and names entities, taken
from the English Wall Street Journal portion of the Penn Treebank:

```json
https://github.com/explosion/spaCy/blob/v2.3.x/examples/training/training-data.json
```

</Accordion>

### Annotation format for creating training examples {#dict-input}

An [`Example`](/api/example) object holds the information for one training
instance. It stores two [`Doc`](/api/doc) objects: one for holding the
gold-standard reference data, and one for holding the predictions of the
pipeline. Examples can be created using the
[`Example.from_dict`](/api/example#from_dict) method with a reference `Doc` and
a dictionary of gold-standard annotations. There are currently two formats
supported for this dictionary of annotations: one with a simple, **flat
structure** of keywords, and one with a more **hierarchical structure**.

> #### Example
>
> ```python
> example = Example.from_dict(doc, gold_dict)
> ```

<Infobox title="Important note" variant="warning">

`Example` objects are used as part of the
[internal training API](/usage/training#api) and they're expected when you call
[`nlp.update`](/api/language#update). However, for most use cases, you
**shouldn't** have to write your own training scripts. It's recommended to train
your models via the [`spacy train`](/api/cli#train) command with a config file
to keep track of your settings and hyperparameters and your own
[registered functions](/usage/training/#custom-code) to customize the setup.

</Infobox>

#### Flat structure {#dict-flat}

> #### Example
>
> ```python
> {
>    "text": str,
>    "words": List[str],
>    "lemmas": List[str],
>    "spaces": List[bool],
>    "tags": List[str],
>    "pos": List[str],
>    "morphs": List[str],
>    "sent_starts": List[bool],
>    "deps": List[string],
>    "heads": List[int],
>    "entities": List[str],
>    "entities": List[(int, int, str)],
>    "cats": Dict[str, float],
>    "links": Dict[(int, int), dict],
> }
> ```

| Name          | Type                         | Description                                                                                                                                                                                    |
| ------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `text`        | str                          | Raw text.                                                                                                                                                                                      |
| `words`       | `List[str]`                  | List of gold-standard tokens.                                                                                                                                                                  |
| `lemmas`      | `List[str]`                  | List of lemmas.                                                                                                                                                                                |
| `spaces`      | `List[bool]`                 | List of boolean values indicating whether the corresponding tokens is followed by a space or not.                                                                                              |
| `tags`        | `List[str]`                  | List of fine-grained [POS tags](/usage/linguistic-features#pos-tagging).                                                                                                                       |
| `pos`         | `List[str]`                  | List of coarse-grained [POS tags](/usage/linguistic-features#pos-tagging).                                                                                                                     |
| `morphs`      | `List[str]`                  | List of [morphological features](/usage/linguistic-features#rule-based-morphology).                                                                                                            |
| `sent_starts` | `List[bool]`                 | List of boolean values indicating whether each token is the first of a sentence or not.                                                                                                        |
| `deps`        | `List[str]`                  | List of string values indicating the [dependency relation](/usage/linguistic-features#dependency-parse) of a token to its head.                                                                |
| `heads`       | `List[int]`                  | List of integer values indicating the dependency head of each token, referring to the absolute index of each token in the text.                                                                |
| `entities`    | `List[str]`                  | Option 1: List of [BILUO tags](#biluo) per token of the format `"{action}-{label}"`, or `None` for unannotated tokens.                                                                         |
| `entities`    | `List[Tuple[int, int, str]]` | Option 2: List of `"(start, end, label)"` tuples defining all entities in the text.                                                                                                            |
| `cats`        | `Dict[str, float]`           | Dictionary of `label`/`value` pairs indicating how relevant a certain [text category](/api/textcategorizer) is for the text.                                                                   |
| `links`       | `Dict[(int, int), Dict]`     | Dictionary of `offset`/`dict` pairs defining [named entity links](/usage/linguistic-features#entity-linking). The character offsets are linked to a dictionary of relevant knowledge base IDs. |

<Infobox variant="warning" title="Important notes and caveats">

- Multiple formats are possible for the "entities" entry, but you have to pick
  one.
- Any values for sentence starts will be ignored if there are annotations for
  dependency relations.
- If the dictionary contains values for `"text"` and `"words"`, but not
  `"spaces"`, the latter are inferred automatically. If "words" is not provided
  either, the values are inferred from the `Doc` argument.

</Infobox>

<!-- TODO: finish reformatting below -->

##### Examples

```python
# Training data for a part-of-speech tagger
doc = Doc(vocab, words=["I", "like", "stuff"])
example = Example.from_dict(doc, {"tags": ["NOUN", "VERB", "NOUN"]})

# Training data for an entity recognizer (option 1)
doc = nlp("Laura flew to Silicon Valley.")
biluo_tags = ["U-PERS", "O", "O", "B-LOC", "L-LOC"]
example = Example.from_dict(doc, {"entities": biluo_tags})

# Training data for an entity recognizer (option 2)
doc = nlp("Laura flew to Silicon Valley.")
entity_tuples = [
        (0, 5, "PERSON"),
        (14, 28, "LOC"),
    ]
example = Example.from_dict(doc, {"entities": entity_tuples})

# Training data for text categorization
doc = nlp("I'm pretty happy about that!")
example = Example.from_dict(doc, {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}})

# Training data for an Entity Linking component
doc = nlp("Russ Cochran his reprints include EC Comics.")
example = Example.from_dict(doc, {"links": {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}}})
```

#### Hierachical structure {#dict-hierarch}

Internally, a more hierarchical dictionary structure is used to store
gold-standard annotations. Its format is similar to the structure described in
the previous section, but there are two main sections `token_annotation` and
`doc_annotation`, and the keys for token annotations should be uppercase
[`Token` attributes](/api/token#attributes) such as "ORTH" and "TAG".

```python
### Hierarchical dictionary
{
    "text": string,                            # Raw text.
    "token_annotation": {
        "ORTH": List[string],                  # List of gold tokens.
        "LEMMA": List[string],                 # List of lemmas.
        "SPACY": List[bool],                   # List of boolean values indicating whether the corresponding tokens is followed by a space or not.
        "TAG": List[string],                   # List of fine-grained [POS tags](/usage/linguistic-features#pos-tagging).
        "POS": List[string],                   # List of coarse-grained [POS tags](/usage/linguistic-features#pos-tagging).
        "MORPH": List[string],                 # List of [morphological features](/usage/linguistic-features#rule-based-morphology).
        "SENT_START": List[bool],              # List of boolean values indicating whether each token is the first of a sentence or not.
        "DEP": List[string],                   # List of string values indicating the [dependency relation](/usage/linguistic-features#dependency-parse) of a token to its head.
        "HEAD": List[int],                     # List of integer values indicating the dependency head of each token, referring to the absolute index of each token in the text.
    },
    "doc_annotation": {
        "entities": List[(int, int, string)],  # List of [BILUO tags](#biluo) per token of the format `"{action}-{label}"`, or `None` for unannotated tokens.
        "cats": Dict[str, float],              # Dictionary of `label:value` pairs indicating how relevant a certain [category](/api/textcategorizer) is for the text.
        "links": Dict[(int, int), Dict],       # Dictionary of `offset:dict` pairs defining [named entity links](/usage/linguistic-features#entity-linking). The charachter offsets are linked to a dictionary of relevant knowledge base IDs.
    }
}
```

There are a few caveats to take into account:

- Any values for sentence starts will be ignored if there are annotations for
  dependency relations.
- If the dictionary contains values for "text" and "ORTH", but not "SPACY", the
  latter are inferred automatically. If "ORTH" is not provided either, the
  values are inferred from the `doc` argument.

## Pretraining data {#pretraining}

The [`spacy pretrain`](/api/cli#pretrain) command lets you pretrain the tok2vec
layer of pipeline components from raw text. Raw text can be provided as a
`.jsonl` (newline-delimited JSON) file containing one input text per line
(roughly paragraph length is good). Optionally, custom tokenization can be
provided.

> #### Tip: Writing JSONL
>
> Our utility library [`srsly`](https://github.com/explosion/srsly) provides a
> handy `write_jsonl` helper that takes a file path and list of dictionaries and
> writes out JSONL-formatted data.
>
> ```python
> import srsly
> data = [{"text": "Some text"}, {"text": "More..."}]
> srsly.write_jsonl("/path/to/text.jsonl", data)
> ```

| Key      | Type | Description                                                |
| -------- | ---- | ---------------------------------------------------------- |
| `text`   | str  | The raw input text. Is not required if `tokens` available. |
| `tokens` | list | Optional tokenization, one string per token.               |

```json
### Example
{"text": "Can I ask where you work now and what you do, and if you enjoy it?"}
{"text": "They may just pull out of the Seattle market completely, at least until they have autonomous vehicles."}
{"text": "My cynical view on this is that it will never be free to the public. Reason: what would be the draw of joining the military? Right now their selling point is free Healthcare and Education. Ironically both are run horribly and most, that I've talked to, come out wishing they never went in."}
{"tokens": ["If", "tokens", "are", "provided", "then", "we", "can", "skip", "the", "raw", "input", "text"]}
```

## Training config {#config new="3"}

Config files define the training process and model pipeline and can be passed to
[`spacy train`](/api/cli#train). They use
[Thinc's configuration system](https://thinc.ai/docs/usage-config) under the
hood. For details on how to use training configs, see the
[usage documentation](/usage/training#config).

<Infobox variant="warning">

The `@` syntax lets you refer to function names registered in the
[function registry](/api/top-level#registry). For example,
`@architectures = "spacy.HashEmbedCNN.v1"` refers to a registered function of
the name `"spacy.HashEmbedCNN.v1"` and all other values defined in its block
will be passed into that function as arguments. Those arguments depend on the
registered function. See the [model architectures](/api/architectures) docs for
API details.

</Infobox>

<!-- TODO: we need to come up with a good way to present the sections and their expected values visually? -->
<!-- TODO: once we know how we want to implement "starter config" workflow or outputting a full default config for the user, update this section with the command -->

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
