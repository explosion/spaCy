---
title: Data formats
teaser: Details on spaCy's input and output data formats
menu:
  - ['Training Config', 'config']
  - ['Training Data', 'training']
  - ['Vocabulary', 'vocab-jsonl']
  - ['Pipeline Meta', 'meta']
---

This section documents input and output formats of data used by spaCy, including
the [training config](/usage/training#config), training data and lexical
vocabulary data. For an overview of label schemes used by the models, see the
[models directory](/models). Each trained pipeline documents the label schemes
used in its components, depending on the data it was trained on.

## Training config {#config new="3"}

Config files define the training process and pipeline and can be passed to
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
> `@architectures = "spacy.HashEmbedCNN.v2"` refers to a registered function of
> the name [spacy.HashEmbedCNN.v2](/api/architectures#HashEmbedCNN) and all
> other values defined in its block will be passed into that function as
> arguments. Those arguments depend on the registered function. See the usage
> guide on [registered functions](/usage/training#config-functions) for details.

```ini
%%GITHUB_SPACY/spacy/default_config.cfg
```

<Infobox title="Notes on data validation" emoji="💡">

Under the hood, spaCy's configs are powered by our machine learning library
[Thinc's config system](https://thinc.ai/docs/usage-config), which uses
[`pydantic`](https://github.com/samuelcolvin/pydantic/) for data validation
based on type hints. See [`spacy/schemas.py`](%%GITHUB_SPACY/spacy/schemas.py)
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
> before_creation = null
> after_creation = null
> after_pipeline_creation = null
> batch_size = 1000
>
> [nlp.tokenizer]
> @tokenizers = "spacy.Tokenizer.v1"
> ```

Defines the `nlp` object, its tokenizer and
[processing pipeline](/usage/processing-pipelines) component names.

| Name                      | Description                                                                                                                                                                                                                                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lang`                    | Pipeline language [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes). Defaults to `null`. ~~str~~                                                                                                                                                                                        |
| `pipeline`                | Names of pipeline components in order. Should correspond to sections in the `[components]` block, e.g. `[components.ner]`. See docs on [defining components](/usage/training#config-components). Defaults to `[]`. ~~List[str]~~                                                                        |
| `disabled`                | Names of pipeline components that are loaded but disabled by default and not run as part of the pipeline. Should correspond to components listed in `pipeline`. After a pipeline is loaded, disabled components can be enabled using [`Language.enable_pipe`](/api/language#enable_pipe). ~~List[str]~~ |
| `before_creation`         | Optional [callback](/usage/training#custom-code-nlp-callbacks) to modify `Language` subclass before it's initialized. Defaults to `null`. ~~Optional[Callable[[Type[Language]], Type[Language]]]~~                                                                                                      |
| `after_creation`          | Optional [callback](/usage/training#custom-code-nlp-callbacks) to modify `nlp` object right after it's initialized. Defaults to `null`. ~~Optional[Callable[[Language], Language]]~~                                                                                                                    |
| `after_pipeline_creation` | Optional [callback](/usage/training#custom-code-nlp-callbacks) to modify `nlp` object after the pipeline components have been added. Defaults to `null`. ~~Optional[Callable[[Language], Language]]~~                                                                                                   |
| `tokenizer`               | The tokenizer to use. Defaults to [`Tokenizer`](/api/tokenizer). ~~Callable[[str], Doc]~~                                                                                                                                                                                                               |
| `batch_size`              | Default batch size for [`Language.pipe`](/api/language#pipe) and [`Language.evaluate`](/api/language#evaluate). ~~int~~                                                                                                                                                                                 |

### components {#config-components tag="section"}

> #### Example
>
> ```ini
> [components.textcat]
> factory = "textcat"
>
> [components.textcat.model]
> @architectures = "spacy.TextCatBOW.v2"
> exclusive_classes = true
> ngram_size = 1
> no_output_layer = false
> ```

This section includes definitions of the
[pipeline components](/usage/processing-pipelines) and their models, if
available. Components in this section can be referenced in the `pipeline` of the
`[nlp]` block. Component blocks need to specify either a `factory` (named
function to use to create component) or a `source` (name of path of trained
pipeline to copy components from). See the docs on
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

### corpora {#config-corpora tag="section"}

> #### Example
>
> ```ini
> [corpora]
>
> [corpora.train]
> @readers = "spacy.Corpus.v1"
> path = ${paths:train}
>
> [corpora.dev]
> @readers = "spacy.Corpus.v1"
> path = ${paths:dev}
>
> [corpora.pretrain]
> @readers = "spacy.JsonlCorpus.v1"
> path = ${paths.raw}
>
> [corpora.my_custom_data]
> @readers = "my_custom_reader.v1"
> ```

This section defines a **dictionary** mapping of string keys to functions. Each
function takes an `nlp` object and yields [`Example`](/api/example) objects. By
default, the two keys `train` and `dev` are specified and each refer to a
[`Corpus`](/api/top-level#Corpus). When pretraining, an additional `pretrain`
section is added that defaults to a [`JsonlCorpus`](/api/top-level#jsonlcorpus).
You can also register custom functions that return a callable.

| Name       | Description                                                                                                                                                                 |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `train`    | Training data corpus, typically used in `[training]` block. ~~Callable[[Language], Iterator[Example]]~~                                                                     |
| `dev`      | Development data corpus, typically used in `[training]` block. ~~Callable[[Language], Iterator[Example]]~~                                                                  |
| `pretrain` | Raw text for [pretraining](/usage/embeddings-transformers#pretraining), typically used in `[pretraining]` block (if available). ~~Callable[[Language], Iterator[Example]]~~ |
| ...        | Any custom or alternative corpora. ~~Callable[[Language], Iterator[Example]]~~                                                                                              |

Alternatively, the `[corpora]` block can refer to **one function** that returns
a dictionary keyed by the corpus names. This can be useful if you want to load a
single corpus once and then divide it up into `train` and `dev` partitions.

> #### Example
>
> ```ini
> [corpora]
> @readers = "my_custom_reader.v1"
> train_path = ${paths:train}
> dev_path = ${paths:dev}
> shuffle = true
>
> ```

| Name      | Description                                                                                                                                                                                                              |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `corpora` | A dictionary keyed by string names, mapped to corpus functions that receive the current `nlp` object and return an iterator of [`Example`](/api/example) objects. ~~Dict[str, Callable[[Language], Iterator[Example]]]~~ |

### training {#config-training tag="section"}

This section defines settings and controls for the training and evaluation
process that are used when you run [`spacy train`](/api/cli#train).

| Name                                                 | Description                                                                                                                                                                                                                                                                                                                         |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `accumulate_gradient`                                | Whether to divide the batch up into substeps. Defaults to `1`. ~~int~~                                                                                                                                                                                                                                                              |
| `batcher`                                            | Callable that takes an iterator of [`Doc`](/api/doc) objects and yields batches of `Doc`s. Defaults to [`batch_by_words`](/api/top-level#batch_by_words). ~~Callable[[Iterator[Doc], Iterator[List[Doc]]]]~~                                                                                                                        |
| `before_to_disk`                                     | Optional callback to modify `nlp` object right before it is saved to disk during and after training. Can be used to remove or reset config values or disable components. Defaults to `null`. ~~Optional[Callable[[Language], Language]]~~                                                                                           |
| `dev_corpus`                                         | Dot notation of the config location defining the dev corpus. Defaults to `corpora.dev`. ~~str~~                                                                                                                                                                                                                                     |
| `dropout`                                            | The dropout rate. Defaults to `0.1`. ~~float~~                                                                                                                                                                                                                                                                                      |
| `eval_frequency`                                     | How often to evaluate during training (steps). Defaults to `200`. ~~int~~                                                                                                                                                                                                                                                           |
| `frozen_components`                                  | Pipeline component names that are "frozen" and shouldn't be initialized or updated during training. See [here](/usage/training#config-components) for details. Defaults to `[]`. ~~List[str]~~                                                                                                                                      |
| `annotating_components` <Tag variant="new">3.1</Tag> | Pipeline component names that should set annotations on the predicted docs during training. See [here](/usage/training#annotating-components) for details. Defaults to `[]`. ~~List[str]~~                                                                                                                                          |
| `gpu_allocator`                                      | Library for cupy to route GPU memory allocation to. Can be `"pytorch"` or `"tensorflow"`. Defaults to variable `${system.gpu_allocator}`. ~~str~~                                                                                                                                                                                   |
| `logger`                                             | Callable that takes the `nlp` and stdout and stderr `IO` objects, sets up the logger, and returns two new callables to log a training step and to finalize the logger. Defaults to [`ConsoleLogger`](/api/top-level#ConsoleLogger). ~~Callable[[Language, IO, IO], [Tuple[Callable[[Dict[str, Any]], None], Callable[[], None]]]]~~ |
| `max_epochs`                                         | Maximum number of epochs to train for. `0` means an unlimited number of epochs. `-1` means that the train corpus should be streamed rather than loaded into memory with no shuffling within the training loop. Defaults to `0`. ~~int~~                                                                                             |
| `max_steps`                                          | Maximum number of update steps to train for. `0` means an unlimited number of steps. Defaults to `20000`. ~~int~~                                                                                                                                                                                                                   |
| `optimizer`                                          | The optimizer. The learning rate schedule and other settings can be configured as part of the optimizer. Defaults to [`Adam`](https://thinc.ai/docs/api-optimizers#adam). ~~Optimizer~~                                                                                                                                             |
| `patience`                                           | How many steps to continue without improvement in evaluation score. `0` disables early stopping. Defaults to `1600`. ~~int~~                                                                                                                                                                                                        |
| `score_weights`                                      | Score names shown in metrics mapped to their weight towards the final weighted score. See [here](/usage/training#metrics) for details. Defaults to `{}`. ~~Dict[str, float]~~                                                                                                                                                       |
| `seed`                                               | The random seed. Defaults to variable `${system.seed}`. ~~int~~                                                                                                                                                                                                                                                                     |
| `train_corpus`                                       | Dot notation of the config location defining the train corpus. Defaults to `corpora.train`. ~~str~~                                                                                                                                                                                                                                 |

### pretraining {#config-pretraining tag="section,optional"}

This section is optional and defines settings and controls for
[language model pretraining](/usage/embeddings-transformers#pretraining). It's
used when you run [`spacy pretrain`](/api/cli#pretrain).

| Name           | Description                                                                                                                                                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `max_epochs`   | Maximum number of epochs. Defaults to `1000`. ~~int~~                                                                                                                                                        |
| `dropout`      | The dropout rate. Defaults to `0.2`. ~~float~~                                                                                                                                                               |
| `n_save_every` | Saving frequency. Defaults to `null`. ~~Optional[int]~~                                                                                                                                                      |
| `objective`    | The pretraining objective. Defaults to `{"type": "characters", "n_characters": 4}`. ~~Dict[str, Any]~~                                                                                                       |
| `optimizer`    | The optimizer. The learning rate schedule and other settings can be configured as part of the optimizer. Defaults to [`Adam`](https://thinc.ai/docs/api-optimizers#adam). ~~Optimizer~~                      |
| `corpus`       | Dot notation of the config location defining the corpus with raw text. Defaults to `corpora.pretrain`. ~~str~~                                                                                               |
| `batcher`      | Callable that takes an iterator of [`Doc`](/api/doc) objects and yields batches of `Doc`s. Defaults to [`batch_by_words`](/api/top-level#batch_by_words). ~~Callable[[Iterator[Doc], Iterator[List[Doc]]]]~~ |
| `component`    | Component name to identify the layer with the model to pretrain. Defaults to `"tok2vec"`. ~~str~~                                                                                                            |
| `layer`        | The specific layer of the model to pretrain. If empty, the whole model will be used. ~~str~~                                                                                                                 |

### initialize {#config-initialize tag="section"}

This config block lets you define resources for **initializing the pipeline**.
It's used by [`Language.initialize`](/api/language#initialize) and typically
called right before training (but not at runtime). The section allows you to
specify local file paths or custom functions to load data resources from,
without requiring them at runtime when you load the trained pipeline back in.
Also see the usage guides on the
[config lifecycle](/usage/training#config-lifecycle) and
[custom initialization](/usage/training#initialization).

> #### Example
>
> ```ini
> [initialize]
> vectors = "/path/to/vectors_nlp"
> init_tok2vec = "/path/to/pretrain.bin"
>
> [initialize_components]
>
> [initialize.components.my_component]
> data_path = "/path/to/component_data"
> ```

| Name           | Description                                                                                                                                                                                                                                                                                                                                                                                                    |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `after_init`   | Optional callback to modify the `nlp` object after initialization. ~~Optional[Callable[[Language], Language]]~~                                                                                                                                                                                                                                                                                                |
| `before_init`  | Optional callback to modify the `nlp` object before initialization. ~~Optional[Callable[[Language], Language]]~~                                                                                                                                                                                                                                                                                               |
| `components`   | Additional arguments passed to the `initialize` method of a pipeline component, keyed by component name. If type annotations are available on the method, the config will be validated against them. The `initialize` methods will always receive the `get_examples` callback and the current `nlp` object. ~~Dict[str, Dict[str, Any]]~~                                                                      |
| `init_tok2vec` | Optional path to pretrained tok2vec weights created with [`spacy pretrain`](/api/cli#pretrain). Defaults to variable `${paths.init_tok2vec}`. Ignored when actually running pretraining, as you're creating the file to be used later. ~~Optional[str]~~                                                                                                                                                       |
| `lookups`      | Additional lexeme and vocab data from [`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data). Defaults to `null`. ~~Optional[Lookups]~~                                                                                                                                                                                                                                                       |
| `tokenizer`    | Additional arguments passed to the `initialize` method of the specified tokenizer. Can be used for languages like Chinese that depend on dictionaries or trained models for tokenization. If type annotations are available on the method, the config will be validated against them. The `initialize` method will always receive the `get_examples` callback and the current `nlp` object. ~~Dict[str, Any]~~ |
| `vectors`      | Name or path of pipeline containing pretrained word vectors to use, e.g. created with [`init vectors`](/api/cli#init-vectors). Defaults to `null`. ~~Optional[str]~~                                                                                                                                                                                                                                           |
| `vocab_data`   | Path to JSONL-formatted [vocabulary file](/api/data-formats#vocab-jsonl) to initialize vocabulary. ~~Optional[str]~~                                                                                                                                                                                                                                                                                           |

## Training data {#training}

### Binary training format {#binary-training new="3"}

> #### Example
>
> ```python
> from spacy.tokens import DocBin
> from spacy.training import Corpus
>
> doc_bin = DocBin(docs=docs)
> doc_bin.to_disk("./data.spacy")
> reader = Corpus("./data.spacy")
> ```

The main data format used in spaCy v3.0 is a **binary format** created by
serializing a [`DocBin`](/api/docbin), which represents a collection of `Doc`
objects. This means that you can train spaCy pipelines using the same format it
outputs: annotated `Doc` objects. The binary format is extremely **efficient in
storage**, especially when packing multiple documents together.

Typically, the extension for these binary files is `.spacy`, and they are used
as input format for specifying a [training corpus](/api/corpus) and for spaCy's
CLI [`train`](/api/cli#train) command. The built-in
[`convert`](/api/cli#convert) command helps you convert spaCy's previous
[JSON format](#json-input) to the new binary format. It also supports conversion
of the `.conllu` format used by the
[Universal Dependencies corpora](https://github.com/UniversalDependencies).

Note that while this is the format used to save training data, you do not have
to understand the internal details to use it or create training data. See the
section on [preparing training data](/usage/training#training-data).

### JSON training format {#json-input tag="deprecated"}

<Infobox variant="warning" title="Changed in v3.0">

As of v3.0, the JSON input format is deprecated and is replaced by the
[binary format](#binary-training). Instead of converting [`Doc`](/api/doc)
objects to JSON, you can now serialize them directly using the
[`DocBin`](/api/docbin) container and then use them as input data.

[`spacy convert`](/api/cli) lets you convert your JSON data to the new `.spacy`
format:

```cli
$ python -m spacy convert ./data.json .
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
> [`offsets_to_biluo_tags`](/api/top-level#offsets_to_biluo_tags) function can
> help you convert entity offsets to the right format.

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

Here's an example of dependencies, part-of-speech tags and named entities, taken
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
your pipelines via the [`spacy train`](/api/cli#train) command with a config
file to keep track of your settings and hyperparameters and your own
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
>    "sent_starts": List[Optional[bool]],
>    "deps": List[str],
>    "heads": List[int],
>    "entities": List[str],
>    "entities": List[(int, int, str)],
>    "cats": Dict[str, float],
>    "links": Dict[(int, int), dict],
>    "spans": Dict[str, List[Tuple]],
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
| `entities`    | **Option 2:** List of `(start_char, end_char, label)` tuples defining all entities in the text. ~~List[Tuple[int, int, str]]~~                                                                                                 |
| `cats`        | Dictionary of `label`/`value` pairs indicating how relevant a certain [text category](/api/textcategorizer) is for the text. ~~Dict[str, float]~~                                                                              |
| `links`       | Dictionary of `offset`/`dict` pairs defining [named entity links](/usage/linguistic-features#entity-linking). The character offsets are linked to a dictionary of relevant knowledge base IDs. ~~Dict[Tuple[int, int], Dict]~~ |
| `spans`       | Dictionary of `spans_key`/`List[Tuple]` pairs defining the spans for each spans key as `(start_char, end_char, label, kb_id)` tuples. ~~Dict[str, List[Tuple[int, int, str, str]]~~                                            |

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

# Training data for an Entity Linking component (also requires entities & sentences)
doc = nlp("Russ Cochran his reprints include EC Comics.")
gold_dict = {"entities": [(0, 12, "PERSON")],
             "links": {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}},
             "sent_starts": [1, -1, -1, -1, -1, -1, -1, -1]}
example = Example.from_dict(doc, gold_dict)
```

## Lexical data for vocabulary {#vocab-jsonl new="2"}

This data file can be provided via the `vocab_data` setting in the
`[initialize]` block of the training config to pre-define the lexical data to
initialize the `nlp` object's vocabulary with. The file should contain one
lexical entry per line. The first line defines the language and vocabulary
settings. All other lines are expected to be JSON objects describing an
individual lexeme. The lexical attributes will be then set as attributes on
spaCy's [`Lexeme`](/api/lexeme#attributes) object.

> #### Example config
>
> ```ini
> [initialize]
> vocab_data = "/path/to/vocab-data.jsonl"
> ```

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
%%GITHUB_SPACY/extra/example_data/vocab-data.jsonl
```

## Pipeline meta {#meta}

The pipeline meta is available as the file `meta.json` and exported
automatically when you save an `nlp` object to disk. Its contents are available
as [`nlp.meta`](/api/language#meta).

<Infobox variant="warning" title="Changed in v3.0">

As of spaCy v3.0, the `meta.json` **isn't** used to construct the language class
and pipeline anymore and only contains meta information for reference and for
creating a Python package with [`spacy package`](/api/cli#package). How to set
up the `nlp` object is now defined in the
[config file](/api/data-formats#config), which includes detailed information
about the pipeline components and their model architectures, and all other
settings and hyperparameters used to train the pipeline. It's the **single
source of truth** used for loading a pipeline.

</Infobox>

> #### Example
>
> ```json
> {
>   "name": "example_pipeline",
>   "lang": "en",
>   "version": "1.0.0",
>   "spacy_version": ">=3.0.0,<3.1.0",
>   "parent_package": "spacy",
>   "requirements": ["spacy-transformers>=1.0.0,<1.1.0"],
>   "description": "Example pipeline for spaCy",
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
>   "performance": {
>     "ents_f": 82.7300930714,
>     "ents_p": 82.135523614,
>     "ents_r": 83.3333333333,
>     "textcat_score": 88.364323811
>   },
>   "speed": { "cpu": 7667.8, "gpu": null, "nwords": 10329 },
>   "spacy_git_version": "61dfdd9fb"
> }
> ```

| Name                                           | Description                                                                                                                                                                                                                                                                                                                      |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lang`                                         | Pipeline language [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes). Defaults to `"en"`. ~~str~~                                                                                                                                                                                                                 |
| `name`                                         | Pipeline name, e.g. `"core_web_sm"`. The final package name will be `{lang}_{name}`. Defaults to `"pipeline"`. ~~str~~                                                                                                                                                                                                           |
| `version`                                      | Pipeline version. Will be used to version a Python package created with [`spacy package`](/api/cli#package). Defaults to `"0.0.0"`. ~~str~~                                                                                                                                                                                      |
| `spacy_version`                                | spaCy version range the package is compatible with. Defaults to the spaCy version used to create the pipeline, up to next minor version, which is the default compatibility for the available [trained pipelines](/models). For instance, a pipeline trained with v3.0.0 will have the version range `">=3.0.0,<3.1.0"`. ~~str~~ |
| `parent_package`                               | Name of the spaCy package. Typically `"spacy"` or `"spacy_nightly"`. Defaults to `"spacy"`. ~~str~~                                                                                                                                                                                                                              |
| `requirements`                                 | Python package requirements that the pipeline depends on. Will be used for the Python package setup in [`spacy package`](/api/cli#package). Should be a list of package names with optional version specifiers, just like you'd define them in a `setup.cfg` or `requirements.txt`. Defaults to `[]`. ~~List[str]~~              |
| `description`                                  | Pipeline description. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                                    |
| `author`                                       | Pipeline author name. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                                    |
| `email`                                        | Pipeline author email. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                                   |
| `url`                                          | Pipeline author URL. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                                     |
| `license`                                      | Pipeline license. Also used for Python package. Defaults to `""`. ~~str~~                                                                                                                                                                                                                                                        |
| `sources`                                      | Data sources used to train the pipeline. Typically a list of dicts with the keys `"name"`, `"url"`, `"author"` and `"license"`. [See here](https://github.com/explosion/spacy-models/tree/master/meta) for examples. Defaults to `None`. ~~Optional[List[Dict[str, str]]]~~                                                      |
| `vectors`                                      | Information about the word vectors included with the pipeline. Typically a dict with the keys `"width"`, `"vectors"` (number of vectors), `"keys"` and `"name"`. ~~Dict[str, Any]~~                                                                                                                                              |
| `pipeline`                                     | Names of pipeline component names, in order. Corresponds to [`nlp.pipe_names`](/api/language#pipe_names). Only exists for reference and is not used to create the components. This information is defined in the [`config.cfg`](/api/data-formats#config). Defaults to `[]`. ~~List[str]~~                                       |
| `labels`                                       | Label schemes of the trained pipeline components, keyed by component name. Corresponds to [`nlp.pipe_labels`](/api/language#pipe_labels). [See here](https://github.com/explosion/spacy-models/tree/master/meta) for examples. Defaults to `{}`. ~~Dict[str, Dict[str, List[str]]]~~                                             |
| `performance`                                  | Training accuracy, added automatically by [`spacy train`](/api/cli#train). Dictionary of [score names](/usage/training#metrics) mapped to scores. Defaults to `{}`. ~~Dict[str, Union[float, Dict[str, float]]]~~                                                                                                                |
| `speed`                                        | Inference speed, added automatically by [`spacy train`](/api/cli#train). Typically a dictionary with the keys `"cpu"`, `"gpu"` and `"nwords"` (words per second). Defaults to `{}`. ~~Dict[str, Optional[Union[float, str]]]~~                                                                                                   |
| `spacy_git_version` <Tag variant="new">3</Tag> | Git commit of [`spacy`](https://github.com/explosion/spaCy) used to create pipeline. ~~str~~                                                                                                                                                                                                                                     |
| other                                          | Any other custom meta information you want to add. The data is preserved in [`nlp.meta`](/api/language#meta). ~~Any~~                                                                                                                                                                                                            |
