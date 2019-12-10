---
title: EntityLinker
teaser:
  Functionality to disambiguate a named entity in text to a unique knowledge
  base identifier.
tag: class
source: spacy/pipeline/pipes.pyx
new: 2.2
---

This class is a subclass of `Pipe` and follows the same API. The pipeline
component is available in the [processing pipeline](/usage/processing-pipelines)
via the ID `"entity_linker"`.

## EntityLinker.Model {#model tag="classmethod"}

Initialize a model for the pipe. The model should implement the
`thinc.neural.Model` API, and should contain a field `tok2vec` that contains the
context encoder. Wrappers are under development for most major machine learning
libraries.

| Name        | Type   | Description                           |
| ----------- | ------ | ------------------------------------- |
| `**kwargs`  | -      | Parameters for initializing the model |
| **RETURNS** | object | The initialized model.                |

## EntityLinker.\_\_init\_\_ {#init tag="method"}

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.create_pipe`](/api/language#create_pipe).

> #### Example
>
> ```python
> # Construction via create_pipe
> entity_linker = nlp.create_pipe("entity_linker")
>
> # Construction from class
> from spacy.pipeline import EntityLinker
> entity_linker = EntityLinker(nlp.vocab)
> entity_linker.from_disk("/path/to/model")
> ```

| Name           | Type                          | Description                                                                                                                                           |
| -------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`        | `Vocab`                       | The shared vocabulary.                                                                                                                                |
| `model`        | `thinc.neural.Model` / `True` | The model powering the pipeline component. If no model is supplied, the model is created when you call `begin_training`, `from_disk` or `from_bytes`. |
| `hidden_width` | int                           | Width of the hidden layer of the entity linking model, defaults to `128`.                                                                             |
| `incl_prior`   | bool                          | Whether or not to include prior probabilities in the model. Defaults to `True`.                                                                       |
| `incl_context` | bool                          | Whether or not to include the local context in the model (if not: only prior probabilities are used). Defaults to `True`.                             |
| **RETURNS**    | `EntityLinker`                | The newly constructed object.                                                                                                                         |

