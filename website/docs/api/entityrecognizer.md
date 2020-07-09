---
title: EntityRecognizer
tag: class
source: spacy/pipeline/pipes.pyx
---

This class is a subclass of `Pipe` and follows the same API. The pipeline
component is available in the [processing pipeline](/usage/processing-pipelines)
via the ID `"ner"`.

## Default config {#config}

This is the default configuration used to initialize the model powering the
pipeline component. See the [model architectures](/api/architectures)
documentation for details on the architectures and their arguments and
hyperparameters. To learn more about how to customize the config and train
custom models, check out the [training config](/usage/training#config) docs.

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/defaults/ner_defaults.cfg
```

## EntityRecognizer.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via create_pipe
> ner = nlp.create_pipe("ner")
>
> # Construction via create_pipe with custom model
> config = {"model": {"@architectures": "my_ner"}}
> parser = nlp.create_pipe("ner", config)
>
> # Construction from class with custom model from file
> from spacy.pipeline import EntityRecognizer
> model = util.load_config("model.cfg", create_objects=True)["model"]
> ner = EntityRecognizer(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.create_pipe`](/api/language#create_pipe).

| Name        | Type               | Description                                                                     |
| ----------- | ------------------ | ------------------------------------------------------------------------------- |
| `vocab`     | `Vocab`            | The shared vocabulary.                                                          |
| `model`     | `Model`            | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. |
| `**cfg`     | -                  | Configuration parameters.                                                       |
| **RETURNS** | `EntityRecognizer` | The newly constructed object.                                                   |

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
> ner = EntityRecognizer(nlp.vocab)
> doc = nlp("This is a sentence.")
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
> ner = EntityRecognizer(nlp.vocab)
> for doc in ner.pipe(docs, batch_size=50):
>     pass
> ```

| Name         | Type            | Description                                            |
| ------------ | --------------- | ------------------------------------------------------ |
| `stream`     | `Iterable[Doc]` | A stream of documents.                                 |
| `batch_size` | int             | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**   | `Doc`           | Processed documents in the order of the original text. |

## EntityRecognizer.predict {#predict tag="method"}

Apply the pipeline's model to a batch of docs, without modifying them.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> scores = ner.predict([doc1, doc2])
> ```

| Name        | Type               | Description                                                                                                |
| ----------- | ------------------ | ---------------------------------------------------------------------------------------------------------- |
| `docs`      | `Iterable[Doc]`    | The documents to predict.                                                                                  |
| **RETURNS** | `List[StateClass]` | List of `syntax.StateClass` objects. `syntax.StateClass` is a helper class for the parse state (internal). |

## EntityRecognizer.set_annotations {#set_annotations tag="method"}

Modify a batch of documents, using pre-computed scores.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
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
> ner = EntityRecognizer(nlp.vocab, ner_model)
> optimizer = nlp.begin_training()
> losses = ner.update(examples, sgd=optimizer)
> ```

| Name              | Type                | Description                                                                                                                                    |
| ----------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | `Iterable[Example]` | A batch of [`Example`](/api/example) objects to learn from.                                                                                    |
| _keyword-only_    |                     |                                                                                                                                                |
| `drop`            | float               | The dropout rate.                                                                                                                              |
| `set_annotations` | bool                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/entityrecognizer#set_annotations). |
| `sgd`             | `Optimizer`         | The [`Optimizer`](https://thinc.ai/docs/api-optimizers) object.                                                                                |
| `losses`          | `Dict[str, float]`  | Optional record of the loss during training. The value keyed by the model's name is updated.                                                   |
| **RETURNS**       | `Dict[str, float]`  | The updated `losses` dictionary.                                                                                                               |

## EntityRecognizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> scores = ner.predict([eg.predicted for eg in examples])
> loss, d_loss = ner.get_loss(examples, scores)
> ```

| Name        | Type                | Description                                         |
| ----------- | ------------------- | --------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The batch of examples.                              |
| `scores`    | `List[StateClass]`  | Scores representing the model's predictions.        |
| **RETURNS** | tuple               | The loss and the gradient, i.e. `(loss, gradient)`. |

## EntityRecognizer.begin_training {#begin_training tag="method"}

Initialize the pipe for training, using data examples if available. Return an
[`Optimizer`](https://thinc.ai/docs/api-optimizers) object.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> nlp.pipeline.append(ner)
> optimizer = ner.begin_training(pipeline=nlp.pipeline)
> ```

| Name           | Type                    | Description                                                                                                                                                          |
| -------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Iterable[Example]`     | Optional gold-standard annotations in the form of [`Example`](/api/example) objects.                                                                                 |
| `pipeline`     | `List[(str, callable)]` | Optional list of pipeline components that this component is part of.                                                                                                 |
| `sgd`          | `Optimizer`             | An optional [`Optimizer`](https://thinc.ai/docs/api-optimizers) object. Will be created via [`create_optimizer`](/api/entityrecognizer#create_optimizer) if not set. |
| **RETURNS**    | `Optimizer`             | An optimizer.                                                                                                                                                        |

## EntityRecognizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> optimizer = ner.create_optimizer()
> ```

| Name        | Type        | Description                                                     |
| ----------- | ----------- | --------------------------------------------------------------- |
| **RETURNS** | `Optimizer` | The [`Optimizer`](https://thinc.ai/docs/api-optimizers) object. |

## EntityRecognizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> with ner.use_params(optimizer.averages):
>     ner.to_disk("/best_model")
> ```

| Name     | Type | Description                                                                                                |
| -------- | ---- | ---------------------------------------------------------------------------------------------------------- |
| `params` | dict | The parameter values to use in the model. At the end of the context, the original parameters are restored. |

## EntityRecognizer.add_label {#add_label tag="method"}

Add a new label to the pipe.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> ner.add_label("MY_LABEL")
> ```

| Name    | Type | Description       |
| ------- | ---- | ----------------- |
| `label` | str  | The label to add. |

## EntityRecognizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> ner.to_disk("/path/to/ner")
> ```

| Name      | Type         | Description                                                                                                           |
| --------- | ------------ | --------------------------------------------------------------------------------------------------------------------- |
| `path`    | str / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| `exclude` | list         | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## EntityRecognizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> ner.from_disk("/path/to/ner")
> ```

| Name        | Type               | Description                                                                |
| ----------- | ------------------ | -------------------------------------------------------------------------- |
| `path`      | str / `Path`       | A path to a directory. Paths may be either strings or `Path`-like objects. |
| `exclude`   | list               | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS** | `EntityRecognizer` | The modified `EntityRecognizer` object.                                    |

## EntityRecognizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> ner_bytes = ner.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name        | Type  | Description                                                               |
| ----------- | ----- | ------------------------------------------------------------------------- |
| `exclude`   | list  | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS** | bytes | The serialized form of the `EntityRecognizer` object.                     |

## EntityRecognizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ner_bytes = ner.to_bytes()
> ner = EntityRecognizer(nlp.vocab)
> ner.from_bytes(ner_bytes)
> ```

| Name         | Type               | Description                                                               |
| ------------ | ------------------ | ------------------------------------------------------------------------- |
| `bytes_data` | bytes              | The data to load from.                                                    |
| `exclude`    | list               | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**  | `EntityRecognizer` | The `EntityRecognizer` object.                                            |

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
