---
title: Data formats
teaser: Details on spaCy's input and output data formats
menu:
  - ['Training Config', 'config']
  - ['Training Data', 'training']
  - ['Pretraining Data', 'pretraining']
  - ['Vocabulary', 'vocab-jsonl']
  - ['Model Meta', 'meta']
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

| Name                      | Description                                                                                                                                                                                                                      |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lang`                    | Model language [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes). Defaults to `null`. ~~str~~                                                                                                                    |
| `pipeline`                | Names of pipeline components in order. Should correspond to sections in the `[components]` block, e.g. `[components.ner]`. See docs on [defining components](/usage/training#config-components). Defaults to `[]`. ~~List[str]~~ |
| `load_vocab_data`         | Whether to load additional lexeme and vocab data from [`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data) if available. Defaults to `true`. ~~bool~~                                                         |
| `before_creation`         | Optional [callback](/usage/training#custom-code-nlp-callbacks) to modify `Language` subclass before it's initialized. Defaults to `null`. ~~Optional[Callable[[Type[Language]], Type[Language]]]~~                               |
| `after_creation`          | Optional [callback](/usage/training#custom-code-nlp-callbacks) to modify `nlp` object right after it's initialized. Defaults to `null`. ~~Optional[Callable[[Language], Language]]~~                                             |
| `after_pipeline_creation` | Optional [callback](/usage/training#custom-code-nlp-callbacks) to modify `nlp` object after the pipeline components have been added. Defaults to `null`. ~~Optional[Callable[[Language], Language]]~~                            |
| `tokenizer`               | The tokenizer to use. Defaults to [`Tokenizer`](/api/tokenizer). ~~Callable[[str], Doc]~~                                                                                                                                        |

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
as variables. For example `${paths.train}` uses the value of `train` defined in
the block `[paths]`. If your config includes custom registered functions that
need paths, you can define them here. All config values can also be
[overwritten](/usage/training#config-overrides) on the CLI when you run
[`spacy train`](/api/cli#train), which is especially relevant for data paths
that you don't want to hard-code in your config file.

```cli
$ python -m spacy train config.cfg --paths.train ./corpus/train.spacy
```

### training {#config-training tag="section"}

This section defines settings and controls for the training and evaluation
process that are used when you run [`spacy train`](/api/cli#train).

| Name                  | Description                                                                                                                                                                                                  |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `accumulate_gradient` | Whether to divide the batch up into substeps. Defaults to `1`. ~~int~~                                                                                                                                       |
| `batcher`             | Callable that takes an iterator of [`Doc`](/api/doc) objects and yields batches of `Doc`s. Defaults to [`batch_by_words`](/api/top-level#batch_by_words). ~~Callable[[Iterator[Doc], Iterator[List[Doc]]]]~~ |
| `dev_corpus`          | Callable that takes the current `nlp` object and yields [`Example`](/api/example) objects. Defaults to [`Corpus`](/api/corpus). ~~Callable[[Language], Iterator[Example]]~~                                  |
| `dropout`             | The dropout rate. Defaults to `0.1`. ~~float~~                                                                                                                                                               |
| `eval_frequency`      | How often to evaluate during training (steps). Defaults to `200`. ~~int~~                                                                                                                                    |
| `frozen_components`   | Pipeline component names that are "frozen" and shouldn't be updated during training. See [here](/usage/training#config-components) for details. Defaults to `[]`. ~~List[str]~~                              |
| `init_tok2vec`        | Optional path to pretrained tok2vec weights created with [`spacy pretrain`](/api/cli#pretrain). Defaults to variable `${paths.init_tok2vec}`. ~~Optional[str]~~                                              |
| `max_epochs`          | Maximum number of epochs to train for. Defaults to `0`. ~~int~~                                                                                                                                              |
| `max_steps`           | Maximum number of update steps to train for. Defaults to `20000`. ~~int~~                                                                                                                                    |
| `optimizer`           | The optimizer. The learning rate schedule and other settings can be configured as part of the optimizer. Defaults to [`Adam`](https://thinc.ai/docs/api-optimizers#adam). ~~Optimizer~~                      |
| `patience`            | How many steps to continue without improvement in evaluation score. Defaults to `1600`. ~~int~~                                                                                                              |
| `raw_text`            | Optional path to a jsonl file with unlabelled text documents for a [rehearsal](/api/language#rehearse) step. Defaults to variable `${paths.raw}`. ~~Optional[str]~~                                          |
| `score_weights`       | Score names shown in metrics mapped to their weight towards the final weighted score. See [here](/usage/training#metrics) for details. Defaults to `{}`. ~~Dict[str, float]~~                                |
| `seed`                | The random seed. Defaults to variable `${system.seed}`. ~~int~~                                                                                                                                              |
| `train_corpus`        | Callable that takes the current `nlp` object and yields [`Example`](/api/example) objects. Defaults to [`Corpus`](/api/corpus). ~~Callable[[Language], Iterator[Example]]~~                                  |
| `vectors`             | Model name or path to model containing pretrained word vectors to use, e.g. created with [`init model`](/api/cli#init-model). Defaults to `null`. ~~Optional[str]~~                                          |

### pretraining {#config-pretraining tag="section,optional"}

This section is optional and defines settings and controls for
[language model pretraining](/usage/training#pretraining). It's used when you
run [`spacy pretrain`](/api/cli#pretrain).

| Name                         | Description                                                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `max_epochs`                 | Maximum number of epochs. Defaults to `1000`. ~~int~~                                                                           |
| `min_length`                 | Minimum length of examples. Defaults to `5`. ~~int~~                                                                            |
| `max_length`                 | Maximum length of examples. Defaults to `500`. ~~int~~                                                                          |
| `dropout`                    | The dropout rate. Defaults to `0.2`. ~~float~~                                                                                  |
| `n_save_every`               | Saving frequency. Defaults to `null`. ~~Optional[int]~~                                                                         |
| `batch_size`                 | The batch size or batch size [schedule](https://thinc.ai/docs/api-schedules). Defaults to `3000`. ~~Union[int, Sequence[int]]~~ |
| `seed`                       | The random seed. Defaults to variable `${system.seed}`. ~~int~~                                                                 |
| `use_pytorch_for_gpu_memory` | Allocate memory via PyTorch. Defaults to variable `${system.use_pytorch_for_gpu_memory}`. ~~bool~~                              |
| `tok2vec_model`              | The model section of the embedding component in the config. Defaults to `"components.tok2vec.model"`. ~~str~~                   |
| `objective`                  | The pretraining objective. Defaults to `{"type": "characters", "n_characters": 4}`. ~~Dict[str, Any]~~                          |
| `optimizer`                  | The optimizer. Defaults to [`Adam`](https://thinc.ai/docs/api-optimizers#adam). ~~Optimizer~~                                   |

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

```cli
$ python -m spacy convert ./data.json ./output.spacy
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

The [`spacy pretrain`](/api/cli#pretrain) command lets you pretrain the
"token-to-vector" embedding layer of pipeline components from raw text. Raw text
can be provided as a `.jsonl` (newline-delimited JSON) file containing one input
text per line (roughly paragraph length is good). Optionally, custom
tokenization can be provided.

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

| Key      | Description                                                           |
| -------- | --------------------------------------------------------------------- |
| `text`   | The raw input text. Is not required if `tokens` is available. ~~str~~ |
| `tokens` | Optional tokenization, one string per token. ~~List[str]~~            |

```json
### Example
{"text": "Can I ask where you work now and what you do, and if you enjoy it?"}
{"text": "They may just pull out of the Seattle market completely, at least until they have autonomous vehicles."}
{"text": "My cynical view on this is that it will never be free to the public. Reason: what would be the draw of joining the military? Right now their selling point is free Healthcare and Education. Ironically both are run horribly and most, that I've talked to, come out wishing they never went in."}
{"tokens": ["If", "tokens", "are", "provided", "then", "we", "can", "skip", "the", "raw", "input", "text"]}
```

## Lexical data for vocabulary {#vocab-jsonl new="2"}

To populate a model's vocabulary, you can use the
[`spacy init model`](/api/cli#init-model) command and load in a
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

## Model meta {#meta}

The model meta is available as the file `meta.json` and exported automatically
when you save an `nlp` object to disk. Its contents are available as
[`nlp.meta`](/api/language#meta).

<Infobox variant="warning" title="Changed in v3.0">

As of spaCy v3.0, the `meta.json` **isn't** used to construct the language class
and pipeline anymore and only contains meta information for reference and for
creating a Python package with [`spacy package`](/api/cli#package). How to set
up the `nlp` object is now defined in the
[`config.cfg`](/api/data-formats#config), which includes detailed information
about the pipeline components and their model architectures, and all other
settings and hyperparameters used to train the model. It's the **single source
of truth** used for loading a model.

</Infobox>

> #### Example
>
> ```json
> {
>   "name": "example_model",
>   "lang": "en",
>   "version": "1.0.0",
>   "spacy_version": ">=3.0.0,<3.1.0",
>   "parent_package": "spacy",
>   "description": "Example model for spaCy",
>   "author": "You",
>   "email": "you@example.com",
>   "url": "https://example.com",
>   "license": "CC BY-SA 3.0",
>   "sources": [{ "name": "My Corpus", "license": "MIT" }],
>   "vectors": { "width": 0, "vectors": 0, "keys": 0, "name": null },
>   "pipeline": ["tok2vec", "ner", "textcat"],
>   "labels": {
>     "ner": ["PERSON", "ORG", "PRODUCT"],
>     "textcat": ["POSITIVE", "NEGATIVE"]
>   },
>   "accuracy": {
>     "ents_f": 82.7300930714,
>     "ents_p": 82.135523614,
>     "ents_r": 83.3333333333,
>     "textcat_score": 88.364323811
>   },
>   "speed": { "cpu": 7667.8, "gpu": null, "nwords": 10329 },
>   "spacy_git_version": "61dfdd9fb"
> }
> ```

| Name                                           | Description                                                                                                                                                                                                                                                                                                              |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `lang`                                         | Model language [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes). Defaults to `"en"`. ~~str~~                                                                                                                                                                                                            |
| `name`                                         | Model name, e.g. `"core_web_sm"`. The final model package name will be `{lang}_{name}`. Defaults to `"model"`. ~~str~~                                                                                                                                                                                                   |
| `version`                                      | Model version. Will be used to version a Python package created with [`spacy package`](/api/cli#package). Defaults to `"0.0.0"`. ~~str~~                                                                                                                                                                                 |
| `spacy_version`                                | spaCy version range the model is compatible with. Defaults to the spaCy version used to create the model, up to next minor version, which is the default compatibility for the available [pretrained models](/models). For instance, a model trained with v3.0.0 will have the version range `">=3.0.0,<3.1.0"`. ~~str~~ |
| `parent_package`                               | Name of the spaCy package. Typically `"spacy"` or `"spacy_nightly"`. Defaults to `"spacy"`. ~~str~~                                                                                                                                                                                                                      |
| `description`                                  | Model description. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                               |
| `author`                                       | Model author name. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                               |
| `email`                                        | Model author email. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                              |
| `url`                                          | Model author URL. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                                |
| `license`                                      | Model license. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                                   |
| `sources`                                      | Data sources used to train the model. Typically a list of dicts with the keys `"name"`, `"url"`, `"author"` and `"license"`. [See here](https://github.com/explosion/spacy-models/tree/master/meta) for examples. Defaults to `None`. ~~Optional[List[Dict[str, str]]]~~                                                 |
| `vectors`                                      | Information about the word vectors included with the model. Typically a dict with the keys `"width"`, `"vectors"` (number of vectors), `"keys"` and `"name"`. ~~Dict[str, Any]~~                                                                                                                                         |
| `pipeline`                                     | Names of pipeline component names in the model, in order. Corresponds to [`nlp.pipe_names`](/api/language#pipe_names). Only exists for reference and is not used to create the components. This information is defined in the [`config.cfg`](/api/data-formats#config). Defaults to `[]`. ~~List[str]~~                  |
| `labels`                                       | Label schemes of the trained pipeline components, keyed by component name. Corresponds to [`nlp.pipe_labels`](/api/language#pipe_labels). [See here](https://github.com/explosion/spacy-models/tree/master/meta) for examples. Defaults to `{}`. ~~Dict[str, Dict[str, List[str]]]~~                                     |
| `accuracy`                                     | Training accuracy, added automatically by [`spacy train`](/api/cli#train). Dictionary of [score names](/usage/training#metrics) mapped to scores. Defaults to `{}`. ~~Dict[str, Union[float, Dict[str, float]]]~~                                                                                                        |
| `speed`                                        | Model speed, added automatically by [`spacy train`](/api/cli#train). Typically a dictionary with the keys `"cpu"`, `"gpu"` and `"nwords"` (words per second). Defaults to `{}`. ~~Dict[str, Optional[Union[float, str]]]~~                                                                                               |
| `spacy_git_version` <Tag variant="new">3</Tag> | Git commit of [`spacy`](https://github.com/explosion/spaCy) used to create model. ~~str~~                                                                                                                                                                                                                                |
| other                                          | Any other custom meta information you want to add. The data is preserved in [`nlp.meta`](/api/language#meta). ~~Any~~                                                                                                                                                                                                    |