## EntityLinker.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/entitylinker#call) and [`pipe`](/api/entitylinker#pipe)
delegate to the [`predict`](/api/entitylinker#predict) and
[`set_annotations`](/api/entitylinker#set_annotations) methods.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> doc = nlp("This is a sentence.")
> # This usually happens under the hood
> processed = entity_linker(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## EntityLinker.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/entitylinker#call) and
[`pipe`](/api/entitylinker#pipe) delegate to the
[`predict`](/api/entitylinker#predict) and
[`set_annotations`](/api/entitylinker#set_annotations) methods.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> for doc in entity_linker.pipe(docs, batch_size=50):
>     pass
> ```

| Name         | Type     | Description                                            |
| ------------ | -------- | ------------------------------------------------------ |
| `stream`     | iterable | A stream of documents.                                 |
| `batch_size` | int      | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**   | `Doc`    | Processed documents in the order of the original text. |

## EntityLinker.predict {#predict tag="method"}

Apply the pipeline's model to a batch of docs, without modifying them.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> kb_ids, tensors = entity_linker.predict([doc1, doc2])
> ```

| Name        | Type     | Description                                                                                                                                                                                        |
| ----------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs`      | iterable | The documents to predict.                                                                                                                                                                          |
| **RETURNS** | tuple    | A `(kb_ids, tensors)` tuple where `kb_ids` are the model's predicted KB identifiers for the entities in the `docs`, and `tensors` are the token representations used to predict these identifiers. |

## EntityLinker.set_annotations {#set_annotations tag="method"}

Modify a batch of documents, using pre-computed entity IDs for a list of named
entities.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> kb_ids, tensors = entity_linker.predict([doc1, doc2])
> entity_linker.set_annotations([doc1, doc2], kb_ids, tensors)
> ```

| Name      | Type     | Description                                                                                       |
| --------- | -------- | ------------------------------------------------------------------------------------------------- |
| `docs`    | iterable | The documents to modify.                                                                          |
| `kb_ids`  | iterable | The knowledge base identifiers for the entities in the docs, predicted by `EntityLinker.predict`. |
| `tensors` | iterable | The token representations used to predict the identifiers.                                        |

## EntityLinker.update {#update tag="method"}

Learn from a batch of documents and gold-standard information, updating both the
pipe's entity linking model and context encoder. Delegates to
[`predict`](/api/entitylinker#predict) and
[`get_loss`](/api/entitylinker#get_loss).

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> losses = {}
> optimizer = nlp.begin_training()
> entity_linker.update([doc1, doc2], [gold1, gold2], losses=losses, sgd=optimizer)
> ```

| Name     | Type     | Description                                                                                             |
| -------- | -------- | ------------------------------------------------------------------------------------------------------- |
| `docs`   | iterable | A batch of documents to learn from.                                                                     |
| `golds`  | iterable | The gold-standard data. Must have the same length as `docs`.                                            |
| `drop`   | float    | The dropout rate, used both for the EL model and the context encoder.                                   |
| `sgd`    | callable | The optimizer for the EL model. Should take two arguments `weights` and `gradient`, and an optional ID. |
| `losses` | dict     | Optional record of the loss during training. The value keyed by the model's name is updated.            |

## EntityLinker.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the entities in a batch of documents and
their predicted scores.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> kb_ids, tensors = entity_linker.predict(docs)
> loss, d_loss = entity_linker.get_loss(docs, [gold1, gold2], kb_ids, tensors)
> ```

| Name        | Type     | Description                                                  |
| ----------- | -------- | ------------------------------------------------------------ |
| `docs`      | iterable | The batch of documents.                                      |
| `golds`     | iterable | The gold-standard data. Must have the same length as `docs`. |
| `kb_ids`    | iterable | KB identifiers representing the model's predictions.         |
| `tensors`   | iterable | The token representations used to predict the identifiers    |
| **RETURNS** | tuple    | The loss and the gradient, i.e. `(loss, gradient)`.          |

## EntityLinker.set_kb {#set_kb tag="method"}

Define the knowledge base (KB) used for disambiguating named entities to KB
identifiers.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> entity_linker.set_kb(kb)
> ```

| Name | Type            | Description                     |
| ---- | --------------- | ------------------------------- |
| `kb` | `KnowledgeBase` | The [`KnowledgeBase`](/api/kb). |

## EntityLinker.begin_training {#begin_training tag="method"}

Initialize the pipe for training, using data examples if available. If no model
has been initialized yet, the model is added. Before calling this method, a
knowledge base should have been defined with
[`set_kb`](/api/entitylinker#set_kb).

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> entity_linker.set_kb(kb)
> nlp.add_pipe(entity_linker, last=True)
> optimizer = entity_linker.begin_training(pipeline=nlp.pipeline)
> ```

| Name          | Type     | Description                                                                                                                                                                         |
| ------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gold_tuples` | iterable | Optional gold-standard annotations from which to construct [`GoldParse`](/api/goldparse) objects.                                                                                   |
| `pipeline`    | list     | Optional list of pipeline components that this component is part of.                                                                                                                |
| `sgd`         | callable | An optional optimizer. Should take two arguments `weights` and `gradient`, and an optional ID. Will be created via [`EntityLinker`](/api/entitylinker#create_optimizer) if not set. |
| **RETURNS**   | callable | An optimizer.                                                                                                                                                                       |

## EntityLinker.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> optimizer = entity_linker.create_optimizer()
> ```

| Name        | Type     | Description    |
| ----------- | -------- | -------------- |
| **RETURNS** | callable | The optimizer. |

## EntityLinker.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's EL model, to use the given parameter values.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> with entity_linker.use_params(optimizer.averages):
>     entity_linker.to_disk("/best_model")
> ```

| Name     | Type | Description                                                                                                |
| -------- | ---- | ---------------------------------------------------------------------------------------------------------- |
| `params` | dict | The parameter values to use in the model. At the end of the context, the original parameters are restored. |

## EntityLinker.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> entity_linker.to_disk("/path/to/entity_linker")
> ```

| Name      | Type             | Description                                                                                                           |
| --------- | ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`    | unicode / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| `exclude` | list             | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## EntityLinker.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> entity_linker = EntityLinker(nlp.vocab)
> entity_linker.from_disk("/path/to/entity_linker")
> ```

| Name        | Type             | Description                                                                |
| ----------- | ---------------- | -------------------------------------------------------------------------- |
| `path`      | unicode / `Path` | A path to a directory. Paths may be either strings or `Path`-like objects. |
| `exclude`   | list             | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS** | `EntityLinker`   | The modified `EntityLinker` object.                                        |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = entity_linker.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
| `kb`    | The knowledge base. You usually don't want to exclude this.    |
