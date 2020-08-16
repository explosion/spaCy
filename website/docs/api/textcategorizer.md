---
title: TextCategorizer
tag: class
source: spacy/pipeline/textcat.py
new: 2
teaser: 'Pipeline component for text classification'
api_base_class: /api/pipe
api_string_name: textcat
api_trainable: true
---

The text categorizer predicts **categories over a whole document**. It can learn
one or more labels, and the labels can be mutually exclusive (i.e. one true
label per document) or non-mutually exclusive (i.e. zero or more labels may be
true per document). The multi-label setting is controlled by the model instance
that's provided.

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
> from spacy.pipeline.textcat import DEFAULT_TEXTCAT_MODEL
> config = {
>    "labels": [],
>    "model": DEFAULT_TEXTCAT_MODEL,
> }
> nlp.add_pipe("textcat", config=config)
> ```

| Setting  | Type                                       | Description                                                                             | Default                                               |
| -------- | ------------------------------------------ | --------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `labels` | `List[str]`                                | A list of categories to learn. If empty, the model infers the categories from the data. | `[]`                                                  |
| `model`  | [`Model`](https://thinc.ai/docs/api-model) | A model instance that predicts scores for each category.                                | [TextCatEnsemble](/api/architectures#TextCatEnsemble) |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/textcat.py
```

