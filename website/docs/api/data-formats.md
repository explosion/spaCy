---
title: Data formats
teaser: Details on spaCy's input and output data formats
menu:
  - ['Training Config', 'config']
  - ['Training Data', 'training']
  - ['Pretraining Data', 'pretraining']
  - ['Vocabulary', 'vocab']
---

This section documents input and output formats of data used by spaCy, including
the [training config](/usage/training#config), training data and lexical
vocabulary data. For an overview of label schemes used by the models, see the
[models directory](/models). Each model documents the label schemes used in its
components, depending on the data it was trained on.

## Training config {#config new="3"}

Config files define the training process and model pipeline and can be passed to
[`spacy train`](/api/cli#train). They use
[Thinc's configuration system](https://thinc.ai/docs/usage-config) under the
hood. For details on how to use training configs, see the
[usage documentation](/usage/training#config). To get started with the
recommended settings for your use case, check out the
[quickstart widget](/usage/training#quickstart) or run the
[`init config`](/api/cli#init-config) command.

> #### What does the @ mean?
>
> The `@` syntax lets you refer to function names registered in the
> [function registry](/api/top-level#registry). For example,
> `@architectures = "spacy.HashEmbedCNN.v1"` refers to a registered function of
> the name [spacy.HashEmbedCNN.v1](/api/architectures#HashEmbedCNN) and all
> other values defined in its block will be passed into that function as
> arguments. Those arguments depend on the registered function. See the usage
> guide on [registered functions](/usage/training#config-functions) for details.

```ini
https://github.com/explosion/spaCy/blob/develop/spacy/default_config.cfg
```

<Infobox title="Notes on data validation" emoji="💡">

Under the hood, spaCy's configs are powered by our machine learning library
[Thinc's config system](https://thinc.ai/docs/usage-config), which uses
[`pydantic`](https://github.com/samuelcolvin/pydantic/) for data validation
based on type hints. See
[`spacy/schemas.py`](https://github.com/explosion/spaCy/blob/develop/spacy/schemas.py)
for the schemas used to validate the default config. Arguments of registered
functions are validated against their type annotations, if available. To debug
your config and check that it's valid, you can run the
[`spacy debug config`](/api/cli#debug-config) command.

</Infobox>

### nlp {#config-nlp tag="section"}

> #### Example
>
> ```ini
> [nlp]
> lang = "en"
> pipeline = ["tagger", "parser", "ner"]
> load_vocab_data = true
> before_creation = null
> after_creation = null
> after_pipeline_creation = null
>
> [nlp.tokenizer]
> @tokenizers = "spacy.Tokenizer.v1"
> ```

Defines the `nlp` object, its tokenizer and
[processing pipeline](/usage/processing-pipelines) component names.

| Name                      | Description                                                                                                                                                                                                    | Default                       |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `lang`                    | The language code to use. ~~str~~                                                                                                                                                                              | `null`                        |
| `pipeline`                | Names of pipeline components in order. Should correspond to sections in the `[components]` block, e.g. `[components.ner]`. See docs on [defining components](/usage/training#config-components). ~~List[str]~~ | `[]`                          |
| `load_vocab_data`         | Whether to load additional lexeme and vocab data from [`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data) if available. ~~bool~~                                                           | `true`                        |
| `before_creation`         | Optional [callback](/usage/training#custom-code-nlp-callbacks) to modify `Language` subclass before it's initialized. ~~Optional[Callable[[Type[Language]], Type[Language]]]~~                                 | `null`                        |
| `after_creation`          | Optional [callback](/usage/training#custom-code-nlp-callbacks) to modify `nlp` object right after it's initialized. ~~Optional[Callable[[Language], Language]]~~                                               | `null`                        |
| `after_pipeline_creation` | Optional [callback](/usage/training#custom-code-nlp-callbacks) to modify `nlp` object after the pipeline components have been added. ~~Optional[Callable[[Language], Language]]~~                              | `null`                        |
| `tokenizer`               | The tokenizer to use. ~~Callable[[str], Doc]~~                                                                                                                                                                 | [`Tokenizer`](/api/tokenizer) |

### components {#config-components tag="section"}

> #### Example
>
> ```ini
> [components.textcat]
> factory = "textcat"
> labels = ["POSITIVE", "NEGATIVE"]
>
> [components.textcat.model]
> @architectures = "spacy.TextCatBOW.v1"
> exclusive_classes = false
> ngram_size = 1
> no_output_layer = false
> ```

This section includes definitions of the
[pipeline components](/usage/processing-pipelines) and their models, if
available. Components in this section can be referenced in the `pipeline` of the
`[nlp]` block. Component blocks need to specify either a `factory` (named
function to use to create component) or a `source` (name of path of pretrained
model to copy components from). See the docs on
[defining pipeline components](/usage/training#config-components) for details.

### paths, system {#config-variables tag="variables"}

These sections define variables that can be referenced across the other sections
as variables. For example `${paths:train}` uses the value of `train` defined in
the block `[paths]`. If your config includes custom registered functions that
need paths, you can define them here. All config values can also be
[overwritten](/usage/training#config-overrides) on the CLI when you run
[`spacy train`](/api/cli#train), which is especially relevant for data paths
that you don't want to hard-code in your config file.

```bash
$ python -m spacy train ./config.cfg --paths.train ./corpus/train.spacy
```

### training {#config-training tag="section"}

This section defines settings and controls for the training and evaluation
process that are used when you run [`spacy train`](/api/cli#train).

<!-- TODO: complete -->

| Name                  | Description                                                                                                                                                   | Default                                             |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `seed`                | The random seed. ~~int~~                                                                                                                                      | `${system:seed}`                                    |
| `dropout`             | The dropout rate. ~~float~~                                                                                                                                   | `0.1`                                               |
| `accumulate_gradient` | Whether to divide the batch up into substeps. ~~int~~                                                                                                         | `1`                                                 |
| `init_tok2vec`        | Optional path to pretrained tok2vec weights created with [`spacy pretrain`](/api/cli#pretrain). ~~Optional[str]~~                                             | `${paths:init_tok2vec}`                             |
| `raw_text`            | ~~Optional[str]~~                                                                                                                                             | `${paths:raw}`                                      |
| `vectors`             | ~~Optional[str]~~                                                                                                                                             | `null`                                              |
| `patience`            | How many steps to continue without improvement in evaluation score. ~~int~~                                                                                   | `1600`                                              |
| `max_epochs`          | Maximum number of epochs to train for. ~~int~~                                                                                                                | `0`                                                 |
| `max_steps`           | Maximum number of update steps to train for. ~~int~~                                                                                                          | `20000`                                             |
| `eval_frequency`      | How often to evaluate during training (steps). ~~int~~                                                                                                        | `200`                                               |
| `score_weights`       | Score names shown in metrics mapped to their weight towards the final weighted score. See [here](/usage/training#metrics) for details. ~~Dict[str, float]~~   | `{}`                                                |
| `frozen_components`   | Pipeline component names that are "frozen" and shouldn't be updated during training. See [here](/usage/training#config-components) for details. ~~List[str]~~ | `[]`                                                |
| `train_corpus`        | Callable that takes the current `nlp` object and yields [`Example`](/api/example) objects. ~~Callable[[Language], Iterator[Example]]~~                        | [`Corpus`](/api/corpus)                             |
| `dev_corpus`          | Callable that takes the current `nlp` object and yields [`Example`](/api/example) objects. ~~Callable[[Language], Iterator[Example]]~~                        | [`Corpus`](/api/corpus)                             |
| `batcher`             | Callable that takes an iterator of [`Doc`](/api/doc) objects and yields batches of `Doc`s. ~~Callable[[Iterator[Doc], Iterator[List[Doc]]]]~~                 | [`batch_by_words`](/api/top-level#batch_by_words)   |
| `optimizer`           | The optimizer. The learning rate schedule and other settings can be configured as part of the optimizer. ~~Optimizer~~                                        | [`Adam`](https://thinc.ai/docs/api-optimizers#adam) |

### pretraining {#config-pretraining tag="section,optional"}

This section is optional and defines settings and controls for
[language model pretraining](/usage/training#pretraining). It's used when you
run [`spacy pretrain`](/api/cli#pretrain).

| Name                         | Description                                                                                                 | Default                                             |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `max_epochs`                 | Maximum number of epochs. ~~int~~                                                                           | `1000`                                              |
| `min_length`                 | Minimum length of examples. ~~int~~                                                                         | `5`                                                 |
| `max_length`                 | Maximum length of examples. ~~int~~                                                                         | `500`                                               |
| `dropout`                    | The dropout rate. ~~float~~                                                                                 | `0.2`                                               |
| `n_save_every`               | Saving frequency. ~~int~~                                                                                   | `null`                                              |
| `batch_size`                 | The batch size or batch size [schedule](https://thinc.ai/docs/api-schedules). ~~Union[int, Sequence[int]]~~ | `3000`                                              |
| `seed`                       | The random seed. ~~int~~                                                                                    | `${system.seed}`                                    |
| `use_pytorch_for_gpu_memory` | Allocate memory via PyTorch. ~~bool~~                                                                       | `${system:use_pytorch_for_gpu_memory}`              |
| `tok2vec_model`              | tok2vec model section in the config. ~~str~~                                                                | `"components.tok2vec.model"`                        |
| `objective`                  | The pretraining objective. ~~Dict[str, Any]~~                                                               | `{"type": "characters", "n_characters": 4}`         |
| `optimizer`                  | The optimizer. ~~Optimizer~~                                                                                | [`Adam`](https://thinc.ai/docs/api-optimizers#adam) |

## Training data {#training}

### Binary training format {#binary-training new="3"}

> #### Example
>
> ```python
> from spacy.tokens import DocBin
> from spacy.gold import Corpus
>
> doc_bin = DocBin(docs=docs)
> doc_bin.to_disk("./data.spacy")
> reader = Corpus("./data.spacy")
> ```

The main data format used in spaCy v3.0 is a **binary format** created by
serializing a [`DocBin`](/api/docbin), which represents a collection of `Doc`
objects. This means that you can train spaCy models using the same format it
outputs: annotated `Doc` objects. The binary format is extremely **efficient in
storage**, especially when packing multiple documents together.

Typically, the extension for these binary files is `.spacy`, and they are used
as input format for specifying a [training corpus](/api/corpus) and for spaCy's
CLI [`train`](/api/cli#train) command. The built-in
[`convert`](/api/cli#convert) command helps you convert spaCy's previous
[JSON format](#json-input) to the new binary format format. It also supports
conversion of the `.conllu` format used by the
[Universal Dependencies corpora](https://github.com/UniversalDependencies).

### JSON training format {#json-input tag="deprecated"}

<Infobox variant="warning" title="Changed in v3.0">

As of v3.0, the JSON input format is deprecated and is replaced by the
[binary format](#binary-training). Instead of converting [`Doc`](/api/doc)
objects to JSON, you can now serialize them directly using the
[`DocBin`](/api/docbin) container and then use them as input data.

[`spacy convert`](/api/cli) lets you convert your JSON data to the new `.spacy`
format:

```bash
$ python -m spacy convert ./data.json ./output
```

</Infobox>

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
a dictionary of gold-standard annotations.

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

| Name          | Description                                                                                                                                                                                                                    |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `text`        | Raw text. ~~str~~                                                                                                                                                                                                              |
| `words`       | List of gold-standard tokens. ~~List[str]~~                                                                                                                                                                                    |
| `lemmas`      | List of lemmas. ~~List[str]~~                                                                                                                                                                                                  |
| `spaces`      | List of boolean values indicating whether the corresponding tokens is followed by a space or not. ~~List[bool]~~                                                                                                               |
| `tags`        | List of fine-grained [POS tags](/usage/linguistic-features#pos-tagging). ~~List[str]~~                                                                                                                                         |
| `pos`         | List of coarse-grained [POS tags](/usage/linguistic-features#pos-tagging). ~~List[str]~~                                                                                                                                       |
| `morphs`      | List of [morphological features](/usage/linguistic-features#rule-based-morphology). ~~List[str]~~                                                                                                                              |
| `sent_starts` | List of boolean values indicating whether each token is the first of a sentence or not. ~~List[bool]~~                                                                                                                         |
| `deps`        | List of string values indicating the [dependency relation](/usage/linguistic-features#dependency-parse) of a token to its head. ~~List[str]~~                                                                                  |
| `heads`       | List of integer values indicating the dependency head of each token, referring to the absolute index of each token in the text. ~~List[int]~~                                                                                  |
| `entities`    | **Option 1:** List of [BILUO tags](/usage/linguistic-features#accessing-ner) per token of the format `"{action}-{label}"`, or `None` for unannotated tokens. ~~List[str]~~                                                     |
| `entities`    | **Option 2:** List of `"(start, end, label)"` tuples defining all entities in the text. ~~List[Tuple[int, int, str]]~~                                                                                                         |
| `cats`        | Dictionary of `label`/`value` pairs indicating how relevant a certain [text category](/api/textcategorizer) is for the text. ~~Dict[str, float]~~                                                                              |
| `links`       | Dictionary of `offset`/`dict` pairs defining [named entity links](/usage/linguistic-features#entity-linking). The character offsets are linked to a dictionary of relevant knowledge base IDs. ~~Dict[Tuple[int, int], Dict]~~ |

<Infobox title="Notes and caveats">

- Multiple formats are possible for the "entities" entry, but you have to pick
  one.
- Any values for sentence starts will be ignored if there are annotations for
  dependency relations.
- If the dictionary contains values for `"text"` and `"words"`, but not
  `"spaces"`, the latter are inferred automatically. If "words" is not provided
  either, the values are inferred from the `Doc` argument.

</Infobox>

```python
### Examples
# Training data for a part-of-speech tagger
doc = Doc(vocab, words=["I", "like", "stuff"])
gold_dict = {"tags": ["NOUN", "VERB", "NOUN"]}
example = Example.from_dict(doc, gold_dict)

# Training data for an entity recognizer (option 1)
doc = nlp("Laura flew to Silicon Valley.")
gold_dict = {"entities": ["U-PERS", "O", "O", "B-LOC", "L-LOC"]}
example = Example.from_dict(doc, gold_dict)

# Training data for an entity recognizer (option 2)
doc = nlp("Laura flew to Silicon Valley.")
gold_dict = {"entities": [(0, 5, "PERSON"), (14, 28, "LOC")]}
example = Example.from_dict(doc, gold_dict)

# Training data for text categorization
doc = nlp("I'm pretty happy about that!")
gold_dict = {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}
example = Example.from_dict(doc, gold_dict)

# Training data for an Entity Linking component
doc = nlp("Russ Cochran his reprints include EC Comics.")
gold_dict = {"links": {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}}}
example = Example.from_dict(doc, gold_dict)
```

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

| Key      | Description                                                        |
| -------- | ------------------------------------------------------------------ |
| `text`   | The raw input text. Is not required if `tokens` available. ~~str~~ |
| `tokens` | Optional tokenization, one string per token. ~~List[str]~~         |

```json
### Example
{"text": "Can I ask where you work now and what you do, and if you enjoy it?"}
{"text": "They may just pull out of the Seattle market completely, at least until they have autonomous vehicles."}
{"text": "My cynical view on this is that it will never be free to the public. Reason: what would be the draw of joining the military? Right now their selling point is free Healthcare and Education. Ironically both are run horribly and most, that I've talked to, come out wishing they never went in."}
{"tokens": ["If", "tokens", "are", "provided", "then", "we", "can", "skip", "the", "raw", "input", "text"]}
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
