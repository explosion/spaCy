---
title: EntityRecognizer
tag: class
source: spacy/pipeline/ner.pyx
teaser: 'Pipeline component for named entity recognition'
api_base_class: /api/pipe
api_string_name: ner
api_trainable: true
---

A transition-based named entity recognition component. The entity recognizer
identifies **non-overlapping labelled spans** of tokens. The transition-based
algorithm used encodes certain assumptions that are effective for "traditional"
named entity recognition tasks, but may not be a good fit for every span
identification problem. Specifically, the loss function optimizes for **whole
entity accuracy**, so if your inter-annotator agreement on boundary tokens is
low, the component will likely perform poorly on your problem. The
transition-based algorithm also assumes that the most decisive information about
your entities will be close to their initial tokens. If your entities are long
and characterized by tokens in their middle, the component will likely not be a
good fit for your task.

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
> from spacy.pipeline.ner import DEFAULT_NER_MODEL
> config = {
>    "moves": None,
>    "update_with_oracle_cut_size": 100,
>    "model": DEFAULT_NER_MODEL,
> }
> nlp.add_pipe("ner", config=config)
> ```

| Setting                       | Description                                                                                                                                                                                                                                         |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `moves`                       | A list of transition names. Inferred from the data if not provided. Defaults to `None`. ~~Optional[List[str]]                                                                                                                                       |
| `update_with_oracle_cut_size` | During training, cut long sequences into shorter segments by creating intermediate states based on the gold-standard history. The model is not very sensitive to this parameter, so you usually won't need to change it. Defaults to `100`. ~~int~~ |
| `model`                       | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. Defaults to [TransitionBasedParser](/api/architectures#TransitionBasedParser). ~~Model[List[Doc], List[Floats2d]]~~                                                 |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/ner.pyx
```

