---
title: SentenceRecognizer
tag: class
source: spacy/pipeline/senter.pyx
new: 3
teaser: 'Pipeline component for sentence segmentation'
api_base_class: /api/tagger
api_string_name: senter
api_trainable: true
---

A trainable pipeline component for sentence segmentation. For a simpler,
ruse-based strategy, see the [`Sentencizer`](/api/sentencizer).

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
> from spacy.pipeline.senter import DEFAULT_SENTER_MODEL
> config = {"model": DEFAULT_SENTER_MODEL,}
> nlp.add_pipe("senter", config=config)
> ```

| Setting | Type                                       | Description       | Default                             |
| ------- | ------------------------------------------ | ----------------- | ----------------------------------- |
| `model` | [`Model`](https://thinc.ai/docs/api-model) | The model to use. | [Tagger](/api/architectures#Tagger) |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/senter.pyx
```

## SentenceRecognizer.\_\_init\_\_ {#init tag="method"}

Initialize the sentence recognizer.

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> senter = nlp.add_pipe("senter")
>
> # Construction via create_pipe with custom model
> config = {"model": {"@architectures": "my_senter"}}
> senter = nlp.add_pipe("senter", config=config)
>
> # Construction from class
> from spacy.pipeline import SentenceRecognizer
> senter = SentenceRecognizer(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

| Name    | Type    | Description                                                                                 |
| ------- | ------- | ------------------------------------------------------------------------------------------- |
| `vocab` | `Vocab` | The shared vocabulary.                                                                      |
| `model` | `Model` | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.             |
| `name`  | str     | String name of the component instance. Used to add entries to the `losses` during training. |

## SentenceRecognizer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/sentencerecognizer#call) and
[`pipe`](/api/sentencerecognizer#pipe) delegate to the
[`predict`](/api/sentencerecognizer#predict) and
[`set_annotations`](/api/sentencerecognizer#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> senter = nlp.add_pipe("senter")
> # This usually happens under the hood
> processed = senter(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## SentenceRecognizer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/sentencerecognizer#call)
and [`pipe`](/api/sentencerecognizer#pipe) delegate to the
[`predict`](/api/sentencerecognizer#predict) and
[`set_annotations`](/api/sentencerecognizer#set_annotations) methods.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> for doc in senter.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                            |
| -------------- | --------------- | ------------------------------------------------------ |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                 |
| _keyword-only_ |                 |                                                        |
| `batch_size`   | int             | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**     | `Doc`           | Processed documents in the order of the original text. |

## SentenceRecognizer.begin_training {#begin_training tag="method"}

Initialize the pipe for training, using data examples if available. Returns an
[`Optimizer`](https://thinc.ai/docs/api-optimizers) object.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> optimizer = senter.begin_training(pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                           |
| -------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects.            |
| _keyword-only_ |                                                     |                                                                                                                       |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                                  |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/sentencerecognizer#create_optimizer) if not set. |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                        |

## SentenceRecognizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> scores = senter.predict([doc1, doc2])
> ```

| Name        | Type            | Description                               |
| ----------- | --------------- | ----------------------------------------- |
| `docs`      | `Iterable[Doc]` | The documents to predict.                 |
| **RETURNS** | -               | The model's prediction for each document. |

## SentenceRecognizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> scores = senter.predict([doc1, doc2])
> senter.set_annotations([doc1, doc2], scores)
> ```

| Name     | Type            | Description                                                  |
| -------- | --------------- | ------------------------------------------------------------ |
| `docs`   | `Iterable[Doc]` | The documents to modify.                                     |
| `scores` | -               | The scores to set, produced by `SentenceRecognizer.predict`. |

## SentenceRecognizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects containing the
predictions and gold-standard annotations, and update the component's model.
Delegates to [`predict`](/api/sentencerecognizer#predict) and
[`get_loss`](/api/sentencerecognizer#get_loss).

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> optimizer = nlp.begin_training()
> losses = senter.update(examples, sgd=optimizer)
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

## SentenceRecognizer.rehearse {#rehearse tag="method,experimental"}

Perform a "rehearsal" update from a batch of data. Rehearsal updates teach the
current model to make predictions similar to an initial model, to try to address
the "catastrophic forgetting" problem. This feature is experimental.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> optimizer = nlp.resume_training()
> losses = senter.rehearse(examples, sgd=optimizer)
> ```

| Name           | Type                                                | Description                                                                               |
| -------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `examples`     | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects to learn from.                               |
| _keyword-only_ |                                                     |                                                                                           |
| `drop`         | float                                               | The dropout rate.                                                                         |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                            |
| `losses`       | `Dict[str, float]`                                  | Optional record of the loss during training. Updated using the component name as the key. |
| **RETURNS**    | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                          |

## SentenceRecognizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> scores = senter.predict([eg.predicted for eg in examples])
> loss, d_loss = senter.get_loss(examples, scores)
> ```

| Name        | Type                  | Description                                         |
| ----------- | --------------------- | --------------------------------------------------- |
| `examples`  | `Iterable[Example]`   | The batch of examples.                              |
| `scores`    | -                     | Scores representing the model's predictions.        |
| **RETURNS** | `Tuple[float, float]` | The loss and the gradient, i.e. `(loss, gradient)`. |

## SentenceRecognizer.score {#score tag="method" new="3"}

Score a batch of examples.

> #### Example
>
> ```python
> scores = senter.score(examples)
> ```

| Name        | Type                | Description                                                              |
| ----------- | ------------------- | ------------------------------------------------------------------------ |
| `examples`  | `Iterable[Example]` | The examples to score.                                                   |
| **RETURNS** | `Dict[str, Any]`    | The scores, produced by [`Scorer.score_spans`](/api/scorer#score_spans). |

## SentenceRecognizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> optimizer = senter.create_optimizer()
> ```

| Name        | Type                                                | Description    |
| ----------- | --------------------------------------------------- | -------------- |
| **RETURNS** | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer. |

## SentenceRecognizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> with senter.use_params(optimizer.averages):
>     senter.to_disk("/best_model")
> ```

| Name     | Type | Description                               |
| -------- | ---- | ----------------------------------------- |
| `params` | dict | The parameter values to use in the model. |

## SentenceRecognizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> senter.to_disk("/path/to/senter")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## SentenceRecognizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> senter.from_disk("/path/to/senter")
> ```

| Name           | Type                 | Description                                                                |
| -------------- | -------------------- | -------------------------------------------------------------------------- |
| `path`         | str / `Path`         | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                      |                                                                            |
| `exclude`      | `Iterable[str]`      | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `SentenceRecognizer` | The modified `SentenceRecognizer` object.                                  |

## SentenceRecognizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> senter = nlp.add_pipe("senter")
> senter_bytes = senter.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the `SentenceRecognizer` object.                   |

## SentenceRecognizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> senter_bytes = senter.to_bytes()
> senter = nlp.add_pipe("senter")
> senter.from_bytes(senter_bytes)
> ```

| Name           | Type                 | Description                                                               |
| -------------- | -------------------- | ------------------------------------------------------------------------- |
| `bytes_data`   | bytes                | The data to load from.                                                    |
| _keyword-only_ |                      |                                                                           |
| `exclude`      | `Iterable[str]`      | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | `SentenceRecognizer` | The `SentenceRecognizer` object.                                          |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = senter.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
