---
title: Pipe
tag: class
teaser: Base class for trainable pipeline components
---

This class is a base class and **not instantiated directly**. Trainable pipeline
components like the [`EntityRecognizer`](/api/entityrecognizer) or
[`TextCategorizer`](/api/textcategorizer) inherit from it and it defines the
interface that components should follow to function as trainable components in a
spaCy pipeline. See the docs on
[writing trainable components](/usage/processing-pipelines#trainable) for how to
use the `Pipe` base class to implement custom components.

> #### Why is Pipe implemented in Cython?
>
> The `Pipe` class is implemented in a `.pyx` module, the extension used by
> [Cython](/api/cython). This is needed so that **other** Cython classes, like
> the [`EntityRecognizer`](/api/entityrecognizer) can inherit from it. But it
> doesn't mean you have to implement trainable components in Cython – pure
> Python components like the [`TextCategorizer`](/api/textcategorizer) can also
> inherit from `Pipe`.

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/pipe.pyx
```

## Pipe.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> from spacy.pipeline import Pipe
> from spacy.language import Language
>
> class CustomPipe(Pipe):
>     ...
>
> @Language.factory("your_custom_pipe", default_config={"model": MODEL})
> def make_custom_pipe(nlp, name, model):
>     return CustomPipe(nlp.vocab, model, name)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#create_pipe).

<Infobox variant="danger">

This method needs to be overwritten with your own custom `__init__` method.

</Infobox>

| Name    | Type                                       | Description                                                                                 |
| ------- | ------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `vocab` | `Vocab`                                    | The shared vocabulary.                                                                      |
| `model` | [`Model`](https://thinc.ai/docs/api-model) | The Thinc [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.       |
| `name`  | str                                        | String name of the component instance. Used to add entries to the `losses` during training. |
| `**cfg` |                                            | Additional config parameters and settings.                                                  |

## Pipe.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/pipe#call) and [`pipe`](/api/pipe#pipe) delegate to the
[`predict`](/api/pipe#predict) and
[`set_annotations`](/api/pipe#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> pipe = nlp.add_pipe("your_custom_pipe")
> # This usually happens under the hood
> processed = pipe(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## Pipe.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/pipe#call) and
[`pipe`](/api/pipe#pipe) delegate to the [`predict`](/api/pipe#predict) and
[`set_annotations`](/api/pipe#set_annotations) methods.

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> for doc in pipe.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                           |
| -------------- | --------------- | ----------------------------------------------------- |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                |
| _keyword-only_ |                 |                                                       |
| `batch_size`   | int             | The number of documents to buffer. Defaults to `128`. |
| **YIELDS**     | `Doc`           | The processed documents in order.                     |

## Pipe.begin_training {#begin_training tag="method"}

Initialize the pipe for training, using data examples if available. Returns an
[`Optimizer`](https://thinc.ai/docs/api-optimizers) object.

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> optimizer = pipe.begin_training(pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                |
| -------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. |
| _keyword-only_ |                                                     |                                                                                                            |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                       |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/pipe#create_optimizer) if not set.    |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                             |

## Pipe.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

<Infobox variant="danger">

This method needs to be overwritten with your own custom `predict` method.

</Infobox>

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> scores = pipe.predict([doc1, doc2])
> ```

| Name        | Type            | Description                               |
| ----------- | --------------- | ----------------------------------------- |
| `docs`      | `Iterable[Doc]` | The documents to predict.                 |
| **RETURNS** | -               | The model's prediction for each document. |

## Pipe.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

<Infobox variant="danger">

This method needs to be overwritten with your own custom `set_annotations`
method.

</Infobox>

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> scores = pipe.predict(docs)
> pipe.set_annotations(docs, scores)
> ```

| Name     | Type            | Description                                    |
| -------- | --------------- | ---------------------------------------------- |
| `docs`   | `Iterable[Doc]` | The documents to modify.                       |
| `scores` | -               | The scores to set, produced by `Pipe.predict`. |

## Pipe.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects containing the
predictions and gold-standard annotations, and update the component's model.

<Infobox variant="danger">

This method needs to be overwritten with your own custom `update` method.

</Infobox>

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> optimizer = nlp.begin_training()
> losses = pipe.update(examples, sgd=optimizer)
> ```

| Name              | Type                                                | Description                                                                                                                        |
| ----------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects to learn from.                                                                        |
| _keyword-only_    |                                                     |                                                                                                                                    |
| `drop`            | float                                               | The dropout rate.                                                                                                                  |
| `set_annotations` | bool                                                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/pipe#set_annotations). |
| `sgd`             | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                                     |
| `losses`          | `Dict[str, float]`                                  | Optional record of the loss during training. Updated using the component name as the key.                                          |
| **RETURNS**       | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                                                                   |

## Pipe.rehearse {#rehearse tag="method,experimental"}

Perform a "rehearsal" update from a batch of data. Rehearsal updates teach the
current model to make predictions similar to an initial model, to try to address
the "catastrophic forgetting" problem. This feature is experimental.

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> optimizer = nlp.resume_training()
> losses = pipe.rehearse(examples, sgd=optimizer)
> ```

| Name           | Type                                                | Description                                                                               |
| -------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `examples`     | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects to learn from.                               |
| _keyword-only_ |                                                     |                                                                                           |
| `drop`         | float                                               | The dropout rate.                                                                         |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                            |
| `losses`       | `Dict[str, float]`                                  | Optional record of the loss during training. Updated using the component name as the key. |
| **RETURNS**    | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                          |

## Pipe.get_loss {#get_loss tag="method"}

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
| `scores`    |                       | Scores representing the model's predictions.        |
| **RETURNS** | `Tuple[float, float]` | The loss and the gradient, i.e. `(loss, gradient)`. |

## Pipe.score {#score tag="method" new="3"}

Score a batch of examples.

> #### Example
>
> ```python
> scores = pipe.score(examples)
> ```

| Name        | Type                | Description                                               |
| ----------- | ------------------- | --------------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The examples to score.                                    |
| **RETURNS** | `Dict[str, Any]`    | The scores, e.g. produced by the [`Scorer`](/api/scorer). |

## Pipe.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component. Defaults to
[`Adam`](https://thinc.ai/docs/api-optimizers#adam) with default settings.

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> optimizer = pipe.create_optimizer()
> ```

| Name        | Type                                                | Description    |
| ----------- | --------------------------------------------------- | -------------- |
| **RETURNS** | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer. |

## Pipe.add_label {#add_label tag="method"}

Add a new label to the pipe. It's possible to extend pretrained models with new
labels, but care should be taken to avoid the "catastrophic forgetting" problem.

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> pipe.add_label("MY_LABEL")
> ```

| Name        | Type | Description                                         |
| ----------- | ---- | --------------------------------------------------- |
| `label`     | str  | The label to add.                                   |
| **RETURNS** | int  | `0` if the label is already present, otherwise `1`. |

## Pipe.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> with pipe.use_params(optimizer.averages):
>     pipe.to_disk("/best_model")
> ```

| Name     | Type | Description                               |
| -------- | ---- | ----------------------------------------- |
| `params` | dict | The parameter values to use in the model. |

## Pipe.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> pipe.to_disk("/path/to/pipe")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## Pipe.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> pipe.from_disk("/path/to/pipe")
> ```

| Name           | Type            | Description                                                                |
| -------------- | --------------- | -------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                            |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `Pipe`          | The modified pipe.                                                         |

## Pipe.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> pipe = nlp.add_pipe("your_custom_pipe")
> pipe_bytes = pipe.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the pipe.                                          |

## Pipe.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> pipe_bytes = pipe.to_bytes()
> pipe = nlp.add_pipe("your_custom_pipe")
> pipe.from_bytes(pipe_bytes)
> ```

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| `bytes_data`   | bytes           | The data to load from.                                                    |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | `Pipe`          | The pipe.                                                                 |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = pipe.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
