---
title: Tok2Vec
source: spacy/pipeline/tok2vec.py
new: 3
teaser: null
api_base_class: /api/pipe
api_string_name: tok2vec
api_trainable: true
---

Apply a "token-to-vector" model and set its outputs in the `Doc.tensor`
attribute. This is mostly useful to **share a single subnetwork** between
multiple components, e.g. to have one embedding and CNN network shared between a
[`DependencyParser`](/api/dependencyparser), [`Tagger`](/api/tagger) and
[`EntityRecognizer`](/api/entityrecognizer).

In order to use the `Tok2Vec` predictions, subsequent components should use the
[Tok2VecListener](/api/architectures#Tok2VecListener) layer as the tok2vec
subnetwork of their model. This layer will read data from the `doc.tensor`
attribute during prediction. During training, the `Tok2Vec` component will save
its prediction and backprop callback for each batch, so that the subsequent
components can backpropagate to the shared weights. This implementation is used
because it allows us to avoid relying on object identity within the models to
achieve the parameter sharing.

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
> from spacy.pipeline.tok2vec import DEFAULT_TOK2VEC_MODEL
> config = {"model": DEFAULT_TOK2VEC_MODEL}
> nlp.add_pipe("tok2vec", config=config)
> ```

| Setting | Type                                       | Description                                                             | Default                                         |
| ------- | ------------------------------------------ | ----------------------------------------------------------------------- | ----------------------------------------------- |
| `model` | [`Model`](https://thinc.ai/docs/api-model) | **Input:** `List[Doc]`. **Output:** `List[Floats2d]`. The model to use. | [HashEmbedCNN](/api/architectures#HashEmbedCNN) |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/tok2vec.py
```

## Tok2Vec.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> tok2vec = nlp.add_pipe("tok2vec")
>
> # Construction via add_pipe with custom model
> config = {"model": {"@architectures": "my_tok2vec"}}
> parser = nlp.add_pipe("tok2vec", config=config)
>
> # Construction from class
> from spacy.pipeline import Tok2Vec
> tok2vec = Tok2Vec(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#create_pipe).

| Name    | Type                                       | Description                                                                                 |
| ------- | ------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `vocab` | `Vocab`                                    | The shared vocabulary.                                                                      |
| `model` | [`Model`](https://thinc.ai/docs/api-model) | The Thinc [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.       |
| `name`  | str                                        | String name of the component instance. Used to add entries to the `losses` during training. |

## Tok2Vec.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document and add context-sensitive embeddings to the
`Doc.tensor` attribute, allowing them to be used as features by downstream
components. The document is modified in place, and returned. This usually
happens under the hood when the `nlp` object is called on a text and all
pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/tok2vec#call) and [`pipe`](/api/tok2vec#pipe) delegate to the
[`predict`](/api/tok2vec#predict) and
[`set_annotations`](/api/tok2vec#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> tok2vec = nlp.add_pipe("tok2vec")
> # This usually happens under the hood
> processed = tok2vec(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## Tok2Vec.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/tok2vec#call) and
[`pipe`](/api/tok2vec#pipe) delegate to the [`predict`](/api/tok2vec#predict)
and [`set_annotations`](/api/tok2vec#set_annotations) methods.

> #### Example
>
> ```python
> tok2vec = nlp.add_pipe("tok2vec")
> for doc in tok2vec.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                           |
| -------------- | --------------- | ----------------------------------------------------- |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                |
| _keyword-only_ |                 |                                                       |
| `batch_size`   | int             | The number of documents to buffer. Defaults to `128`. |
| **YIELDS**     | `Doc`           | The processed documents in order.                     |

## Tok2Vec.begin_training {#begin_training tag="method"}

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
> tok2vec = nlp.add_pipe("tok2vec")
> optimizer = tok2vec.begin_training(lambda: [], pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                |
| -------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. |
| _keyword-only_ |                                                     |                                                                                                            |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                       |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/tok2vec#create_optimizer) if not set. |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                             |

## Tok2Vec.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> tok2vec = nlp.add_pipe("tok2vec")
> scores = tok2vec.predict([doc1, doc2])
> ```

| Name        | Type            | Description                               |
| ----------- | --------------- | ----------------------------------------- |
| `docs`      | `Iterable[Doc]` | The documents to predict.                 |
| **RETURNS** | -               | The model's prediction for each document. |

## Tok2Vec.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

> #### Example
>
> ```python
> tok2vec = nlp.add_pipe("tok2vec")
> scores = tok2vec.predict(docs)
> tok2vec.set_annotations(docs, scores)
> ```

| Name     | Type            | Description                                       |
| -------- | --------------- | ------------------------------------------------- |
| `docs`   | `Iterable[Doc]` | The documents to modify.                          |
| `scores` | -               | The scores to set, produced by `Tok2Vec.predict`. |

## Tok2Vec.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects containing the
predictions and gold-standard annotations, and update the component's model.
Delegates to [`predict`](/api/tok2vec#predict).

> #### Example
>
> ```python
> tok2vec = nlp.add_pipe("tok2vec")
> optimizer = nlp.begin_training()
> losses = tok2vec.update(examples, sgd=optimizer)
> ```

| Name              | Type                                                | Description                                                                                                                           |
| ----------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects to learn from.                                                                           |
| _keyword-only_    |                                                     |                                                                                                                                       |
| `drop`            | float                                               | The dropout rate.                                                                                                                     |
| `set_annotations` | bool                                                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/tok2vec#set_annotations). |
| `sgd`             | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                                        |
| `losses`          | `Dict[str, float]`                                  | Optional record of the loss during training. Updated using the component name as the key.                                             |
| **RETURNS**       | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                                                                      |

## Tok2Vec.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> tok2vec = nlp.add_pipe("tok2vec")
> optimizer = tok2vec.create_optimizer()
> ```

| Name        | Type                                                | Description    |
| ----------- | --------------------------------------------------- | -------------- |
| **RETURNS** | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer. |

## Tok2Vec.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> tok2vec = nlp.add_pipe("tok2vec")
> with tok2vec.use_params(optimizer.averages):
>     tok2vec.to_disk("/best_model")
> ```

| Name     | Type | Description                               |
| -------- | ---- | ----------------------------------------- |
| `params` | dict | The parameter values to use in the model. |

## Tok2Vec.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> tok2vec = nlp.add_pipe("tok2vec")
> tok2vec.to_disk("/path/to/tok2vec")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## Tok2Vec.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> tok2vec = nlp.add_pipe("tok2vec")
> tok2vec.from_disk("/path/to/tok2vec")
> ```

| Name           | Type            | Description                                                                |
| -------------- | --------------- | -------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                            |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `Tok2Vec`       | The modified `Tok2Vec` object.                                             |

## Tok2Vec.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> tok2vec = nlp.add_pipe("tok2vec")
> tok2vec_bytes = tok2vec.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the `Tok2Vec` object.                              |

## Tok2Vec.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> tok2vec_bytes = tok2vec.to_bytes()
> tok2vec = nlp.add_pipe("tok2vec")
> tok2vec.from_bytes(tok2vec_bytes)
> ```

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| `bytes_data`   | bytes           | The data to load from.                                                    |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | `Tok2Vec`       | The `Tok2Vec` object.                                                     |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = tok2vec.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
