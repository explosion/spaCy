---
title: Training Models
next: /usage/projects
menu:
  - ['Introduction', 'basics']
  - ['CLI & Config', 'cli-config']
  - ['Transfer Learning', 'transfer-learning']
  - ['Custom Models', 'custom-models']
  - ['Parallel Training', 'parallel-training']
  - ['Internal API', 'api']
---

## Introduction to training models {#basics hidden="true"}

import Training101 from 'usage/101/\_training.md'

<Training101 />

<Infobox title="Tip: Try the Prodigy annotation tool">

[![Prodigy: Radically efficient machine teaching](../images/prodigy.jpg)](https://prodi.gy)

If you need to label a lot of data, check out [Prodigy](https://prodi.gy), a
new, active learning-powered annotation tool we've developed. Prodigy is fast
and extensible, and comes with a modern **web application** that helps you
collect training data faster. It integrates seamlessly with spaCy, pre-selects
the **most relevant examples** for annotation, and lets you train and evaluate
ready-to-use spaCy models.

</Infobox>

## Training CLI & config {#cli-config}

<!-- TODO: intro describing the new v3 training philosophy -->

The recommended way to train your spaCy models is via the
[`spacy train`](/api/cli#train) command on the command line.

1. The **training and evaluation data** in spaCy's
   [binary `.spacy` format](/api/data-formats#binary-training) created using
   [`spacy convert`](/api/cli#convert).
2. A [`config.cfg`](#config) **configuration file** with all settings and
   hyperparameters.
3. An optional **Python file** to register
   [custom models and architectures](#custom-models).

<!-- TODO: decide how we want to present the "getting started" workflow here, get a default config etc. -->

```bash
$ python -m spacy train train.spacy dev.spacy config.cfg --output ./output
```

> #### Tip: Debug your data
>
> The [`debug-data` command](/api/cli#debug-data) lets you analyze and validate
> your training and development data, get useful stats, and find problems like
> invalid entity annotations, cyclic dependencies, low data labels and more.
>
> ```bash
> $ python -m spacy debug-data en train.spacy dev.spacy --verbose
> ```

<Project id="some_example_project">

The easiest way to get started with an end-to-end training process is to clone a
[project](/usage/projects) template. Projects let you manage multi-step
workflows, from data preprocessing to training and packaging your model.

</Project>

<Accordion title="Understanding the training output">

When you train a model using the [`spacy train`](/api/cli#train) command, you'll
see a table showing metrics after each pass over the data. Here's what those
metrics means:

<!-- TODO: update table below with updated metrics if needed -->

| Name       | Description                                                                                       |
| ---------- | ------------------------------------------------------------------------------------------------- |
| `Dep Loss` | Training loss for dependency parser. Should decrease, but usually not to 0.                       |
| `NER Loss` | Training loss for named entity recognizer. Should decrease, but usually not to 0.                 |
| `UAS`      | Unlabeled attachment score for parser. The percentage of unlabeled correct arcs. Should increase. |
| `NER P.`   | NER precision on development data. Should increase.                                               |
| `NER R.`   | NER recall on development data. Should increase.                                                  |
| `NER F.`   | NER F-score on development data. Should increase.                                                 |
| `Tag %`    | Fine-grained part-of-speech tag accuracy on development data. Should increase.                    |
| `Token %`  | Tokenization accuracy on development data.                                                        |
| `CPU WPS`  | Prediction speed on CPU in words per second, if available. Should stay stable.                    |
| `GPU WPS`  | Prediction speed on GPU in words per second, if available. Should stay stable.                    |

Note that if the development data has raw text, some of the gold-standard
entities might not align to the predicted tokenization. These tokenization
errors are **excluded from the NER evaluation**. If your tokenization makes it
impossible for the model to predict 50% of your entities, your NER F-score might
still look good.

</Accordion>

---

### Training config files {#config}

> #### Migration from spaCy v2.x
>
> TODO: once we have an answer for how to update the training command
> (`spacy migrate`?), add details here

Training config files include all **settings and hyperparameters** for training
your model. Instead of providing lots of arguments on the command line, you only
need to pass your `config.cfg` file to [`spacy train`](/api/cli#train). Under
the hood, the training config uses the
[configuration system](https://thinc.ai/docs/usage-config) provided by our
machine learning library [Thinc](https://thinc.ai). This also makes it easy to
integrate custom models and architectures, written in your framework of choice.
Some of the main advantages and features of spaCy's training config are:

- **Structured sections.** The config is grouped into sections, and nested
  sections are defined using the `.` notation. For example, `[nlp.pipeline.ner]`
  defines the settings for the pipeline's named entity recognizer. The config
  can be loaded as a Python dict.
- **References to registered functions.** Sections can refer to registered
  functions like [model architectures](/api/architectures),
  [optimizers](https://thinc.ai/docs/api-optimizers) or
  [schedules](https://thinc.ai/docs/api-schedules) and define arguments that are
  passed into them. You can also register your own functions to define
  [custom architectures](#custom-models), reference them in your config and
  tweak their parameters.
- **Interpolation.** If you have hyperparameters used by multiple components,
  define them once and reference them as variables.
- **Reproducibility with no hidden defaults.** The config file is the "single
  source of truth" and includes all settings. <!-- TODO: explain this better -->
- **Automated checks and validation.** When you load a config, spaCy checks if
  the settings are complete and if all values have the correct types. This lets
  you catch potential mistakes early. In your custom architectures, you can use
  Python [type hints](https://docs.python.org/3/library/typing.html) to tell the
  config which types of data to expect.

<!-- TODO: instead of hard-coding a full config here, we probably want to embed it from GitHub, e.g. from one of the project templates. This also makes it easier to keep it up to date, and the embed widgets take up less space-->

```ini
[training]
use_gpu = -1
limit = 0
dropout = 0.2
patience = 1000
eval_frequency = 20
scores = ["ents_p", "ents_r", "ents_f"]
score_weights = {"ents_f": 1}
orth_variant_level = 0.0
gold_preproc = false
max_length = 0
seed = 0
accumulate_gradient = 1
discard_oversize = false

[training.batch_size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001

[training.optimizer]
@optimizers = "Adam.v1"
learn_rate = 0.001
beta1 = 0.9
beta2 = 0.999
use_averages = false

[nlp]
lang = "en"
vectors = null

[nlp.pipeline.ner]
factory = "ner"

[nlp.pipeline.ner.model]
@architectures = "spacy.TransitionBasedParser.v1"
nr_feature_tokens = 3
hidden_width = 128
maxout_pieces = 3
use_upper = true

[nlp.pipeline.ner.model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v1"
width = 128
depth = 4
embed_size = 7000
maxout_pieces = 3
window_size = 1
subword_features = true
pretrained_vectors = null
dropout = null
```

<!-- TODO: explain settings and @ notation, refer to function registry docs -->

<Infobox title="Config format and settings" emoji="📖">

For a full overview of spaCy's config format and settings, see the
[training format documentation](/api/data-formats#config). The settings
available for the different architectures are documented with the
[model architectures API](/api/architectures). See the Thinc documentation for
[optimizers](https://thinc.ai/docs/api-optimizers) and
[schedules](https://thinc.ai/docs/api-schedules).

</Infobox>

#### Using registered functions {#config-functions}

The training configuration defined in the config file doesn't have to only
consist of static values. Some settings can also be **functions**. For instance,
the `batch_size` can be a number that doesn't change, or a schedule, like a
sequence of compounding values, which has shown to be an effective trick (see
[Smith et al., 2017](https://arxiv.org/abs/1711.00489)).

```ini
### With static value
[training]
batch_size = 128
```

To refer to a function instead, you can make `[training.batch_size]` its own
section and use the `@` syntax specify the function and its arguments – in this
case [`compounding.v1`](https://thinc.ai/docs/api-schedules#compounding) defined
in the [function registry](/api/top-level#registry). All other values defined in
the block are passed to the function as keyword arguments when it's initialized.
You can also use this mechanism to register
[custom implementations and architectures](#custom-models) and reference them
from your configs.

> #### TODO
>
> TODO: something about how the tree is built bottom-up?

```ini
### With registered function
[training.batch_size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001
```

### Model architectures {#model-architectures}

<!-- TODO: refer to architectures API: /api/architectures. This should document the architectures in spacy/ml/models -->

<!-- TODO: how do we document the default configs? -->

## Transfer learning {#transfer-learning}

### Using transformer models like BERT {#transformers}

<!-- TODO: document usage of spacy-transformers, refer to example config/project -->

<Project id="en_core_bert">

Try out a BERT-based model pipeline using this project template: swap in your
data, edit the settings and hyperparameters and train, evaluate, package and
visualize your model.

</Project>

### Pretraining with spaCy {#pretraining}

<!-- TODO: document spacy pretrain -->

## Custom model implementations and architectures {#custom-models}

<!-- TODO: intro, should summarise what spaCy v3 can do and that you can now use fully custom implementations, models defined in PyTorch and TF, etc. etc. -->

### Training with custom code {#custom-code}

The [`spacy train`](/api/cli#train) recipe lets you specify an optional argument
`--code` that points to a Python file. The file is imported before training and
allows you to add custom functions and architectures to the function registry
that can then be referenced from your `config.cfg`. This lets you train spaCy
models with custom components, without having to re-implement the whole training
workflow.

For example, let's say you've implemented your own batch size schedule to use
during training. The `@spacy.registry.schedules` decorator lets you register
that function in the `schedules` [registry](/api/top-level#registry) and assign
it a string name:

> #### Why the version in the name?
>
> A big benefit of the config system is that it makes your experiments
> reproducible. We recommend versioning the functions you register, especially
> if you expect them to change (like a new model architecture). This way, you
> know that a config referencing `v1` means a different function than a config
> referencing `v2`.

```python
### functions.py
import spacy

@spacy.registry.schedules("my_custom_schedule.v1")
def my_custom_schedule(start: int = 1, factor: int = 1.001):
   while True:
      yield start
      start = start * factor
```

In your config, you can now reference the schedule in the
`[training.batch_size]` block via `@schedules`. If a block contains a key
starting with an `@`, it's interpreted as a reference to a function. All other
settings in the block will be passed to the function as keyword arguments. Keep
in mind that the config shouldn't have any hidden defaults and all arguments on
the functions need to be represented in the config.

<!-- TODO: this needs to be updated once we've decided on a workflow for "fill config" -->

```ini
### config.cfg (excerpt)
[training.batch_size]
@schedules = "my_custom_schedule.v1"
start = 2
factor = 1.005
```

You can now run [`spacy train`](/api/cli#train) with the `config.cfg` and your
custom `functions.py` as the argument `--code`. Before loading the config, spaCy
will import the `functions.py` module and your custom functions will be
registered.

```bash
### Training with custom code {wrap="true"}
python -m spacy train train.spacy dev.spacy config.cfg --output ./output --code ./functions.py
```

<Infobox title="Tip: Use Python type hints" emoji="💡">

spaCy's configs are powered by our machine learning library Thinc's
[configuration system](https://thinc.ai/docs/usage-config), which supports
[type hints](https://docs.python.org/3/library/typing.html) and even
[advanced type annotations](https://thinc.ai/docs/usage-config#advanced-types)
using [`pydantic`](https://github.com/samuelcolvin/pydantic). If your registered
function provides For example, `start: int` in the example above will ensure
that the value received as the argument `start` is an integer. If the value
can't be cast to an integer, spaCy will raise an error.
`start: pydantic.StrictInt` will force the value to be an integer and raise an
error if it's not – for instance, if your config defines a float.

</Infobox>

### Defining custom architectures {#custom-architectures}

<!-- TODO: this could maybe be a more general example of using Thinc to compose some layers? We don't want to go too deep here and probably want to focus on a simple architecture example to show how it works -->

### Wrapping PyTorch and TensorFlow {#custom-frameworks}

<!-- TODO:  -->

<Project id="example_pytorch_model">

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus interdum
sodales lectus, ut sodales orci ullamcorper id. Sed condimentum neque ut erat
mattis pretium.

</Project>

## Parallel Training with Ray {#parallel-training}

<!-- TODO: document Ray integration -->

<Project id="some_example_project">

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus interdum
sodales lectus, ut sodales orci ullamcorper id. Sed condimentum neque ut erat
mattis pretium.

</Project>

## Internal training API {#api}

<!-- TODO: rewrite for new nlp.update / example logic -->

The [`GoldParse`](/api/goldparse) object collects the annotated training
examples, also called the **gold standard**. It's initialized with the
[`Doc`](/api/doc) object it refers to, and keyword arguments specifying the
annotations, like `tags` or `entities`. Its job is to encode the annotations,
keep them aligned and create the C-level data structures required for efficient
access. Here's an example of a simple `GoldParse` for part-of-speech tags:

```python
vocab = Vocab(tag_map={"N": {"pos": "NOUN"}, "V": {"pos": "VERB"}})
doc = Doc(vocab, words=["I", "like", "stuff"])
gold = GoldParse(doc, tags=["N", "V", "N"])
```

Using the `Doc` and its gold-standard annotations, the model can be updated to
learn a sentence of three words with their assigned part-of-speech tags. The
[tag map](/usage/adding-languages#tag-map) is part of the vocabulary and defines
the annotation scheme. If you're training a new language model, this will let
you map the tags present in the treebank you train on to spaCy's tag scheme.

```python
doc = Doc(Vocab(), words=["Facebook", "released", "React", "in", "2014"])
gold = GoldParse(doc, entities=["U-ORG", "O", "U-TECHNOLOGY", "O", "U-DATE"])
```

The same goes for named entities. The letters added before the labels refer to
the tags of the [BILUO scheme](/usage/linguistic-features#updating-biluo) – `O`
is a token outside an entity, `U` an single entity unit, `B` the beginning of an
entity, `I` a token inside an entity and `L` the last token of an entity.

> - **Training data**: The training examples.
> - **Text and label**: The current example.
> - **Doc**: A `Doc` object created from the example text.
> - **GoldParse**: A `GoldParse` object of the `Doc` and label.
> - **nlp**: The `nlp` object with the model.
> - **Optimizer**: A function that holds state between updates.
> - **Update**: Update the model's weights.

![The training loop](../images/training-loop.svg)

Of course, it's not enough to only show a model a single example once.
Especially if you only have few examples, you'll want to train for a **number of
iterations**. At each iteration, the training data is **shuffled** to ensure the
model doesn't make any generalizations based on the order of examples. Another
technique to improve the learning results is to set a **dropout rate**, a rate
at which to randomly "drop" individual features and representations. This makes
it harder for the model to memorize the training data. For example, a `0.25`
dropout means that each feature or internal representation has a 1/4 likelihood
of being dropped.

> - [`begin_training`](/api/language#begin_training): Start the training and
>   return an optimizer function to update the model's weights. Can take an
>   optional function converting the training data to spaCy's training format.
> - [`update`](/api/language#update): Update the model with the training example
>   and gold data.
> - [`to_disk`](/api/language#to_disk): Save the updated model to a directory.

```python
### Example training loop
optimizer = nlp.begin_training(get_data)
for itn in range(100):
    random.shuffle(train_data)
    for raw_text, entity_offsets in train_data:
        doc = nlp.make_doc(raw_text)
        gold = GoldParse(doc, entities=entity_offsets)
        nlp.update([doc], [gold], drop=0.5, sgd=optimizer)
nlp.to_disk("/model")
```

The [`nlp.update`](/api/language#update) method takes the following arguments:

| Name    | Description                                                                                                                                                                                                   |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs`  | [`Doc`](/api/doc) objects. The `update` method takes a sequence of them, so you can batch up your training examples. Alternatively, you can also pass in a sequence of raw texts.                             |
| `golds` | [`GoldParse`](/api/goldparse) objects. The `update` method takes a sequence of them, so you can batch up your training examples. Alternatively, you can also pass in a dictionary containing the annotations. |
| `drop`  | Dropout rate. Makes it harder for the model to just memorize the data.                                                                                                                                        |
| `sgd`   | An optimizer, i.e. a callable to update the model's weights. If not set, spaCy will create a new one and save it for further use.                                                                             |

Instead of writing your own training loop, you can also use the built-in
[`train`](/api/cli#train) command, which expects data in spaCy's
[JSON format](/api/data-formats#json-input). On each epoch, a model will be
saved out to the directory.
