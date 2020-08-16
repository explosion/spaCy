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
> }
> nlp.add_pipe("ner", config=config)
> ```

| Setting                       | Type                                       | Description                                                                                                                                                                                                              | Default                                                           |
| ----------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| `moves`                       | `List[str]`                                | A list of transition names. Inferred from the data if not provided.                                                                                                                                                      |
| `update_with_oracle_cut_size` | int                                        | During training, cut long sequences into shorter segments by creating intermediate states based on the gold-standard history. The model is not very sensitive to this parameter, so you usually won't need to change it. | `100`                                                             |
| `model`                       | [`Model`](https://thinc.ai/docs/api-model) | The model to use.                                                                                                                                                                                                        | [TransitionBasedParser](/api/architectures#TransitionBasedParser) |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/ner.pyx
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

| Name                          | Type                                       | Description                                                                                                                                                                                                                                       |
| ----------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`                       | `Vocab`                                    | The shared vocabulary.                                                                                                                                                                                                                            |
| `model`                       | [`Model`](https://thinc.ai/docs/api-model) | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.                                                                                                                                                                   |
| `name`                        | str                                        | String name of the component instance. Used to add entries to the `losses` during training.                                                                                                                                                       |
| `moves`                       | `List[str]`                                | A list of transition names. Inferred from the data if not provided.                                                                                                                                                                               |
| _keyword-only_                |                                            |                                                                                                                                                                                                                                                   |
| `update_with_oracle_cut_size` | int                                        | During training, cut long sequences into shorter segments by creating intermediate states based on the gold-standard history. The model is not very sensitive to this parameter, so you usually won't need to change it. `100` is a good default. |

## EntityRecognizer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
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

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

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

| Name           | Type            | Description                                            |
| -------------- | --------------- | ------------------------------------------------------ |
| `docs`         | `Iterable[Doc]` | A stream of documents.                                 |
| _keyword-only_ |                 |                                                        |
| `batch_size`   | int             | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**     | `Doc`           | Processed documents in the order of the original text. |

## EntityRecognizer.begin_training {#begin_training tag="method"}

Initialize the component for training and return an
[`Optimizer`](https://thinc.ai/docs/api-optimizers). `get_examples` should be a
function that returns an iterable of [`Example`](/api/example) objects. The data
examples are used to **initialize the model** of the component and can either be
the full training data or a representative sample. Initialization includes
validating the network,
[inferring missing shapes](https://thinc.ai/docs/usage-models#validation) and
setting up the label scheme based on the data.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> optimizer = ner.begin_training(lambda: [], pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                         |
| -------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects.          |
| _keyword-only_ |                                                     |                                                                                                                     |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                                |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/entityrecognizer#create_optimizer) if not set. |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                      |

## EntityRecognizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> scores = ner.predict([doc1, doc2])
> ```

| Name        | Type               | Description                                                                                                |
| ----------- | ------------------ | ---------------------------------------------------------------------------------------------------------- |
| `docs`      | `Iterable[Doc]`    | The documents to predict.                                                                                  |
| **RETURNS** | `List[StateClass]` | List of `syntax.StateClass` objects. `syntax.StateClass` is a helper class for the parse state (internal). |

## EntityRecognizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> scores = ner.predict([doc1, doc2])
> ner.set_annotations([doc1, doc2], scores)
> ```

| Name     | Type               | Description                                                |
| -------- | ------------------ | ---------------------------------------------------------- |
| `docs`   | `Iterable[Doc]`    | The documents to modify.                                   |
| `scores` | `List[StateClass]` | The scores to set, produced by `EntityRecognizer.predict`. |

## EntityRecognizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects, updating the pipe's
model. Delegates to [`predict`](/api/entityrecognizer#predict) and
[`get_loss`](/api/entityrecognizer#get_loss).

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> optimizer = nlp.begin_training()
> losses = ner.update(examples, sgd=optimizer)
> ```

| Name              | Type                                                | Description                                                                                                                                    |
| ----------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects to learn from.                                                                                    |
| _keyword-only_    |                                                     |                                                                                                                                                |
| `drop`            | float                                               | The dropout rate.                                                                                                                              |
| `set_annotations` | bool                                                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/entityrecognizer#set_annotations). |
| `sgd`             | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                                                 |
| `losses`          | `Dict[str, float]`                                  | Optional record of the loss during training. Updated using the component name as the key.                                                      |
| **RETURNS**       | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                                                                               |

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

| Name        | Type                  | Description                                         |
| ----------- | --------------------- | --------------------------------------------------- |
| `examples`  | `Iterable[Example]`   | The batch of examples.                              |
| `scores`    | `List[StateClass]`    | Scores representing the model's predictions.        |
| **RETURNS** | `Tuple[float, float]` | The loss and the gradient, i.e. `(loss, gradient)`. |

## EntityRecognizer.score {#score tag="method" new="3"}

Score a batch of examples.

> #### Example
>
> ```python
> scores = ner.score(examples)
> ```

| Name        | Type                | Description                                                              |
| ----------- | ------------------- | ------------------------------------------------------------------------ |
| `examples`  | `Iterable[Example]` | The examples to score.                                                   |
| **RETURNS** | `Dict[str, Any]`    | The scores, produced by [`Scorer.score_spans`](/api/scorer#score_spans). |

## EntityRecognizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> optimizer = ner.create_optimizer()
> ```

| Name        | Type                                                | Description    |
| ----------- | --------------------------------------------------- | -------------- |
| **RETURNS** | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer. |

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

| Name     | Type | Description                               |
| -------- | ---- | ----------------------------------------- |
| `params` | dict | The parameter values to use in the model. |

## EntityRecognizer.add_label {#add_label tag="method"}

Add a new label to the pipe.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.add_label("MY_LABEL")
> ```

| Name        | Type | Description                                         |
| ----------- | ---- | --------------------------------------------------- |
| `label`     | str  | The label to add.                                   |
| **RETURNS** | int  | `0` if the label is already present, otherwise `1`. |

## EntityRecognizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.to_disk("/path/to/ner")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## EntityRecognizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.from_disk("/path/to/ner")
> ```

| Name           | Type               | Description                                                                |
| -------------- | ------------------ | -------------------------------------------------------------------------- |
| `path`         | str / `Path`       | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                    |                                                                            |
| `exclude`      | `Iterable[str]`    | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `EntityRecognizer` | The modified `EntityRecognizer` object.                                    |

## EntityRecognizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner_bytes = ner.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the `EntityRecognizer` object.                     |

## EntityRecognizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ner_bytes = ner.to_bytes()
> ner = nlp.add_pipe("ner")
> ner.from_bytes(ner_bytes)
> ```

| Name           | Type               | Description                                                               |
| -------------- | ------------------ | ------------------------------------------------------------------------- |
| `bytes_data`   | bytes              | The data to load from.                                                    |
| _keyword-only_ |                    |                                                                           |
| `exclude`      | `Iterable[str]`    | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | `EntityRecognizer` | The `EntityRecognizer` object.                                            |

## EntityRecognizer.labels {#labels tag="property"}

The labels currently added to the component.

> #### Example
>
> ```python
> ner.add_label("MY_LABEL")
> assert "MY_LABEL" in ner.labels
> ```

| Name        | Type  | Description                        |
| ----------- | ----- | ---------------------------------- |
| **RETURNS** | tuple | The labels added to the component. |

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
