---
title: EntityRecognizer
tag: class
source: spacy/pipeline/ner.pyx
teaser: 'Pipeline component for named entity recognition'
api_base_class: /api/pipe
api_string_name: ner
api_trainable: true
---

A transition-based named entity recognition component. The entity recognizer
identifies **non-overlapping labelled spans** of tokens. The transition-based
algorithm used encodes certain assumptions that are effective for "traditional"
named entity recognition tasks, but may not be a good fit for every span
identification problem. Specifically, the loss function optimizes for **whole
entity accuracy**, so if your inter-annotator agreement on boundary tokens is
low, the component will likely perform poorly on your problem. The
transition-based algorithm also assumes that the most decisive information about
your entities will be close to their initial tokens. If your entities are long
and characterized by tokens in their middle, the component will likely not be a
good fit for your task.

## Assigned Attributes {#assigned-attributes}

Predictions will be saved to `Doc.ents` as a tuple. Each label will also be
reflected to each underlying token, where it is saved in the `Token.ent_type`
and `Token.ent_iob` fields. Note that by definition each token can only have one
label.

When setting `Doc.ents` to create training data, all the spans must be valid and
non-overlapping, or an error will be thrown.

| Location          | Value                                                             |
| ----------------- | ----------------------------------------------------------------- |
| `Doc.ents`        | The annotated spans. ~~Tuple[Span]~~                              |
| `Token.ent_iob`   | An enum encoding of the IOB part of the named entity tag. ~~int~~ |
| `Token.ent_iob_`  | The IOB part of the named entity tag. ~~str~~                     |
| `Token.ent_type`  | The label part of the named entity tag (hash). ~~int~~            |
| `Token.ent_type_` | The label part of the named entity tag. ~~str~~                   |

## Config and implementation {#config}

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config). See the
[model architectures](/api/architectures) documentation for details on the
architectures and their arguments and hyperparameters.

> #### Example
>
> ```python
> from spacy.pipeline.ner import DEFAULT_NER_MODEL
> config = {
>    "moves": None,
>    "update_with_oracle_cut_size": 100,
>    "model": DEFAULT_NER_MODEL,
>    "incorrect_spans_key": "incorrect_spans",
> }
> nlp.add_pipe("ner", config=config)
> ```

