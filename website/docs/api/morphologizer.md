---
title: Morphologizer
tag: class
source: spacy/pipeline/morphologizer.pyx
new: 3
---

A trainable pipeline component to predict morphological features and
coarse-grained POS tags following the Universal Dependencies
[UPOS](https://universaldependencies.org/u/pos/index.html) and
[FEATS](https://universaldependencies.org/format.html#morphological-annotation)
annotation guidelines. This class is a subclass of `Pipe` and follows the same
API. The pipeline component is available in the
[processing pipeline](/usage/processing-pipelines) via the ID `"morphologizer"`.

## Implementation and defaults {#implementation}

See the [model architectures](/api/architectures) documentation for details on
the architectures and their arguments and hyperparameters. To learn more about
how to customize the config and train custom models, check out the
[training config](/usage/training#config) docs.

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/morphologizer.pyx
```

## Morphologizer.\_\_init\_\_ {#init tag="method"}

Initialize the morphologizer.

> #### Example
>
> ```python
> # Construction via add_pipe
> morphologizer = nlp.add_pipe("morphologizer")
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

| Name        | Type            | Description                                                                     |
| ----------- | --------------- | ------------------------------------------------------------------------------- |
| `vocab`     | `Vocab`         | The shared vocabulary.                                                          |
| `model`     | `Model`         | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. |
| `**cfg`     | -               | Configuration parameters.                                                       |
| **RETURNS** | `Morphologizer` | The newly constructed object.                                                   |

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
> morphologizer = Morphologizer(nlp.vocab)
> doc = nlp("This is a sentence.")
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
> morphologizer = Morphologizer(nlp.vocab)
> for doc in morphologizer.pipe(docs, batch_size=50):
>     pass
> ```

| Name         | Type            | Description                                            |
| ------------ | --------------- | ------------------------------------------------------ |
| `stream`     | `Iterable[Doc]` | A stream of documents.                                 |
| `batch_size` | int             | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**   | `Doc`           | Processed documents in the order of the original text. |

## Morphologizer.predict {#predict tag="method"}

Apply the pipeline's model to a batch of docs, without modifying them.

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> scores = morphologizer.predict([doc1, doc2])
> ```

| Name        | Type            | Description                               |
| ----------- | --------------- | ----------------------------------------- |
| `docs`      | `Iterable[Doc]` | The documents to predict.                 |
| **RETURNS** | -               | The model's prediction for each document. |

## Morphologizer.set_annotations {#set_annotations tag="method"}

Modify a batch of documents, using pre-computed scores.

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> scores = morphologizer.predict([doc1, doc2])
> morphologizer.set_annotations([doc1, doc2], scores)
> ```

| Name     | Type            | Description                                             |
| -------- | --------------- | ------------------------------------------------------- |
| `docs`   | `Iterable[Doc]` | The documents to modify.                                |
| `scores` | -               | The scores to set, produced by `Morphologizer.predict`. |

## Morphologizer.update {#update tag="method"}

Learn from a batch of documents and gold-standard information, updating the
pipe's model. Delegates to [`predict`](/api/morphologizer#predict) and
[`get_loss`](/api/morphologizer#get_loss).

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab, morphologizer_model)
> optimizer = nlp.begin_training()
> losses = morphologizer.update(examples, sgd=optimizer)
> ```

| Name              | Type                | Description                                                                                                                                 |
| ----------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | `Iterable[Example]` | A batch of [`Example`](/api/example) objects to learn from.                                                                                 |
| _keyword-only_    |                     |                                                                                                                                             |
| `drop`            | float               | The dropout rate.                                                                                                                           |
| `set_annotations` | bool                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/morphologizer#set_annotations). |
| `sgd`             | `Optimizer`         | The [`Optimizer`](https://thinc.ai/docs/api-optimizers) object.                                                                             |
| `losses`          | `Dict[str, float]`  | Optional record of the loss during training. The value keyed by the model's name is updated.                                                |
| **RETURNS**       | `Dict[str, float]`  | The updated `losses` dictionary.                                                                                                            |

## Morphologizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> scores = morphologizer.predict([eg.predicted for eg in examples])
> loss, d_loss = morphologizer.get_loss(examples, scores)
> ```

| Name        | Type                | Description                                         |
| ----------- | ------------------- | --------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The batch of examples.                              |
| `scores`    | -                   | Scores representing the model's predictions.        |
| **RETURNS** | tuple               | The loss and the gradient, i.e. `(loss, gradient)`. |

## Morphologizer.begin_training {#begin_training tag="method"}

Initialize the pipe for training, using data examples if available. Return an
[`Optimizer`](https://thinc.ai/docs/api-optimizers) object.

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> nlp.pipeline.append(morphologizer)
> optimizer = morphologizer.begin_training(pipeline=nlp.pipeline)
> ```

| Name           | Type                    | Description                                                                                                                                                       |
| -------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Iterable[Example]`     | Optional gold-standard annotations in the form of [`Example`](/api/example) objects.                                                                              |
| `pipeline`     | `List[(str, callable)]` | Optional list of pipeline components that this component is part of.                                                                                              |
| `sgd`          | `Optimizer`             | An optional [`Optimizer`](https://thinc.ai/docs/api-optimizers) object. Will be created via [`create_optimizer`](/api/morphologizer#create_optimizer) if not set. |
| **RETURNS**    | `Optimizer`             | An optimizer.                                                                                                                                                     |

## Morphologizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> optimizer = morphologizer.create_optimizer()
> ```

| Name        | Type        | Description                                                     |
| ----------- | ----------- | --------------------------------------------------------------- |
| **RETURNS** | `Optimizer` | The [`Optimizer`](https://thinc.ai/docs/api-optimizers) object. |

## Morphologizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values.

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> with morphologizer.use_params():
>     morphologizer.to_disk("/best_model")
> ```

| Name     | Type | Description                                                                                                |
| -------- | ---- | ---------------------------------------------------------------------------------------------------------- |
| `params` | -    | The parameter values to use in the model. At the end of the context, the original parameters are restored. |

## Morphologizer.add_label {#add_label tag="method"}

Add a new label to the pipe. If the `Morphologizer` should set annotations for
both `pos` and `morph`, the label should include the UPOS as the feature `POS`.

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> morphologizer.add_label("Mood=Ind|POS=VERB|Tense=Past|VerbForm=Fin")
> ```

| Name    | Type | Description       |
| ------- | ---- | ----------------- |
| `label` | str  | The label to add. |

## Morphologizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> morphologizer.to_disk("/path/to/morphologizer")
> ```

| Name      | Type         | Description                                                                                                           |
| --------- | ------------ | --------------------------------------------------------------------------------------------------------------------- |
| `path`    | str / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| `exclude` | list         | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## Morphologizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> morphologizer.from_disk("/path/to/morphologizer")
> ```

| Name        | Type            | Description                                                                |
| ----------- | --------------- | -------------------------------------------------------------------------- |
| `path`      | str / `Path`    | A path to a directory. Paths may be either strings or `Path`-like objects. |
| `exclude`   | list            | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS** | `Morphologizer` | The modified `Morphologizer` object.                                       |

## Morphologizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> morphologizer = Morphologizer(nlp.vocab)
> morphologizer_bytes = morphologizer.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name        | Type  | Description                                                               |
| ----------- | ----- | ------------------------------------------------------------------------- |
| `exclude`   | list  | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS** | bytes | The serialized form of the `Morphologizer` object.                        |

## Morphologizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> morphologizer_bytes = morphologizer.to_bytes()
> morphologizer = Morphologizer(nlp.vocab)
> morphologizer.from_bytes(morphologizer_bytes)
> ```

| Name         | Type            | Description                                                               |
| ------------ | --------------- | ------------------------------------------------------------------------- |
| `bytes_data` | bytes           | The data to load from.                                                    |
| `exclude`    | list            | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**  | `Morphologizer` | The `Morphologizer` object.                                               |

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