## TextCategorizer.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> textcat = nlp.add_pipe("textcat")
>
> # Construction via add_pipe with custom model
> config = {"model": {"@architectures": "my_textcat"}}
> parser = nlp.add_pipe("textcat", config=config)
>
> # Construction from class
> from spacy.pipeline import TextCategorizer
> textcat = TextCategorizer(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#create_pipe).

| Name           | Type                                       | Description                                                                                 |
| -------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `vocab`        | `Vocab`                                    | The shared vocabulary.                                                                      |
| `model`        | [`Model`](https://thinc.ai/docs/api-model) | The Thinc [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.       |
| `name`         | str                                        | String name of the component instance. Used to add entries to the `losses` during training. |
| _keyword-only_ |                                            |                                                                                             |
| `labels`       | `Iterable[str]`                            | The labels to use.                                                                          |

## TextCategorizer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/textcategorizer#call) and [`pipe`](/api/textcategorizer#pipe)
delegate to the [`predict`](/api/textcategorizer#predict) and
[`set_annotations`](/api/textcategorizer#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> textcat = nlp.add_pipe("textcat")
> # This usually happens under the hood
> processed = textcat(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## TextCategorizer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/textcategorizer#call) and
[`pipe`](/api/textcategorizer#pipe) delegate to the
[`predict`](/api/textcategorizer#predict) and
[`set_annotations`](/api/textcategorizer#set_annotations) methods.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> for doc in textcat.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                           |
| -------------- | --------------- | ----------------------------------------------------- |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                |
| _keyword-only_ |                 |                                                       |
| `batch_size`   | int             | The number of documents to buffer. Defaults to `128`. |
| **YIELDS**     | `Doc`           | The processed documents in order.                     |

## TextCategorizer.begin_training {#begin_training tag="method"}

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
> textcat = nlp.add_pipe("textcat")
> optimizer = textcat.begin_training(lambda: [], pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                        |
| -------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects.         |
| _keyword-only_ |                                                     |                                                                                                                    |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                               |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/textcategorizer#create_optimizer) if not set. |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                     |

## TextCategorizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> scores = textcat.predict([doc1, doc2])
> ```

| Name        | Type            | Description                               |
| ----------- | --------------- | ----------------------------------------- |
| `docs`      | `Iterable[Doc]` | The documents to predict.                 |
| **RETURNS** | -               | The model's prediction for each document. |

## TextCategorizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> scores = textcat.predict(docs)
> textcat.set_annotations(docs, scores)
> ```

| Name     | Type            | Description                                               |
| -------- | --------------- | --------------------------------------------------------- |
| `docs`   | `Iterable[Doc]` | The documents to modify.                                  |
| `scores` | -               | The scores to set, produced by `TextCategorizer.predict`. |

## TextCategorizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects containing the
predictions and gold-standard annotations, and update the component's model.
Delegates to [`predict`](/api/textcategorizer#predict) and
[`get_loss`](/api/textcategorizer#get_loss).

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> optimizer = nlp.begin_training()
> losses = textcat.update(examples, sgd=optimizer)
> ```

| Name              | Type                                                | Description                                                                                                                                   |
| ----------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects to learn from.                                                                                   |
| _keyword-only_    |                                                     |                                                                                                                                               |
| `drop`            | float                                               | The dropout rate.                                                                                                                             |
| `set_annotations` | bool                                                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/textcategorizer#set_annotations). |
| `sgd`             | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                                                |
| `losses`          | `Dict[str, float]`                                  | Optional record of the loss during training. Updated using the component name as the key.                                                     |
| **RETURNS**       | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                                                                              |

## TextCategorizer.rehearse {#rehearse tag="method,experimental" new="3"}

Perform a "rehearsal" update from a batch of data. Rehearsal updates teach the
current model to make predictions similar to an initial model, to try to address
the "catastrophic forgetting" problem. This feature is experimental.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> optimizer = nlp.resume_training()
> losses = textcat.rehearse(examples, sgd=optimizer)
> ```

| Name           | Type                                                | Description                                                                               |
| -------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `examples`     | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects to learn from.                               |
| _keyword-only_ |                                                     |                                                                                           |
| `drop`         | float                                               | The dropout rate.                                                                         |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                            |
| `losses`       | `Dict[str, float]`                                  | Optional record of the loss during training. Updated using the component name as the key. |
| **RETURNS**    | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                          |

## TextCategorizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> scores = textcat.predict([eg.predicted for eg in examples])
> loss, d_loss = textcat.get_loss(examples, scores)
> ```

| Name        | Type                  | Description                                         |
| ----------- | --------------------- | --------------------------------------------------- |
| `examples`  | `Iterable[Example]`   | The batch of examples.                              |
| `scores`    | -                     | Scores representing the model's predictions.        |
| **RETURNS** | `Tuple[float, float]` | The loss and the gradient, i.e. `(loss, gradient)`. |

## TextCategorizer.score {#score tag="method" new="3"}

Score a batch of examples.

> #### Example
>
> ```python
> scores = textcat.score(examples)
> ```

| Name             | Type                | Description                                                            |
| ---------------- | ------------------- | ---------------------------------------------------------------------- |
| `examples`       | `Iterable[Example]` | The examples to score.                                                 |
| _keyword-only_   |                     |                                                                        |
| `positive_label` | str                 | Optional positive label.                                               |
| **RETURNS**      | `Dict[str, Any]`    | The scores, produced by [`Scorer.score_cats`](/api/scorer#score_cats). |

## TextCategorizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> optimizer = textcat.create_optimizer()
> ```

| Name        | Type                                                | Description    |
| ----------- | --------------------------------------------------- | -------------- |
| **RETURNS** | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer. |

## TextCategorizer.add_label {#add_label tag="method"}

Add a new label to the pipe.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> textcat.add_label("MY_LABEL")
> ```

| Name        | Type | Description                                         |
| ----------- | ---- | --------------------------------------------------- |
| `label`     | str  | The label to add.                                   |
| **RETURNS** | int  | `0` if the label is already present, otherwise `1`. |

## TextCategorizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> with textcat.use_params(optimizer.averages):
>     textcat.to_disk("/best_model")
> ```

| Name     | Type | Description                               |
| -------- | ---- | ----------------------------------------- |
| `params` | dict | The parameter values to use in the model. |

## TextCategorizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> textcat.to_disk("/path/to/textcat")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## TextCategorizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> textcat.from_disk("/path/to/textcat")
> ```

| Name           | Type              | Description                                                                |
| -------------- | ----------------- | -------------------------------------------------------------------------- |
| `path`         | str / `Path`      | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                   |                                                                            |
| `exclude`      | `Iterable[str]`   | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `TextCategorizer` | The modified `TextCategorizer` object.                                     |

## TextCategorizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> textcat_bytes = textcat.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the `TextCategorizer` object.                      |

## TextCategorizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> textcat_bytes = textcat.to_bytes()
> textcat = nlp.add_pipe("textcat")
> textcat.from_bytes(textcat_bytes)
> ```

| Name           | Type              | Description                                                               |
| -------------- | ----------------- | ------------------------------------------------------------------------- |
| `bytes_data`   | bytes             | The data to load from.                                                    |
| _keyword-only_ |                   |                                                                           |
| `exclude`      | `Iterable[str]`   | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | `TextCategorizer` | The `TextCategorizer` object.                                             |

## TextCategorizer.labels {#labels tag="property"}

The labels currently added to the component.

> #### Example
>
> ```python
> textcat.add_label("MY_LABEL")
> assert "MY_LABEL" in textcat.labels
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
> data = textcat.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
