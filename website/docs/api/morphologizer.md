---
title: Morphologizer
tag: class
source: spacy/pipeline/morphologizer.pyx
new: 3
teaser: 'Pipeline component for predicting morphological features'
api_base_class: /api/tagger
api_string_name: morphologizer
api_trainable: true
---

A trainable pipeline component to predict morphological features and
coarse-grained POS tags following the Universal Dependencies
[UPOS](https://universaldependencies.org/u/pos/index.html) and
[FEATS](https://universaldependencies.org/format.html#morphological-annotation)
annotation guidelines.

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
> from spacy.pipeline.morphologizer import DEFAULT_MORPH_MODEL
> config = {"model": DEFAULT_MORPH_MODEL}
> nlp.add_pipe("morphologizer", config=config)
> ```

| Setting | Type                                       | Description       | Default                             |
| ------- | ------------------------------------------ | ----------------- | ----------------------------------- |
| `model` | [`Model`](https://thinc.ai/docs/api-model) | The model to use. | [Tagger](/api/architectures#Tagger) |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/morphologizer.pyx
```

## Morphologizer.\_\_init\_\_ {#init tag="method"}

Initialize the morphologizer.

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> morphologizer = nlp.add_pipe("morphologizer")
>
> # Construction via create_pipe with custom model
> config = {"model": {"@architectures": "my_morphologizer"}}
> morphologizer = nlp.add_pipe("morphologizer", config=config)
>
> # Construction from class
> from spacy.pipeline import Morphologizer
> morphologizer = Morphologizer(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

| Name           | Type    | Description                                                                                 |
| -------------- | ------- | ------------------------------------------------------------------------------------------- |
| `vocab`        | `Vocab` | The shared vocabulary.                                                                      |
| `model`        | `Model` | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.             |
| `name`         | str     | String name of the component instance. Used to add entries to the `losses` during training. |
| _keyword-only_ |         |                                                                                             |
| `labels_morph` | dict    | Mapping of morph + POS tags to morph labels.                                                |
| `labels_pos`   | dict    | Mapping of morph + POS tags to POS tags.                                                    |

## Morphologizer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/morphologizer#call) and [`pipe`](/api/morphologizer#pipe)
delegate to the [`predict`](/api/morphologizer#predict) and
[`set_annotations`](/api/morphologizer#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> morphologizer = nlp.add_pipe("morphologizer")
> # This usually happens under the hood
> processed = morphologizer(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## Morphologizer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/morphologizer#call) and
[`pipe`](/api/morphologizer#pipe) delegate to the
[`predict`](/api/morphologizer#predict) and
[`set_annotations`](/api/morphologizer#set_annotations) methods.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> for doc in morphologizer.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                            |
| -------------- | --------------- | ------------------------------------------------------ |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                 |
| _keyword-only_ |                 |                                                        |
| `batch_size`   | int             | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**     | `Doc`           | Processed documents in the order of the original text. |

## Morphologizer.begin_training {#begin_training tag="method"}

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
> morphologizer = nlp.add_pipe("morphologizer")
> nlp.pipeline.append(morphologizer)
> optimizer = morphologizer.begin_training(lambda: [], pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                           |
| -------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects.            |
| _keyword-only_ |                                                     |                                                                                                                       |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                                  |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/sentencerecognizer#create_optimizer) if not set. |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                        |

## Morphologizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> scores = morphologizer.predict([doc1, doc2])
> ```

| Name        | Type            | Description                               |
| ----------- | --------------- | ----------------------------------------- |
| `docs`      | `Iterable[Doc]` | The documents to predict.                 |
| **RETURNS** | -               | The model's prediction for each document. |

## Morphologizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> scores = morphologizer.predict([doc1, doc2])
> morphologizer.set_annotations([doc1, doc2], scores)
> ```

| Name     | Type            | Description                                             |
| -------- | --------------- | ------------------------------------------------------- |
| `docs`   | `Iterable[Doc]` | The documents to modify.                                |
| `scores` | -               | The scores to set, produced by `Morphologizer.predict`. |

## Morphologizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects containing the
predictions and gold-standard annotations, and update the component's model.
Delegates to [`predict`](/api/morphologizer#predict) and
[`get_loss`](/api/morphologizer#get_loss).

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> optimizer = nlp.begin_training()
> losses = morphologizer.update(examples, sgd=optimizer)
> ```

| Name              | Type                                                | Description                                                                                                                                      |
| ----------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `examples`        | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects to learn from.                                                                                      |
| _keyword-only_    |                                                     |                                                                                                                                                  |
| `drop`            | float                                               | The dropout rate.                                                                                                                                |
| `set_annotations` | bool                                                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/sentencerecognizer#set_annotations). |
| `sgd`             | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                                                   |
| `losses`          | `Dict[str, float]`                                  | Optional record of the loss during training. The value keyed by the model's name is updated.                                                     |
| **RETURNS**       | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                                                                                 |

## Morphologizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> scores = morphologizer.predict([eg.predicted for eg in examples])
> loss, d_loss = morphologizer.get_loss(examples, scores)
> ```

| Name        | Type                  | Description                                         |
| ----------- | --------------------- | --------------------------------------------------- |
| `examples`  | `Iterable[Example]`   | The batch of examples.                              |
| `scores`    | -                     | Scores representing the model's predictions.        |
| **RETURNS** | `Tuple[float, float]` | The loss and the gradient, i.e. `(loss, gradient)`. |

## Morphologizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> optimizer = morphologizer.create_optimizer()
> ```

| Name        | Type                                                | Description    |
| ----------- | --------------------------------------------------- | -------------- |
| **RETURNS** | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer. |

## Morphologizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> with morphologizer.use_params(optimizer.averages):
>     morphologizer.to_disk("/best_model")
> ```

| Name     | Type | Description                               |
| -------- | ---- | ----------------------------------------- |
| `params` | dict | The parameter values to use in the model. |

## Morphologizer.add_label {#add_label tag="method"}

Add a new label to the pipe. If the `Morphologizer` should set annotations for
both `pos` and `morph`, the label should include the UPOS as the feature `POS`.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer.add_label("Mood=Ind|POS=VERB|Tense=Past|VerbForm=Fin")
> ```

| Name        | Type | Description                                         |
| ----------- | ---- | --------------------------------------------------- |
| `label`     | str  | The label to add.                                   |
| **RETURNS** | int  | `0` if the label is already present, otherwise `1`. |

## Morphologizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer.to_disk("/path/to/morphologizer")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## Morphologizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer.from_disk("/path/to/morphologizer")
> ```

| Name           | Type            | Description                                                                |
| -------------- | --------------- | -------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                            |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `Morphologizer` | The modified `Morphologizer` object.                                       |

## Morphologizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer_bytes = morphologizer.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the `Morphologizer` object.                        |

## Morphologizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> morphologizer_bytes = morphologizer.to_bytes()
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer.from_bytes(morphologizer_bytes)
> ```

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| `bytes_data`   | bytes           | The data to load from.                                                    |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | `Morphologizer` | The `Morphologizer` object.                                               |

## Morphologizer.labels {#labels tag="property"}

The labels currently added to the component in Universal Dependencies
[FEATS format](https://universaldependencies.org/format.html#morphological-annotation).
Note that even for a blank component, this will always include the internal
empty label `_`. If POS features are used, the labels will include the
coarse-grained POS as the feature `POS`.

> #### Example
>
> ```python
> morphologizer.add_label("Mood=Ind|POS=VERB|Tense=Past|VerbForm=Fin")
> assert "Mood=Ind|POS=VERB|Tense=Past|VerbForm=Fin" in morphologizer.labels
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
> data = morphologizer.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
