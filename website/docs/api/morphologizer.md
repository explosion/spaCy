---
title: Morphologizer
tag: class
source: spacy/pipeline/morphologizer.pyx
new: 3
teaser: 'Pipeline component for predicting morphological features'
api_base_class: /api/tagger
api_string_name: morphologizer
api_trainable: true
---

A trainable pipeline component to predict morphological features and
coarse-grained POS tags following the Universal Dependencies
[UPOS](https://universaldependencies.org/u/pos/index.html) and
[FEATS](https://universaldependencies.org/format.html#morphological-annotation)
annotation guidelines.

## Assigned Attributes {#assigned-attributes}

Predictions are saved to `Token.morph` and `Token.pos`.

| Location      | Value                                     |
| ------------- | ----------------------------------------- |
| `Token.pos`   | The UPOS part of speech (hash). ~~int~~   |
| `Token.pos_`  | The UPOS part of speech. ~~str~~          |
| `Token.morph` | Morphological features. ~~MorphAnalysis~~ |

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
> from spacy.pipeline.morphologizer import DEFAULT_MORPH_MODEL
> config = {"model": DEFAULT_MORPH_MODEL}
> nlp.add_pipe("morphologizer", config=config)
> ```

| Setting                                  | Description                                                                                                                                                                                                                                                            |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                                  | The model to use. Defaults to [Tagger](/api/architectures#Tagger). ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                                |
| `overwrite` <Tag variant="new">3.2</Tag> | Whether the values of existing features are overwritten. Defaults to `True`. ~~bool~~                                                                                                                                                                                  |
| `extend` <Tag variant="new">3.2</Tag>    | Whether existing feature types (whose values may or may not be overwritten depending on `overwrite`) are preserved. Defaults to `False`. ~~bool~~                                                                                                                      |
| `scorer` <Tag variant="new">3.2</Tag>    | The scoring method. Defaults to [`Scorer.score_token_attr`](/api/scorer#score_token_attr) for the attributes `"pos"` and `"morph"` and [`Scorer.score_token_attr_per_feat`](/api/scorer#score_token_attr_per_feat) for the attribute `"morph"`. ~~Optional[Callable]~~ |

```python
%%GITHUB_SPACY/spacy/pipeline/morphologizer.pyx
```

## Morphologizer.\_\_init\_\_ {#init tag="method"}

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

The `overwrite` and `extend` settings determine how existing annotation is
handled (with the example for existing annotation `A=B|C=D` + predicted
annotation `C=E|X=Y`):

- `overwrite=True, extend=True`: overwrite values of existing features, add any
  new features (`A=B|C=D` + `C=E|X=Y` &rarr; `A=B|C=E|X=Y`)
- `overwrite=True, extend=False`: overwrite completely, removing any existing
  features (`A=B|C=D` + `C=E|X=Y` &rarr; `C=E|X=Y`)
- `overwrite=False, extend=True`: keep values of existing features, add any new
  features (`A=B|C=D` + `C=E|X=Y` &rarr; `A=B|C=D|X=Y`)
- `overwrite=False, extend=False`: do not modify the existing annotation if set
  (`A=B|C=D` + `C=E|X=Y` &rarr; `A=B|C=D`)

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> morphologizer = nlp.add_pipe("morphologizer")
>
> # Construction via create_pipe with custom model
> config = {"model": {"@architectures": "my_morphologizer"}}
> morphologizer = nlp.add_pipe("morphologizer", config=config)
>
> # Construction from class
> from spacy.pipeline import Morphologizer
> morphologizer = Morphologizer(nlp.vocab, model)
> ```

| Name                                     | Description                                                                                                                                                                                                                                                            |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`                                  | The shared vocabulary. ~~Vocab~~                                                                                                                                                                                                                                       |
| `model`                                  | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                   |
| `name`                                   | String name of the component instance. Used to add entries to the `losses` during training. ~~str~~                                                                                                                                                                    |
| _keyword-only_                           |                                                                                                                                                                                                                                                                        |
| `overwrite` <Tag variant="new">3.2</Tag> | Whether the values of existing features are overwritten. Defaults to `True`. ~~bool~~                                                                                                                                                                                  |
| `extend` <Tag variant="new">3.2</Tag>    | Whether existing feature types (whose values may or may not be overwritten depending on `overwrite`) are preserved. Defaults to `False`. ~~bool~~                                                                                                                      |
| `scorer` <Tag variant="new">3.2</Tag>    | The scoring method. Defaults to [`Scorer.score_token_attr`](/api/scorer#score_token_attr) for the attributes `"pos"` and `"morph"` and [`Scorer.score_token_attr_per_feat`](/api/scorer#score_token_attr_per_feat) for the attribute `"morph"`. ~~Optional[Callable]~~ |

## Morphologizer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/morphologizer#call) and [`pipe`](/api/morphologizer#pipe)
delegate to the [`predict`](/api/morphologizer#predict) and
[`set_annotations`](/api/morphologizer#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> morphologizer = nlp.add_pipe("morphologizer")
> # This usually happens under the hood
> processed = morphologizer(doc)
> ```

| Name        | Description                      |
| ----------- | -------------------------------- |
| `doc`       | The document to process. ~~Doc~~ |
| **RETURNS** | The processed document. ~~Doc~~  |

## Morphologizer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/morphologizer#call) and
[`pipe`](/api/morphologizer#pipe) delegate to the
[`predict`](/api/morphologizer#predict) and
[`set_annotations`](/api/morphologizer#set_annotations) methods.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> for doc in morphologizer.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `stream`       | A stream of documents. ~~Iterable[Doc]~~                      |
| _keyword-only_ |                                                               |
| `batch_size`   | The number of documents to buffer. Defaults to `128`. ~~int~~ |
| **YIELDS**     | The processed documents in order. ~~Doc~~                     |

## Morphologizer.initialize {#initialize tag="method"}

Initialize the component for training. `get_examples` should be a function that
returns an iterable of [`Example`](/api/example) objects. The data examples are
used to **initialize the model** of the component and can either be the full
training data or a representative sample. Initialization includes validating the
network,
[inferring missing shapes](https://thinc.ai/docs/usage-models#validation) and
setting up the label scheme based on the data. This method is typically called
by [`Language.initialize`](/api/language#initialize) and lets you customize
arguments it receives via the
[`[initialize.components]`](/api/data-formats#config-initialize) block in the
config.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer.initialize(lambda: [], nlp=nlp)
> ```
>
> ```ini
> ### config.cfg
> [initialize.components.morphologizer]
>
> [initialize.components.morphologizer.labels]
> @readers = "spacy.read_labels.v1"
> path = "corpus/labels/morphologizer.json
> ```

| Name           | Description                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. ~~Callable[[], Iterable[Example]]~~                                                                                                                                                                                                                                                             |
| _keyword-only_ |                                                                                                                                                                                                                                                                                                                                                                                                   |
| `nlp`          | The current `nlp` object. Defaults to `None`. ~~Optional[Language]~~                                                                                                                                                                                                                                                                                                                              |
| `labels`       | The label information to add to the component, as provided by the [`label_data`](#label_data) property after initialization. To generate a reusable JSON file from your data, you should run the [`init labels`](/api/cli#init-labels) command. If no labels are provided, the `get_examples` callback is used to extract the labels from the data, which may be a lot slower. ~~Optional[dict]~~ |

## Morphologizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> scores = morphologizer.predict([doc1, doc2])
> ```

| Name        | Description                                 |
| ----------- | ------------------------------------------- |
| `docs`      | The documents to predict. ~~Iterable[Doc]~~ |
| **RETURNS** | The model's prediction for each document.   |

## Morphologizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects, using pre-computed scores.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> scores = morphologizer.predict([doc1, doc2])
> morphologizer.set_annotations([doc1, doc2], scores)
> ```

| Name     | Description                                             |
| -------- | ------------------------------------------------------- |
| `docs`   | The documents to modify. ~~Iterable[Doc]~~              |
| `scores` | The scores to set, produced by `Morphologizer.predict`. |

## Morphologizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects containing the
predictions and gold-standard annotations, and update the component's model.
Delegates to [`predict`](/api/morphologizer#predict) and
[`get_loss`](/api/morphologizer#get_loss).

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> optimizer = nlp.initialize()
> losses = morphologizer.update(examples, sgd=optimizer)
> ```

| Name           | Description                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `examples`     | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                        |
| _keyword-only_ |                                                                                                                          |
| `drop`         | The dropout rate. ~~float~~                                                                                              |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~            |
| `losses`       | Optional record of the loss during training. Updated using the component name as the key. ~~Optional[Dict[str, float]]~~ |
| **RETURNS**    | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                    |

## Morphologizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> scores = morphologizer.predict([eg.predicted for eg in examples])
> loss, d_loss = morphologizer.get_loss(examples, scores)
> ```

| Name        | Description                                                                 |
| ----------- | --------------------------------------------------------------------------- |
| `examples`  | The batch of examples. ~~Iterable[Example]~~                                |
| `scores`    | Scores representing the model's predictions.                                |
| **RETURNS** | The loss and the gradient, i.e. `(loss, gradient)`. ~~Tuple[float, float]~~ |

## Morphologizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> optimizer = morphologizer.create_optimizer()
> ```

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The optimizer. ~~Optimizer~~ |

## Morphologizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> with morphologizer.use_params(optimizer.averages):
>     morphologizer.to_disk("/best_model")
> ```

| Name     | Description                                        |
| -------- | -------------------------------------------------- |
| `params` | The parameter values to use in the model. ~~dict~~ |

## Morphologizer.add_label {#add_label tag="method"}

Add a new label to the pipe. If the `Morphologizer` should set annotations for
both `pos` and `morph`, the label should include the UPOS as the feature `POS`.
Raises an error if the output dimension is already set, or if the model has
already been fully [initialized](#initialize). Note that you don't have to call
this method if you provide a **representative data sample** to the
[`initialize`](#initialize) method. In this case, all labels found in the sample
will be automatically added to the model, and the output dimension will be
[inferred](/usage/layers-architectures#thinc-shape-inference) automatically.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer.add_label("Mood=Ind|POS=VERB|Tense=Past|VerbForm=Fin")
> ```

| Name        | Description                                                 |
| ----------- | ----------------------------------------------------------- |
| `label`     | The label to add. ~~str~~                                   |
| **RETURNS** | `0` if the label is already present, otherwise `1`. ~~int~~ |

## Morphologizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer.to_disk("/path/to/morphologizer")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## Morphologizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer.from_disk("/path/to/morphologizer")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `Morphologizer` object. ~~Morphologizer~~                                          |

## Morphologizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer_bytes = morphologizer.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The serialized form of the `Morphologizer` object. ~~bytes~~                                |

## Morphologizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> morphologizer_bytes = morphologizer.to_bytes()
> morphologizer = nlp.add_pipe("morphologizer")
> morphologizer.from_bytes(morphologizer_bytes)
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                            |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `Morphologizer` object. ~~Morphologizer~~                                               |

## Morphologizer.labels {#labels tag="property"}

The labels currently added to the component in the Universal Dependencies
[FEATS](https://universaldependencies.org/format.html#morphological-annotation)
format. Note that even for a blank component, this will always include the
internal empty label `_`. If POS features are used, the labels will include the
coarse-grained POS as the feature `POS`.

> #### Example
>
> ```python
> morphologizer.add_label("Mood=Ind|POS=VERB|Tense=Past|VerbForm=Fin")
> assert "Mood=Ind|POS=VERB|Tense=Past|VerbForm=Fin" in morphologizer.labels
> ```

| Name        | Description                                            |
| ----------- | ------------------------------------------------------ |
| **RETURNS** | The labels added to the component. ~~Tuple[str, ...]~~ |

## Morphologizer.label_data {#label_data tag="property" new="3"}

The labels currently added to the component and their internal meta information.
This is the data generated by [`init labels`](/api/cli#init-labels) and used by
[`Morphologizer.initialize`](/api/morphologizer#initialize) to initialize the
model with a pre-defined label set.

> #### Example
>
> ```python
> labels = morphologizer.label_data
> morphologizer.initialize(lambda: [], nlp=nlp, labels=labels)
> ```

| Name        | Description                                     |
| ----------- | ----------------------------------------------- |
| **RETURNS** | The label data added to the component. ~~dict~~ |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = morphologizer.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
