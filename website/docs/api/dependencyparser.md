---
title: DependencyParser
tag: class
source: spacy/pipeline/dep_parser.pyx
teaser: 'Pipeline component for syntactic dependency parsing'
api_base_class: /api/pipe
api_string_name: parser
api_trainable: true
---

A transition-based dependency parser component. The dependency parser jointly
learns sentence segmentation and labelled dependency parsing, and can optionally
learn to merge tokens that had been over-segmented by the tokenizer. The parser
uses a variant of the **non-monotonic arc-eager transition-system** described by
[Honnibal and Johnson (2014)](https://www.aclweb.org/anthology/D15-1162/), with
the addition of a "break" transition to perform the sentence segmentation.
[Nivre (2005)](https://www.aclweb.org/anthology/P05-1013/)'s **pseudo-projective
dependency transformation** is used to allow the parser to predict
non-projective parses.

The parser is trained using an **imitation learning objective**. It follows the
actions predicted by the current weights, and at each state, determines which
actions are compatible with the optimal parse that could be reached from the
current state. The weights such that the scores assigned to the set of optimal
actions is increased, while scores assigned to other actions are decreased. Note
that more than one action may be optimal for a given state.

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
>    "update_with_oracle_cut_size": 100,
>    "learn_tokens": False,
>    "min_action_freq": 30,
>    "model": DEFAULT_PARSER_MODEL,
> }
> nlp.add_pipe("parser", config=config)
> ```

| Setting                       | Type                                       | Description                                                                                                                                                                                                                                                                                 | Default                                                           |
| ----------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `moves`                       | `List[str]`                                | A list of transition names. Inferred from the data if not provided.                                                                                                                                                                                                                         | `None`                                                            |
| `update_with_oracle_cut_size` | int                                        | During training, cut long sequences into shorter segments by creating intermediate states based on the gold-standard history. The model is not very sensitive to this parameter, so you usually won't need to change it.                                                                    | `100`                                                             |
| `learn_tokens`                | bool                                       | Whether to learn to merge subtokens that are split relative to the gold standard. Experimental.                                                                                                                                                                                             | `False`                                                           |
| `min_action_freq`             | int                                        | The minimum frequency of labelled actions to retain. Rarer labelled actions have their label backed-off to "dep". While this primarily affects the label accuracy, it can also affect the attachment structure, as the labels are used to represent the pseudo-projectivity transformation. | `30`                                                              |
| `model`                       | [`Model`](https://thinc.ai/docs/api-model) | The model to use.                                                                                                                                                                                                                                                                           | [TransitionBasedParser](/api/architectures#TransitionBasedParser) |

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

| Name                          | Type                                       | Description                                                                                                                                                                                                                                                                                 |
| ----------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`                       | `Vocab`                                    | The shared vocabulary.                                                                                                                                                                                                                                                                      |
| `model`                       | [`Model`](https://thinc.ai/docs/api-model) | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.                                                                                                                                                                                                             |
| `name`                        | str                                        | String name of the component instance. Used to add entries to the `losses` during training.                                                                                                                                                                                                 |
| `moves`                       | `List[str]`                                | A list of transition names. Inferred from the data if not provided.                                                                                                                                                                                                                         |
| _keyword-only_                |                                            |                                                                                                                                                                                                                                                                                             |
| `update_with_oracle_cut_size` | int                                        | During training, cut long sequences into shorter segments by creating intermediate states based on the gold-standard history. The model is not very sensitive to this parameter, so you usually won't need to change it. `100` is a good default.                                           |
| `learn_tokens`                | bool                                       | Whether to learn to merge subtokens that are split relative to the gold standard. Experimental.                                                                                                                                                                                             |
| `min_action_freq`             | int                                        | The minimum frequency of labelled actions to retain. Rarer labelled actions have their label backed-off to "dep". While this primarily affects the label accuracy, it can also affect the attachment structure, as the labels are used to represent the pseudo-projectivity transformation. |

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
> parser = nlp.add_pipe("parser")
> optimizer = parser.begin_training(lambda: [], pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                         |
| -------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects.          |
| _keyword-only_ |                                                     |                                                                                                                     |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                                |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/dependencyparser#create_optimizer) if not set. |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                      |

## DependencyParser.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

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

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

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

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## DependencyParser.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> parser.from_disk("/path/to/parser")
> ```

| Name           | Type               | Description                                                                |
| -------------- | ------------------ | -------------------------------------------------------------------------- |
| `path`         | str / `Path`       | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                    |                                                                            |
| `exclude`      | `Iterable[str]`    | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `DependencyParser` | The modified `DependencyParser` object.                                    |

## DependencyParser.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> parser = nlp.add_pipe("parser")
> parser_bytes = parser.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the `DependencyParser` object.                     |

## DependencyParser.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> parser_bytes = parser.to_bytes()
> parser = nlp.add_pipe("parser")
> parser.from_bytes(parser_bytes)
> ```

| Name           | Type               | Description                                                               |
| -------------- | ------------------ | ------------------------------------------------------------------------- |
| `bytes_data`   | bytes              | The data to load from.                                                    |
| _keyword-only_ |                    |                                                                           |
| `exclude`      | `Iterable[str]`    | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | `DependencyParser` | The `DependencyParser` object.                                            |

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
