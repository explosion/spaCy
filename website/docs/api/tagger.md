---
title: Tagger
tag: class
source: spacy/pipeline/tagger.pyx
---

This class is a subclass of `Pipe` and follows the same API. The pipeline
component is available in the [processing pipeline](/usage/processing-pipelines)
via the ID `"tagger"`.

## Tagger.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> tagger = nlp.add_pipe("tagger")
>
> # Construction via create_pipe with custom model
> config = {"model": {"@architectures": "my_tagger"}}
> parser = nlp.add_pipe("tagger", config)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

| Name        | Type     | Description                                                                     |
| ----------- | -------- | ------------------------------------------------------------------------------- |
| `vocab`     | `Vocab`  | The shared vocabulary.                                                          |
| `model`     | `Model`  | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. |
| `**cfg`     | -        | Configuration parameters.                                                       |
| **RETURNS** | `Tagger` | The newly constructed object.                                                   |

## Tagger.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/tagger#call) and [`pipe`](/api/tagger#pipe) delegate to the
[`predict`](/api/tagger#predict) and
[`set_annotations`](/api/tagger#set_annotations) methods.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> doc = nlp("This is a sentence.")
> # This usually happens under the hood
> processed = tagger(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## Tagger.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/tagger#call) and
[`pipe`](/api/tagger#pipe) delegate to the [`predict`](/api/tagger#predict) and
[`set_annotations`](/api/tagger#set_annotations) methods.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> for doc in tagger.pipe(docs, batch_size=50):
>     pass
> ```

| Name         | Type            | Description                                            |
| ------------ | --------------- | ------------------------------------------------------ |
| `stream`     | `Iterable[Doc]` | A stream of documents.                                 |
| `batch_size` | int             | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**   | `Doc`           | Processed documents in the order of the original text. |

## Tagger.predict {#predict tag="method"}

Apply the pipeline's model to a batch of docs, without modifying them.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> scores = tagger.predict([doc1, doc2])
> ```

| Name        | Type            | Description                               |
| ----------- | --------------- | ----------------------------------------- |
| `docs`      | `Iterable[Doc]` | The documents to predict.                 |
| **RETURNS** | -               | The model's prediction for each document. |

## Tagger.set_annotations {#set_annotations tag="method"}

Modify a batch of documents, using pre-computed scores.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> scores = tagger.predict([doc1, doc2])
> tagger.set_annotations([doc1, doc2], scores)
> ```

| Name     | Type            | Description                                      |
| -------- | --------------- | ------------------------------------------------ |
| `docs`   | `Iterable[Doc]` | The documents to modify.                         |
| `scores` | -               | The scores to set, produced by `Tagger.predict`. |

## Tagger.update {#update tag="method"}

Learn from a batch of documents and gold-standard information, updating the
pipe's model. Delegates to [`predict`](/api/tagger#predict) and
[`get_loss`](/api/tagger#get_loss).

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab, tagger_model)
> optimizer = nlp.begin_training()
> losses = tagger.update(examples, sgd=optimizer)
> ```

| Name              | Type                | Description                                                                                                                          |
| ----------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `examples`        | `Iterable[Example]` | A batch of [`Example`](/api/example) objects to learn from.                                                                          |
| _keyword-only_    |                     |                                                                                                                                      |
| `drop`            | float               | The dropout rate.                                                                                                                    |
| `set_annotations` | bool                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/tagger#set_annotations). |
| `sgd`             | `Optimizer`         | The [`Optimizer`](https://thinc.ai/docs/api-optimizers) object.                                                                      |
| `losses`          | `Dict[str, float]`  | Optional record of the loss during training. The value keyed by the model's name is updated.                                         |
| **RETURNS**       | `Dict[str, float]`  | The updated `losses` dictionary.                                                                                                     |

## Tagger.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> scores = tagger.predict([eg.predicted for eg in examples])
> loss, d_loss = tagger.get_loss(examples, scores)
> ```

| Name        | Type                | Description                                         |
| ----------- | ------------------- | --------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The batch of examples.                              |
| `scores`    | -                   | Scores representing the model's predictions.        |
| **RETURNS** | tuple               | The loss and the gradient, i.e. `(loss, gradient)`. |

## Tagger.begin_training {#begin_training tag="method"}

Initialize the pipe for training, using data examples if available. Return an
[`Optimizer`](https://thinc.ai/docs/api-optimizers) object.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> nlp.pipeline.append(tagger)
> optimizer = tagger.begin_training(pipeline=nlp.pipeline)
> ```

| Name           | Type                    | Description                                                                                                                                                |
| -------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Iterable[Example]`     | Optional gold-standard annotations in the form of [`Example`](/api/example) objects.                                                                       |
| `pipeline`     | `List[(str, callable)]` | Optional list of pipeline components that this component is part of.                                                                                       |
| `sgd`          | `Optimizer`             | An optional [`Optimizer`](https://thinc.ai/docs/api-optimizers) object. Will be created via [`create_optimizer`](/api/tagger#create_optimizer) if not set. |
| **RETURNS**    | `Optimizer`             | An optimizer.                                                                                                                                              |

## Tagger.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> optimizer = tagger.create_optimizer()
> ```

| Name        | Type        | Description                                                     |
| ----------- | ----------- | --------------------------------------------------------------- |
| **RETURNS** | `Optimizer` | The [`Optimizer`](https://thinc.ai/docs/api-optimizers) object. |

## Tagger.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> with tagger.use_params():
>     tagger.to_disk("/best_model")
> ```

| Name     | Type | Description                                                                                                |
| -------- | ---- | ---------------------------------------------------------------------------------------------------------- |
| `params` | -    | The parameter values to use in the model. At the end of the context, the original parameters are restored. |

## Tagger.add_label {#add_label tag="method"}

Add a new label to the pipe.

> #### Example
>
> ```python
> from spacy.symbols import POS
> tagger = Tagger(nlp.vocab)
> tagger.add_label("MY_LABEL", {POS: 'NOUN'})
> ```

| Name     | Type | Description                                                     |
| -------- | ---- | --------------------------------------------------------------- |
| `label`  | str  | The label to add.                                               |
| `values` | dict | Optional values to map to the label, e.g. a tag map dictionary. |

## Tagger.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> tagger.to_disk("/path/to/tagger")
> ```

| Name      | Type         | Description                                                                                                           |
| --------- | ------------ | --------------------------------------------------------------------------------------------------------------------- |
| `path`    | str / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| `exclude` | list         | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## Tagger.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> tagger.from_disk("/path/to/tagger")
> ```

| Name        | Type         | Description                                                                |
| ----------- | ------------ | -------------------------------------------------------------------------- |
| `path`      | str / `Path` | A path to a directory. Paths may be either strings or `Path`-like objects. |
| `exclude`   | list         | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS** | `Tagger`     | The modified `Tagger` object.                                              |

## Tagger.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> tagger = Tagger(nlp.vocab)
> tagger_bytes = tagger.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name        | Type  | Description                                                               |
| ----------- | ----- | ------------------------------------------------------------------------- |
| `exclude`   | list  | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS** | bytes | The serialized form of the `Tagger` object.                               |

## Tagger.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> tagger_bytes = tagger.to_bytes()
> tagger = Tagger(nlp.vocab)
> tagger.from_bytes(tagger_bytes)
> ```

| Name         | Type     | Description                                                               |
| ------------ | -------- | ------------------------------------------------------------------------- |
| `bytes_data` | bytes    | The data to load from.                                                    |
| `exclude`    | list     | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**  | `Tagger` | The `Tagger` object.                                                      |

## Tagger.labels {#labels tag="property"}

The labels currently added to the component. Note that even for a blank
component, this will always include the built-in coarse-grained part-of-speech
tags by default, e.g. `VERB`, `NOUN` and so on.

> #### Example
>
> ```python
> tagger.add_label("MY_LABEL")
> assert "MY_LABEL" in tagger.labels
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
> data = tagger.to_disk("/path", exclude=["vocab"])
> ```

| Name      | Description                                                                                |
| --------- | ------------------------------------------------------------------------------------------ |
| `vocab`   | The shared [`Vocab`](/api/vocab).                                                          |
| `cfg`     | The config file. You usually don't want to exclude this.                                   |
| `model`   | The binary model data. You usually don't want to exclude this.                             |
| `tag_map` | The [tag map](/usage/adding-languages#tag-map) mapping fine-grained to coarse-grained tag. |
