---
title: EditTreeLemmatizer
tag: class
source: spacy/pipeline/edit_tree_lemmatizer.py
new: 3.3
teaser: 'Pipeline component for lemmatization'
api_base_class: /api/pipe
api_string_name: trainable_lemmatizer
api_trainable: true
---

A trainable component for assigning base forms to tokens. This lemmatizer uses
**edit trees** to transform tokens into base forms. The lemmatization model
predicts which edit tree is applicable to a token. The edit tree data structure
and construction method used by this lemmatizer were proposed in
[Joint Lemmatization and Morphological Tagging with Lemming](https://aclanthology.org/D15-1272.pdf)
(Thomas Müller et al., 2015).

For a lookup and rule-based lemmatizer, see [`Lemmatizer`](/api/lemmatizer).

## Assigned Attributes {#assigned-attributes}

Predictions are assigned to `Token.lemma`.

| Location       | Value                     |
| -------------- | ------------------------- |
| `Token.lemma`  | The lemma (hash). ~~int~~ |
| `Token.lemma_` | The lemma. ~~str~~        |

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
> from spacy.pipeline.edit_tree_lemmatizer import DEFAULT_EDIT_TREE_LEMMATIZER_MODEL
> config = {"model": DEFAULT_EDIT_TREE_LEMMATIZER_MODEL}
> nlp.add_pipe("trainable_lemmatizer", config=config, name="lemmatizer")
> ```

| Setting         | Description                                                                                                                                                                                                                                                                                                        |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `model`         | A model instance that predicts the edit tree probabilities. The output vectors should match the number of edit trees in size, and be normalized as probabilities (all scores between 0 and 1, with the rows summing to `1`). Defaults to [Tagger](/api/architectures#Tagger). ~~Model[List[Doc], List[Floats2d]]~~ |
| `backoff`       | ~~Token~~ attribute to use when no applicable edit tree is found. Defaults to `orth`. ~~str~~                                                                                                                                                                                                                      |
| `min_tree_freq` | Minimum frequency of an edit tree in the training set to be used. Defaults to `3`. ~~int~~                                                                                                                                                                                                                         |
| `overwrite`     | Whether existing annotation is overwritten. Defaults to `False`. ~~bool~~                                                                                                                                                                                                                                          |
| `top_k`         | The number of most probable edit trees to try before resorting to `backoff`. Defaults to `1`. ~~int~~                                                                                                                                                                                                              |
| `scorer`        | The scoring method. Defaults to [`Scorer.score_token_attr`](/api/scorer#score_token_attr) for the attribute `"lemma"`. ~~Optional[Callable]~~                                                                                                                                                                      |

```python
%%GITHUB_SPACY/spacy/pipeline/edit_tree_lemmatizer.py
```

## EditTreeLemmatizer.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
>
> # Construction via create_pipe with custom model
> config = {"model": {"@architectures": "my_tagger"}}
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", config=config, name="lemmatizer")
>
> # Construction from class
> from spacy.pipeline import EditTreeLemmatizer
> lemmatizer = EditTreeLemmatizer(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

| Name            | Description                                                                                                                                                                                                                                                       |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`         | The shared vocabulary. ~~Vocab~~                                                                                                                                                                                                                                  |
| `model`         | A model instance that predicts the edit tree probabilities. The output vectors should match the number of edit trees in size, and be normalized as probabilities (all scores between 0 and 1, with the rows summing to `1`). ~~Model[List[Doc], List[Floats2d]]~~ |
| `name`          | String name of the component instance. Used to add entries to the `losses` during training. ~~str~~                                                                                                                                                               |
| _keyword-only_  |                                                                                                                                                                                                                                                                   |
| `backoff`       | ~~Token~~ attribute to use when no applicable edit tree is found. Defaults to `orth`. ~~str~~                                                                                                                                                                     |
| `min_tree_freq` | Minimum frequency of an edit tree in the training set to be used. Defaults to `3`. ~~int~~                                                                                                                                                                        |
| `overwrite`     | Whether existing annotation is overwritten. Defaults to `False`. ~~bool~~                                                                                                                                                                                         |
| `top_k`         | The number of most probable edit trees to try before resorting to `backoff`. Defaults to `1`. ~~int~~                                                                                                                                                             |
| `scorer`        | The scoring method. Defaults to [`Scorer.score_token_attr`](/api/scorer#score_token_attr) for the attribute `"lemma"`. ~~Optional[Callable]~~                                                                                                                     |

## EditTreeLemmatizer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/edittreelemmatizer#call) and
[`pipe`](/api/edittreelemmatizer#pipe) delegate to the
[`predict`](/api/edittreelemmatizer#predict) and
[`set_annotations`](/api/edittreelemmatizer#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> # This usually happens under the hood
> processed = lemmatizer(doc)
> ```

| Name        | Description                      |
| ----------- | -------------------------------- |
| `doc`       | The document to process. ~~Doc~~ |
| **RETURNS** | The processed document. ~~Doc~~  |

## EditTreeLemmatizer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/edittreelemmatizer#call)
and [`pipe`](/api/edittreelemmatizer#pipe) delegate to the
[`predict`](/api/edittreelemmatizer#predict) and
[`set_annotations`](/api/edittreelemmatizer#set_annotations) methods.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> for doc in lemmatizer.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `stream`       | A stream of documents. ~~Iterable[Doc]~~                      |
| _keyword-only_ |                                                               |
| `batch_size`   | The number of documents to buffer. Defaults to `128`. ~~int~~ |
| **YIELDS**     | The processed documents in order. ~~Doc~~                     |

## EditTreeLemmatizer.initialize {#initialize tag="method" new="3"}

Initialize the component for training. `get_examples` should be a function that
returns an iterable of [`Example`](/api/example) objects. **At least one example
should be supplied.** The data examples are used to **initialize the model** of
the component and can either be the full training data or a representative
sample. Initialization includes validating the network,
[inferring missing shapes](https://thinc.ai/docs/usage-models#validation) and
setting up the label scheme based on the data. This method is typically called
by [`Language.initialize`](/api/language#initialize) and lets you customize
arguments it receives via the
[`[initialize.components]`](/api/data-formats#config-initialize) block in the
config.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> lemmatizer.initialize(lambda: examples, nlp=nlp)
> ```
>
> ```ini
> ### config.cfg
> [initialize.components.lemmatizer]
>
> [initialize.components.lemmatizer.labels]
> @readers = "spacy.read_labels.v1"
> path = "corpus/labels/lemmatizer.json
> ```

| Name           | Description                                                                                                                                                                                                                                                                                                                                                                                                |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. Must contain at least one `Example`. ~~Callable[[], Iterable[Example]]~~                                                                                                                                                                                                                                 |
| _keyword-only_ |                                                                                                                                                                                                                                                                                                                                                                                                            |
| `nlp`          | The current `nlp` object. Defaults to `None`. ~~Optional[Language]~~                                                                                                                                                                                                                                                                                                                                       |
| `labels`       | The label information to add to the component, as provided by the [`label_data`](#label_data) property after initialization. To generate a reusable JSON file from your data, you should run the [`init labels`](/api/cli#init-labels) command. If no labels are provided, the `get_examples` callback is used to extract the labels from the data, which may be a lot slower. ~~Optional[Iterable[str]]~~ |

## EditTreeLemmatizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> tree_ids = lemmatizer.predict([doc1, doc2])
> ```

| Name        | Description                                 |
| ----------- | ------------------------------------------- |
| `docs`      | The documents to predict. ~~Iterable[Doc]~~ |
| **RETURNS** | The model's prediction for each document.   |

## EditTreeLemmatizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed tree
identifiers.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> tree_ids = lemmatizer.predict([doc1, doc2])
> lemmatizer.set_annotations([doc1, doc2], tree_ids)
> ```

| Name       | Description                                                                           |
| ---------- | ------------------------------------------------------------------------------------- |
| `docs`     | The documents to modify. ~~Iterable[Doc]~~                                            |
| `tree_ids` | The identifiers of the edit trees to apply, produced by `EditTreeLemmatizer.predict`. |

## EditTreeLemmatizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects containing the
predictions and gold-standard annotations, and update the component's model.
Delegates to [`predict`](/api/edittreelemmatizer#predict) and
[`get_loss`](/api/edittreelemmatizer#get_loss).

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> optimizer = nlp.initialize()
> losses = lemmatizer.update(examples, sgd=optimizer)
> ```

| Name           | Description                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `examples`     | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                        |
| _keyword-only_ |                                                                                                                          |
| `drop`         | The dropout rate. ~~float~~                                                                                              |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~            |
| `losses`       | Optional record of the loss during training. Updated using the component name as the key. ~~Optional[Dict[str, float]]~~ |
| **RETURNS**    | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                    |

## EditTreeLemmatizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> scores = lemmatizer.model.begin_update([eg.predicted for eg in examples])
> loss, d_loss = lemmatizer.get_loss(examples, scores)
> ```

| Name        | Description                                                                 |
| ----------- | --------------------------------------------------------------------------- |
| `examples`  | The batch of examples. ~~Iterable[Example]~~                                |
| `scores`    | Scores representing the model's predictions.                                |
| **RETURNS** | The loss and the gradient, i.e. `(loss, gradient)`. ~~Tuple[float, float]~~ |

## EditTreeLemmatizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> optimizer = lemmatizer.create_optimizer()
> ```

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The optimizer. ~~Optimizer~~ |

## EditTreeLemmatizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> with lemmatizer.use_params(optimizer.averages):
>     lemmatizer.to_disk("/best_model")
> ```

| Name     | Description                                        |
| -------- | -------------------------------------------------- |
| `params` | The parameter values to use in the model. ~~dict~~ |

## EditTreeLemmatizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> lemmatizer.to_disk("/path/to/lemmatizer")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## EditTreeLemmatizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> lemmatizer.from_disk("/path/to/lemmatizer")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `EditTreeLemmatizer` object. ~~EditTreeLemmatizer~~                                |

## EditTreeLemmatizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> lemmatizer_bytes = lemmatizer.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The serialized form of the `EditTreeLemmatizer` object. ~~bytes~~                           |

## EditTreeLemmatizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> lemmatizer_bytes = lemmatizer.to_bytes()
> lemmatizer = nlp.add_pipe("trainable_lemmatizer", name="lemmatizer")
> lemmatizer.from_bytes(lemmatizer_bytes)
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                            |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `EditTreeLemmatizer` object. ~~EditTreeLemmatizer~~                                     |

## EditTreeLemmatizer.labels {#labels tag="property"}

The labels currently added to the component.

<Infobox variant="warning" title="Interpretability of the labels">

The `EditTreeLemmatizer` labels are not useful by themselves, since they are
identifiers of edit trees.

</Infobox>

| Name        | Description                                            |
| ----------- | ------------------------------------------------------ |
| **RETURNS** | The labels added to the component. ~~Tuple[str, ...]~~ |

## EditTreeLemmatizer.label_data {#label_data tag="property" new="3"}

The labels currently added to the component and their internal meta information.
This is the data generated by [`init labels`](/api/cli#init-labels) and used by
[`EditTreeLemmatizer.initialize`](/api/edittreelemmatizer#initialize) to
initialize the model with a pre-defined label set.

> #### Example
>
> ```python
> labels = lemmatizer.label_data
> lemmatizer.initialize(lambda: [], nlp=nlp, labels=labels)
> ```

| Name        | Description                                                |
| ----------- | ---------------------------------------------------------- |
| **RETURNS** | The label data added to the component. ~~Tuple[str, ...]~~ |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = lemmatizer.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
| `trees` | The edit trees. You usually don't want to exclude this.        |