| Setting                       | Description                                                                                                                                                                                                                                         |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `moves`                       | A list of transition names. Inferred from the data if not provided. Defaults to `None`. ~~Optional[TransitionSystem]~~                                                                                                                              |
| `update_with_oracle_cut_size` | During training, cut long sequences into shorter segments by creating intermediate states based on the gold-standard history. The model is not very sensitive to this parameter, so you usually won't need to change it. Defaults to `100`. ~~int~~ |
| `model`                       | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. Defaults to [TransitionBasedParser](/api/architectures#TransitionBasedParser). ~~Model[List[Doc], List[Floats2d]]~~                                                 |
| `incorrect_spans_key`         | This key refers to a `SpanGroup` in `doc.spans` that specifies incorrect spans. The NER will learn not to predict (exactly) those spans. Defaults to `None`. ~~Optional[str]~~                                                                      |
| `scorer`                      | The scoring method. Defaults to [`spacy.scorer.get_ner_prf`](/api/scorer#get_ner_prf). ~~Optional[Callable]~~                                                                                                                                       |

```python
%%GITHUB_SPACY/spacy/pipeline/ner.pyx
```

## EntityRecognizer.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> ner = nlp.add_pipe("ner")
>
> # Construction via add_pipe with custom model
> config = {"model": {"@architectures": "my_ner"}}
> parser = nlp.add_pipe("ner", config=config)
>
> # Construction from class
> from spacy.pipeline import EntityRecognizer
> ner = EntityRecognizer(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

| Name                          | Description                                                                                                                                                                                                                                         |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`                       | The shared vocabulary. ~~Vocab~~                                                                                                                                                                                                                    |
| `model`                       | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                |
| `name`                        | String name of the component instance. Used to add entries to the `losses` during training. ~~str~~                                                                                                                                                 |
| `moves`                       | A list of transition names. Inferred from the data if set to `None`, which is the default. ~~Optional[TransitionSystem]~~                                                                                                                           |
| _keyword-only_                |                                                                                                                                                                                                                                                     |
| `update_with_oracle_cut_size` | During training, cut long sequences into shorter segments by creating intermediate states based on the gold-standard history. The model is not very sensitive to this parameter, so you usually won't need to change it. Defaults to `100`. ~~int~~ |
| `incorrect_spans_key`         | Identifies spans that are known to be incorrect entity annotations. The incorrect entity annotations can be stored in the span group in [`Doc.spans`](/api/doc#spans), under this key. Defaults to `None`. ~~Optional[str]~~                        |

## EntityRecognizer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/entityrecognizer#call) and
[`pipe`](/api/entityrecognizer#pipe) delegate to the
[`predict`](/api/entityrecognizer#predict) and
[`set_annotations`](/api/entityrecognizer#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> ner = nlp.add_pipe("ner")
> # This usually happens under the hood
> processed = ner(doc)
> ```

| Name        | Description                      |
| ----------- | -------------------------------- |
| `doc`       | The document to process. ~~Doc~~ |
| **RETURNS** | The processed document. ~~Doc~~  |

## EntityRecognizer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/entityrecognizer#call) and
[`pipe`](/api/entityrecognizer#pipe) delegate to the
[`predict`](/api/entityrecognizer#predict) and
[`set_annotations`](/api/entityrecognizer#set_annotations) methods.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> for doc in ner.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `docs`         | A stream of documents. ~~Iterable[Doc]~~                      |
| _keyword-only_ |                                                               |
| `batch_size`   | The number of documents to buffer. Defaults to `128`. ~~int~~ |
| **YIELDS**     | The processed documents in order. ~~Doc~~                     |

## EntityRecognizer.initialize {#initialize tag="method" new="3"}

Initialize the component for training. `get_examples` should be a function that
returns an iterable of [`Example`](/api/example) objects. **At least one example
should be supplied.** The data examples are used to **initialize the model** of
the component and can either be the full training data or a representative
sample. Initialization includes validating the network,
[inferring missing shapes](https://thinc.ai/docs/usage-models#validation) and
setting up the label scheme based on the data. This method is typically called
by [`Language.initialize`](/api/language#initialize) and lets you customize
arguments it receives via the
[`[initialize.components]`](/api/data-formats#config-initialize) block in the
config.

<Infobox variant="warning" title="Changed in v3.0" id="begin_training">

This method was previously called `begin_training`.

</Infobox>

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.initialize(lambda: examples, nlp=nlp)
> ```
>
> ```ini
> ### config.cfg
> [initialize.components.ner]
>
> [initialize.components.ner.labels]
> @readers = "spacy.read_labels.v1"
> path = "corpus/labels/ner.json
> ```

| Name           | Description                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. Must contain at least one `Example`. ~~Callable[[], Iterable[Example]]~~                                                                                                                                                                                                                                             |
| _keyword-only_ |                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `nlp`          | The current `nlp` object. Defaults to `None`. ~~Optional[Language]~~                                                                                                                                                                                                                                                                                                                                                   |
| `labels`       | The label information to add to the component, as provided by the [`label_data`](#label_data) property after initialization. To generate a reusable JSON file from your data, you should run the [`init labels`](/api/cli#init-labels) command. If no labels are provided, the `get_examples` callback is used to extract the labels from the data, which may be a lot slower. ~~Optional[Dict[str, Dict[str, int]]]~~ |

## EntityRecognizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> scores = ner.predict([doc1, doc2])
> ```

| Name        | Description                                                   |
| ----------- | ------------------------------------------------------------- |
| `docs`      | The documents to predict. ~~Iterable[Doc]~~                   |
| **RETURNS** | A helper class for the parse state (internal). ~~StateClass~~ |

## EntityRecognizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> scores = ner.predict([doc1, doc2])
> ner.set_annotations([doc1, doc2], scores)
> ```

| Name     | Description                                                                                                                           |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `docs`   | The documents to modify. ~~Iterable[Doc]~~                                                                                            |
| `scores` | The scores to set, produced by `EntityRecognizer.predict`. Returns an internal helper class for the parse state. ~~List[StateClass]~~ |

## EntityRecognizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects, updating the pipe's
model. Delegates to [`predict`](/api/entityrecognizer#predict) and
[`get_loss`](/api/entityrecognizer#get_loss).

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> optimizer = nlp.initialize()
> losses = ner.update(examples, sgd=optimizer)
> ```

| Name           | Description                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `examples`     | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                        |
| _keyword-only_ |                                                                                                                          |
| `drop`         | The dropout rate. ~~float~~                                                                                              |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~            |
| `losses`       | Optional record of the loss during training. Updated using the component name as the key. ~~Optional[Dict[str, float]]~~ |
| **RETURNS**    | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                    |

## EntityRecognizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> scores = ner.predict([eg.predicted for eg in examples])
> loss, d_loss = ner.get_loss(examples, scores)
> ```

| Name        | Description                                                                 |
| ----------- | --------------------------------------------------------------------------- |
| `examples`  | The batch of examples. ~~Iterable[Example]~~                                |
| `scores`    | Scores representing the model's predictions. ~~StateClass~~                 |
| **RETURNS** | The loss and the gradient, i.e. `(loss, gradient)`. ~~Tuple[float, float]~~ |

## EntityRecognizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> optimizer = ner.create_optimizer()
> ```

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The optimizer. ~~Optimizer~~ |

## EntityRecognizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> with ner.use_params(optimizer.averages):
>     ner.to_disk("/best_model")
> ```

| Name     | Description                                        |
| -------- | -------------------------------------------------- |
| `params` | The parameter values to use in the model. ~~dict~~ |

## EntityRecognizer.add_label {#add_label tag="method"}

Add a new label to the pipe. Note that you don't have to call this method if you
provide a **representative data sample** to the [`initialize`](#initialize)
method. In this case, all labels found in the sample will be automatically added
to the model, and the output dimension will be
[inferred](/usage/layers-architectures#thinc-shape-inference) automatically.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.add_label("MY_LABEL")
> ```

| Name        | Description                                                 |
| ----------- | ----------------------------------------------------------- |
| `label`     | The label to add. ~~str~~                                   |
| **RETURNS** | `0` if the label is already present, otherwise `1`. ~~int~~ |

## EntityRecognizer.set_output {#set_output tag="method"}

Change the output dimension of the component's model by calling the model's
attribute `resize_output`. This is a function that takes the original model and
the new output dimension `nO`, and changes the model in place. When resizing an
already trained model, care should be taken to avoid the "catastrophic
forgetting" problem.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.set_output(512)
> ```

| Name | Description                       |
| ---- | --------------------------------- |
| `nO` | The new output dimension. ~~int~~ |

## EntityRecognizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.to_disk("/path/to/ner")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## EntityRecognizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.from_disk("/path/to/ner")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `EntityRecognizer` object. ~~EntityRecognizer~~                                    |

## EntityRecognizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner_bytes = ner.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The serialized form of the `EntityRecognizer` object. ~~bytes~~                             |

## EntityRecognizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ner_bytes = ner.to_bytes()
> ner = nlp.add_pipe("ner")
> ner.from_bytes(ner_bytes)
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                            |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `EntityRecognizer` object. ~~EntityRecognizer~~                                         |

## EntityRecognizer.labels {#labels tag="property"}

The labels currently added to the component.

> #### Example
>
> ```python
> ner.add_label("MY_LABEL")
> assert "MY_LABEL" in ner.labels
> ```

| Name        | Description                                            |
| ----------- | ------------------------------------------------------ |
| **RETURNS** | The labels added to the component. ~~Tuple[str, ...]~~ |

## EntityRecognizer.label_data {#label_data tag="property" new="3"}

The labels currently added to the component and their internal meta information.
This is the data generated by [`init labels`](/api/cli#init-labels) and used by
[`EntityRecognizer.initialize`](/api/entityrecognizer#initialize) to initialize
the model with a pre-defined label set.

> #### Example
>
> ```python
> labels = ner.label_data
> ner.initialize(lambda: [], nlp=nlp, labels=labels)
> ```

| Name        | Description                                                                     |
| ----------- | ------------------------------------------------------------------------------- |
| **RETURNS** | The label data added to the component. ~~Dict[str, Dict[str, Dict[str, int]]]~~ |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = ner.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
