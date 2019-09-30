---
title: EntityRecognizer
tag: class
source: spacy/pipeline/pipes.pyx
---

This class is a subclass of `Pipe` and follows the same API. The pipeline
component is available in the [processing pipeline](/usage/processing-pipelines)
via the ID `"ner"`.

## EntityRecognizer.Model {#model tag="classmethod"}

Initialize a model for the pipe. The model should implement the
`thinc.neural.Model` API. Wrappers are under development for most major machine
learning libraries.

| Name        | Type   | Description                           |
| ----------- | ------ | ------------------------------------- |
| `**kwargs`  | -      | Parameters for initializing the model |
| **RETURNS** | object | The initialized model.                |

## EntityRecognizer.\_\_init\_\_ {#init tag="method"}

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.create_pipe`](/api/language#create_pipe).

> #### Example
>
> ```python
> # Construction via create_pipe
> ner = nlp.create_pipe("ner")
>
> # Construction from class
> from spacy.pipeline import EntityRecognizer
> ner = EntityRecognizer(nlp.vocab)
> ner.from_disk("/path/to/model")
> ```

| Name        | Type                          | Description                                                                                                                                           |
| ----------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`     | `Vocab`                       | The shared vocabulary.                                                                                                                                |
| `model`     | `thinc.neural.Model` / `True` | The model powering the pipeline component. If no model is supplied, the model is created when you call `begin_training`, `from_disk` or `from_bytes`. |
| `**cfg`     | -                             | Configuration parameters.                                                                                                                             |
| **RETURNS** | `EntityRecognizer`            | The newly constructed object.                                                                                                                         |

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
> doc = nlp(u"This is a sentence.")
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

| Name         | Type     | Description                                            |
| ------------ | -------- | ------------------------------------------------------ |
| `stream`     | iterable | A stream of documents.                                 |
| `batch_size` | int      | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**   | `Doc`    | Processed documents in the order of the original text. |

## EntityRecognizer.predict {#predict tag="method"}

Apply the pipeline's model to a batch of docs, without modifying them.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> scores = ner.predict([doc1, doc2])
> ```

| Name        | Type     | Description                                                                                                                                                                                                                        |
| ----------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs`      | iterable | The documents to predict.                                                                                                                                                                                                          |
| **RETURNS** | tuple    | A `(scores, tensors)` tuple where `scores` is the model's prediction for each document and `tensors` is the token representations used to predict the scores. Each tensor is an array with one row for each token in the document. |

## EntityRecognizer.set_annotations {#set_annotations tag="method"}

Modify a batch of documents, using pre-computed scores.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> scores = ner.predict([doc1, doc2])
> ner.set_annotations([doc1, doc2], scores)
> ```

| Name     | Type     | Description                                                |
| -------- | -------- | ---------------------------------------------------------- |
| `docs`   | iterable | The documents to modify.                                   |
| `scores` | -        | The scores to set, produced by `EntityRecognizer.predict`. |

## EntityRecognizer.update {#update tag="method"}

Learn from a batch of documents and gold-standard information, updating the
pipe's model. Delegates to [`predict`](/api/entityrecognizer#predict) and
[`get_loss`](/api/entityrecognizer#get_loss).

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> losses = {}
> optimizer = nlp.begin_training()
> ner.update([doc1, doc2], [gold1, gold2], losses=losses, sgd=optimizer)
> ```

| Name     | Type     | Description                                                                                  |
| -------- | -------- | -------------------------------------------------------------------------------------------- |
| `docs`   | iterable | A batch of documents to learn from.                                                          |
| `golds`  | iterable | The gold-standard data. Must have the same length as `docs`.                                 |
| `drop`   | float    | The dropout rate.                                                                            |
| `sgd`    | callable | The optimizer. Should take two arguments `weights` and `gradient`, and an optional ID.       |
| `losses` | dict     | Optional record of the loss during training. The value keyed by the model's name is updated. |

## EntityRecognizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> scores = ner.predict([doc1, doc2])
> loss, d_loss = ner.get_loss([doc1, doc2], [gold1, gold2], scores)
> ```

| Name        | Type     | Description                                                  |
| ----------- | -------- | ------------------------------------------------------------ |
| `docs`      | iterable | The batch of documents.                                      |
| `golds`     | iterable | The gold-standard data. Must have the same length as `docs`. |
| `scores`    | -        | Scores representing the model's predictions.                 |
| **RETURNS** | tuple    | The loss and the gradient, i.e. `(loss, gradient)`.          |

## EntityRecognizer.begin_training {#begin_training tag="method"}

Initialize the pipe for training, using data examples if available. If no model
has been initialized yet, the model is added.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> nlp.pipeline.append(ner)
> optimizer = ner.begin_training(pipeline=nlp.pipeline)
> ```

| Name          | Type     | Description                                                                                                                                                                                 |
| ------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gold_tuples` | iterable | Optional gold-standard annotations from which to construct [`GoldParse`](/api/goldparse) objects.                                                                                           |
| `pipeline`    | list     | Optional list of pipeline components that this component is part of.                                                                                                                        |
| `sgd`         | callable | An optional optimizer. Should take two arguments `weights` and `gradient`, and an optional ID. Will be created via [`EntityRecognizer`](/api/entityrecognizer#create_optimizer) if not set. |
| **RETURNS**   | callable | An optimizer.                                                                                                                                                                               |

## EntityRecognizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> optimizer = ner.create_optimizer()
> ```

| Name        | Type     | Description    |
| ----------- | -------- | -------------- |
| **RETURNS** | callable | The optimizer. |

## EntityRecognizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> with ner.use_params():
>     ner.to_disk("/best_model")
> ```

| Name     | Type | Description                                                                                                |
| -------- | ---- | ---------------------------------------------------------------------------------------------------------- |
| `params` | -    | The parameter values to use in the model. At the end of the context, the original parameters are restored. |

## EntityRecognizer.add_label {#add_label tag="method"}

Add a new label to the pipe.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> ner.add_label("MY_LABEL")
> ```

| Name    | Type    | Description       |
| ------- | ------- | ----------------- |
| `label` | unicode | The label to add. |

## EntityRecognizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> ner.to_disk("/path/to/ner")
> ```

| Name      | Type             | Description                                                                                                           |
| --------- | ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`    | unicode / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| `exclude` | list             | String names of [serialization fields](#serialization-fields) to exclude.                                             |

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
| `path`      | unicode / `Path`   | A path to a directory. Paths may be either strings or `Path`-like objects. |
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
