---
title: DependencyParser
tag: class
source: spacy/pipeline/dep_parser.pyx
teaser: 'Pipeline component for syntactic dependency parsing'
api_base_class: /api/pipe
api_string_name: parser
api_trainable: true
---

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
> from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL
> config = {
>    "moves": None,
>   # TODO: rest
>    "model": DEFAULT_PARSER_MODEL,
> }
> nlp.add_pipe("parser", config=config)
> ```

| Setting | Type                                       | Description       | Default                                                           |
| ------- | ------------------------------------------ | ----------------- | ----------------------------------------------------------------- |
| `moves` | list                                       | <!-- TODO: -->    | `None`                                                            |
| `model` | [`Model`](https://thinc.ai/docs/api-model) | The model to use. | [TransitionBasedParser](/api/architectures#TransitionBasedParser) |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/dep_parser.pyx
```

## DependencyParser.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> parser = nlp.add_pipe("parser")
>
> # Construction via add_pipe with custom model
> config = {"model": {"@architectures": "my_parser"}}
> parser = nlp.add_pipe("parser", config=config)
>
> # Construction from class
> from spacy.pipeline import DependencyParser
> parser = DependencyParser(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

| Name                          | Type                                       | Description                                                                                 |
| ----------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `vocab`                       | `Vocab`                                    | The shared vocabulary.                                                                      |
| `model`                       | [`Model`](https://thinc.ai/docs/api-model) | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.             |
| `name`                        | str                                        | String name of the component instance. Used to add entries to the `losses` during training. |
| `moves`                       | list                                       | <!-- TODO: -->                                                                              |
| _keyword-only_                |                                            |                                                                                             |
| `update_with_oracle_cut_size` | int                                        | <!-- TODO: -->                                                                              |
| `multitasks`                  | `Iterable`                                 | <!-- TODO: -->                                                                              |
| `learn_tokens`                | bool                                       | <!-- TODO: -->                                                                              |
| `min_action_freq`             | int                                        | <!-- TODO: -->                                                                              |

## DependencyParser.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/dependencyparser#call) and
[`pipe`](/api/dependencyparser#pipe) delegate to the
[`predict`](/api/dependencyparser#predict) and
[`set_annotations`](/api/dependencyparser#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> parser = nlp.add_pipe("parser")
> # This usually happens under the hood
> processed = parser(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## DependencyParser.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/dependencyparser#call) and
[`pipe`](/api/dependencyparser#pipe) delegate to the
[`predict`](/api/dependencyparser#predict) and
[`set_annotations`](/api/dependencyparser#set_annotations) methods.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> for doc in parser.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                            |
| -------------- | --------------- | ------------------------------------------------------ |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                 |
| _keyword-only_ |                 |                                                        |
| `batch_size`   | int             | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**     | `Doc`           | Processed documents in the order of the original text. |

## DependencyParser.begin_training {#begin_training tag="method"}

Initialize the pipe for training, using data examples if available. Return an
[`Optimizer`](https://thinc.ai/docs/api-optimizers) object.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> optimizer = parser.begin_training(pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                         |
| -------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects.          |
| _keyword-only_ |                                                     |                                                                                                                     |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                                |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/dependencyparser#create_optimizer) if not set. |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                      |

## DependencyParser.predict {#predict tag="method"}

Apply the pipeline's model to a batch of docs, without modifying them.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> scores = parser.predict([doc1, doc2])
> ```

| Name        | Type                | Description                                    |
| ----------- | ------------------- | ---------------------------------------------- |
| `docs`      | `Iterable[Doc]`     | The documents to predict.                      |
| **RETURNS** | `syntax.StateClass` | A helper class for the parse state (internal). |

## DependencyParser.set_annotations {#set_annotations tag="method"}

Modify a batch of documents, using pre-computed scores.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> scores = parser.predict([doc1, doc2])
> parser.set_annotations([doc1, doc2], scores)
> ```

| Name     | Type                | Description                                                |
| -------- | ------------------- | ---------------------------------------------------------- |
| `docs`   | `Iterable[Doc]`     | The documents to modify.                                   |
| `scores` | `syntax.StateClass` | The scores to set, produced by `DependencyParser.predict`. |

## DependencyParser.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects, updating the pipe's
model. Delegates to [`predict`](/api/dependencyparser#predict) and
[`get_loss`](/api/dependencyparser#get_loss).

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> optimizer = nlp.begin_training()
> losses = parser.update(examples, sgd=optimizer)
> ```

| Name              | Type                | Description                                                                                                                                    |
| ----------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | `Iterable[Example]` | A batch of [`Example`](/api/example) objects to learn from.                                                                                    |
| _keyword-only_    |                     |                                                                                                                                                |
| `drop`            | float               | The dropout rate.                                                                                                                              |
| `set_annotations` | bool                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/dependencyparser#set_annotations). |
| `sgd`             | `Optimizer`         | The [`Optimizer`](https://thinc.ai/docs/api-optimizers) object.                                                                                |
| `losses`          | `Dict[str, float]`  | Optional record of the loss during training. Updated using the component name as the key.                                                      |
| **RETURNS**       | `Dict[str, float]`  | The updated `losses` dictionary.                                                                                                               |

## DependencyParser.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> scores = parser.predict([eg.predicted for eg in examples])
> loss, d_loss = parser.get_loss(examples, scores)
> ```

| Name        | Type                  | Description                                         |
| ----------- | --------------------- | --------------------------------------------------- |
| `examples`  | `Iterable[Example]`   | The batch of examples.                              |
| `scores`    | `syntax.StateClass`   | Scores representing the model's predictions.        |
| **RETURNS** | `Tuple[float, float]` | The loss and the gradient, i.e. `(loss, gradient)`. |

## DependencyParser.score {#score tag="method" new="3"}

Score a batch of examples.

> #### Example
>
> ```python
> scores = parser.score(examples)
> ```

| Name        | Type                | Description                                                                                                                |
| ----------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The examples to score.                                                                                                     |
| **RETURNS** | `Dict[str, Any]`    | The scores, produced by [`Scorer.score_spans`](/api/scorer#score_spans) and [`Scorer.score_deps`](/api/scorer#score_deps). |

## DependencyParser.create_optimizer {#create_optimizer tag="method"}

Create an [`Optimizer`](https://thinc.ai/docs/api-optimizers) for the pipeline
component.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> optimizer = parser.create_optimizer()
> ```

| Name        | Type                                                | Description    |
| ----------- | --------------------------------------------------- | -------------- |
| **RETURNS** | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer. |

## DependencyParser.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> parser = DependencyParser(nlp.vocab)
> with parser.use_params(optimizer.averages):
>     parser.to_disk("/best_model")
> ```

| Name     | Type | Description                               |
| -------- | ---- | ----------------------------------------- |
| `params` | dict | The parameter values to use in the model. |

## DependencyParser.add_label {#add_label tag="method"}

Add a new label to the pipe.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> parser.add_label("MY_LABEL")
> ```

| Name        | Type | Description                                         |
| ----------- | ---- | --------------------------------------------------- |
| `label`     | str  | The label to add.                                   |
| **RETURNS** | int  | `0` if the label is already present, otherwise `1`. |

## DependencyParser.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> parser.to_disk("/path/to/parser")
> ```

| Name      | Type            | Description                                                                                                           |
| --------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`    | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| `exclude` | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## DependencyParser.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> parser.from_disk("/path/to/parser")
> ```

| Name        | Type               | Description                                                                |
| ----------- | ------------------ | -------------------------------------------------------------------------- |
| `path`      | str / `Path`       | A path to a directory. Paths may be either strings or `Path`-like objects. |
| `exclude`   | `Iterable[str]`    | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS** | `DependencyParser` | The modified `DependencyParser` object.                                    |

## DependencyParser.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> parser_bytes = parser.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name        | Type            | Description                                                               |
| ----------- | --------------- | ------------------------------------------------------------------------- |
| `exclude`   | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS** | bytes           | The serialized form of the `DependencyParser` object.                     |

## DependencyParser.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> parser_bytes = parser.to_bytes()
> parser = nlp.add_pipe("parser")
> parser.from_bytes(parser_bytes)
> ```

| Name         | Type               | Description                                                               |
| ------------ | ------------------ | ------------------------------------------------------------------------- |
| `bytes_data` | bytes              | The data to load from.                                                    |
| `exclude`    | `Iterable[str]`    | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**  | `DependencyParser` | The `DependencyParser` object.                                            |

## DependencyParser.labels {#labels tag="property"}

The labels currently added to the component.

> #### Example
>
> ```python
> parser.add_label("MY_LABEL")
> assert "MY_LABEL" in parser.labels
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
> data = parser.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