## EntityRecognizer.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> ner = nlp.add_pipe("ner")
>
> # Construction via add_pipe with custom model
> config = {"model": {"@architectures": "my_ner"}}
> parser = nlp.add_pipe("ner", config=config)
>
> # Construction from class
> from spacy.pipeline import EntityRecognizer
> ner = EntityRecognizer(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

| Name                          | Description                                                                                                                                                                                                                                               |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`                       | The shared vocabulary. ~~Vocab~~                                                                                                                                                                                                                          |
| `model`                       | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                      |
| `name`                        | String name of the component instance. Used to add entries to the `losses` during training. ~~str~~                                                                                                                                                       |
| `moves`                       | A list of transition names. Inferred from the data if not provided. ~~Optional[List[str]]~~                                                                                                                                                               |
| _keyword-only_                |                                                                                                                                                                                                                                                           |
| `update_with_oracle_cut_size` | During training, cut long sequences into shorter segments by creating intermediate states based on the gold-standard history. The model is not very sensitive to this parameter, so you usually won't need to change it. `100` is a good default. ~~int~~ |

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
> doc = nlp("This is a sentence.")
> ner = nlp.add_pipe("ner")
> # This usually happens under the hood
> processed = ner(doc)
> ```

| Name        | Description                      |
| ----------- | -------------------------------- |
| `doc`       | The document to process. ~~Doc~~ |
| **RETURNS** | The processed document. ~~Doc~~  |

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
> ner = nlp.add_pipe("ner")
> for doc in ner.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `docs`         | A stream of documents. ~~Iterable[Doc]~~                      |
| _keyword-only_ |                                                               |
| `batch_size`   | The number of documents to buffer. Defaults to `128`. ~~int~~ |
| **YIELDS**     | The processed documents in order. ~~Doc~~                     |

## EntityRecognizer.begin_training {#begin_training tag="method"}

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
> ner = nlp.add_pipe("ner")
> optimizer = ner.begin_training(lambda: [], pipeline=nlp.pipeline)
> ```

| Name           | Description                                                                                                                           |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. ~~Callable[[], Iterable[Example]]~~ |
| _keyword-only_ |                                                                                                                                       |
| `pipeline`     | Optional list of pipeline components that this component is part of. ~~Optional[List[Tuple[str, Callable[[Doc], Doc]]]]~~             |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~                         |
| **RETURNS**    | The optimizer. ~~Optimizer~~                                                                                                          |

## EntityRecognizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> scores = ner.predict([doc1, doc2])
> ```

| Name        | Description                                                   |
| ----------- | ------------------------------------------------------------- |
| `docs`      | The documents to predict. ~~Iterable[Doc]~~                   |
| **RETURNS** | A helper class for the parse state (internal). ~~StateClass~~ |

## EntityRecognizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> scores = ner.predict([doc1, doc2])
> ner.set_annotations([doc1, doc2], scores)
> ```

| Name     | Description                                                                                                                           |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `docs`   | The documents to modify. ~~Iterable[Doc]~~                                                                                            |
| `scores` | The scores to set, produced by `EntityRecognizer.predict`. Returns an internal helper class for the parse state. ~~List[StateClass]~~ |

## EntityRecognizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects, updating the pipe's
model. Delegates to [`predict`](/api/entityrecognizer#predict) and
[`get_loss`](/api/entityrecognizer#get_loss).

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> optimizer = nlp.begin_training()
> losses = ner.update(examples, sgd=optimizer)
> ```

| Name              | Description                                                                                                                        |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                                  |
| _keyword-only_    |                                                                                                                                    |  |
| `drop`            | The dropout rate. ~~float~~                                                                                                        |
| `set_annotations` | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](#set_annotations). ~~bool~~ |
| `sgd`             | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~                      |
| `losses`          | Optional record of the loss during training. Updated using the component name as the key. ~~Optional[Dict[str, float]]~~           |
| **RETURNS**       | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                              |

## EntityRecognizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> scores = ner.predict([eg.predicted for eg in examples])
> loss, d_loss = ner.get_loss(examples, scores)
> ```

| Name        | Description                                                                 |
| ----------- | --------------------------------------------------------------------------- |
| `examples`  | The batch of examples. ~~Iterable[Example]~~                                |
| `scores`    | Scores representing the model's predictions. ~~StateClass~~                 |
| **RETURNS** | The loss and the gradient, i.e. `(loss, gradient)`. ~~Tuple[float, float]~~ |

## EntityRecognizer.score {#score tag="method" new="3"}

Score a batch of examples.

> #### Example
>
> ```python
> scores = ner.score(examples)
> ```

| Name        | Description                                                                                                            |
| ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| `examples`  | The examples to score. ~~Iterable[Example]~~                                                                           |
| **RETURNS** | The scores, produced by [`Scorer.score_spans`](/api/scorer#score_spans). ~~Dict[str, Union[float, Dict[str, float]]]~~ |

## EntityRecognizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> optimizer = ner.create_optimizer()
> ```

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The optimizer. ~~Optimizer~~ |

## EntityRecognizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> ner = EntityRecognizer(nlp.vocab)
> with ner.use_params(optimizer.averages):
>     ner.to_disk("/best_model")
> ```

| Name     | Description                                        |
| -------- | -------------------------------------------------- |
| `params` | The parameter values to use in the model. ~~dict~~ |

## EntityRecognizer.add_label {#add_label tag="method"}

Add a new label to the pipe.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.add_label("MY_LABEL")
> ```

| Name        | Description                                                 |
| ----------- | ----------------------------------------------------------- |
| `label`     | The label to add. ~~str~~                                   |
| **RETURNS** | `0` if the label is already present, otherwise `1`. ~~int~~ |

## EntityRecognizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.to_disk("/path/to/ner")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## EntityRecognizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner.from_disk("/path/to/ner")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `EntityRecognizer` object. ~~EntityRecognizer~~                                    |

## EntityRecognizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> ner = nlp.add_pipe("ner")
> ner_bytes = ner.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The serialized form of the `EntityRecognizer` object. ~~bytes~~                             |

## EntityRecognizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ner_bytes = ner.to_bytes()
> ner = nlp.add_pipe("ner")
> ner.from_bytes(ner_bytes)
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                            |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `EntityRecognizer` object. ~~EntityRecognizer~~                                         |

## EntityRecognizer.labels {#labels tag="property"}

The labels currently added to the component.

> #### Example
>
> ```python
> ner.add_label("MY_LABEL")
> assert "MY_LABEL" in ner.labels
> ```

| Name        | Description                                            |
| ----------- | ------------------------------------------------------ |
| **RETURNS** | The labels added to the component. ~~Tuple[str, ...]~~ |

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
