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

The text categorizer predicts **categories over a whole document**. and comes in
two flavors: `textcat` and `textcat_multilabel`. When you need to predict
exactly one true label per document, use the `textcat` which has mutually
exclusive labels. If you want to perform multi-label classification and predict
zero, one or more true labels per document, use the `textcat_multilabel`
component instead. For a binary classification task, you can use `textcat` with
**two** labels or `textcat_multilabel` with **one** label.

Both components are documented on this page.

<Infobox title="Migration from v2" variant="warning">

In spaCy v2, the `textcat` component could also perform **multi-label
classification**, and even used this setting by default. Since v3.0, the
component `textcat_multilabel` should be used for multi-label classification
instead. The `textcat` component is now used for mutually exclusive classes
only.

</Infobox>

## Assigned Attributes {#assigned-attributes}

Predictions will be saved to `doc.cats` as a dictionary, where the key is the
name of the category and the value is a score between 0 and 1 (inclusive). For
`textcat` (exclusive categories), the scores will sum to 1, while for
`textcat_multilabel` there is no particular guarantee about their sum.

Note that when assigning values to create training data, the score of each
category must be 0 or 1. Using other values, for example to create a document
that is a little bit in category A and a little bit in category B, is not
supported.

| Location   | Value                                 |
| ---------- | ------------------------------------- |
| `Doc.cats` | Category scores. ~~Dict[str, float]~~ |

## Config and implementation {#config}

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config). See the
[model architectures](/api/architectures) documentation for details on the
architectures and their arguments and hyperparameters.

> #### Example (textcat)
>
> ```python
> from spacy.pipeline.textcat import DEFAULT_SINGLE_TEXTCAT_MODEL
> config = {
>    "threshold": 0.5,
>    "model": DEFAULT_SINGLE_TEXTCAT_MODEL,
> }
> nlp.add_pipe("textcat", config=config)
> ```

> #### Example (textcat_multilabel)
>
> ```python
> from spacy.pipeline.textcat_multilabel import DEFAULT_MULTI_TEXTCAT_MODEL
> config = {
>    "threshold": 0.5,
>    "model": DEFAULT_MULTI_TEXTCAT_MODEL,
> }
> nlp.add_pipe("textcat_multilabel", config=config)
> ```

| Setting     | Description                                                                                                                                                      |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `threshold` | Cutoff to consider a prediction "positive", relevant when printing accuracy results. ~~float~~                                                                   |
| `model`     | A model instance that predicts scores for each category. Defaults to [TextCatEnsemble](/api/architectures#TextCatEnsemble). ~~Model[List[Doc], List[Floats2d]]~~ |

```python
%%GITHUB_SPACY/spacy/pipeline/textcat.py
```

```python
%%GITHUB_SPACY/spacy/pipeline/textcat_multilabel.py
```

## TextCategorizer.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> # Use 'textcat_multilabel' for multi-label classification
> textcat = nlp.add_pipe("textcat")
>
> # Construction via add_pipe with custom model
> config = {"model": {"@architectures": "my_textcat"}}
> parser = nlp.add_pipe("textcat", config=config)
>
> # Construction from class
> # Use 'MultiLabel_TextCategorizer' for multi-label classification
> from spacy.pipeline import TextCategorizer
> textcat = TextCategorizer(nlp.vocab, model, threshold=0.5)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#create_pipe).

| Name           | Description                                                                                                                      |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`        | The shared vocabulary. ~~Vocab~~                                                                                                 |
| `model`        | The Thinc [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. ~~Model[List[Doc], List[Floats2d]]~~       |
| `name`         | String name of the component instance. Used to add entries to the `losses` during training. ~~str~~                              |
| _keyword-only_ |                                                                                                                                  |
| `threshold`    | Cutoff to consider a prediction "positive", relevant when printing accuracy results. ~~float~~                                   |
| `scorer`       | The scoring method. Defaults to [`Scorer.score_cats`](/api/scorer#score_cats) for the attribute `"cats"`. ~~Optional[Callable]~~ |

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

| Name        | Description                      |
| ----------- | -------------------------------- |
| `doc`       | The document to process. ~~Doc~~ |
| **RETURNS** | The processed document. ~~Doc~~  |

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

| Name           | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `stream`       | A stream of documents. ~~Iterable[Doc]~~                      |
| _keyword-only_ |                                                               |
| `batch_size`   | The number of documents to buffer. Defaults to `128`. ~~int~~ |
| **YIELDS**     | The processed documents in order. ~~Doc~~                     |

## TextCategorizer.initialize {#initialize tag="method" new="3"}

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

<Infobox variant="warning" title="Changed in v3.0" id="begin_training">

This method was previously called `begin_training`.

</Infobox>

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> textcat.initialize(lambda: [], nlp=nlp)
> ```
>
> ```ini
> ### config.cfg
> [initialize.components.textcat]
> positive_label = "POS"
>
> [initialize.components.textcat.labels]
> @readers = "spacy.read_labels.v1"
> path = "corpus/labels/textcat.json
> ```

| Name             | Description                                                                                                                                                                                                                                                                                                                                                                                                |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples`   | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. ~~Callable[[], Iterable[Example]]~~                                                                                                                                                                                                                                                                      |
| _keyword-only_   |                                                                                                                                                                                                                                                                                                                                                                                                            |
| `nlp`            | The current `nlp` object. Defaults to `None`. ~~Optional[Language]~~                                                                                                                                                                                                                                                                                                                                       |
| `labels`         | The label information to add to the component, as provided by the [`label_data`](#label_data) property after initialization. To generate a reusable JSON file from your data, you should run the [`init labels`](/api/cli#init-labels) command. If no labels are provided, the `get_examples` callback is used to extract the labels from the data, which may be a lot slower. ~~Optional[Iterable[str]]~~ |
| `positive_label` | The positive label for a binary task with exclusive classes, `None` otherwise and by default. This parameter is only used during scoring. It is not available when using the `textcat_multilabel` component. ~~Optional[str]~~                                                                                                                                                                             |

## TextCategorizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects without
modifying them.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> scores = textcat.predict([doc1, doc2])
> ```

| Name        | Description                                 |
| ----------- | ------------------------------------------- |
| `docs`      | The documents to predict. ~~Iterable[Doc]~~ |
| **RETURNS** | The model's prediction for each document.   |

## TextCategorizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects using pre-computed scores.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> scores = textcat.predict(docs)
> textcat.set_annotations(docs, scores)
> ```

| Name     | Description                                               |
| -------- | --------------------------------------------------------- |
| `docs`   | The documents to modify. ~~Iterable[Doc]~~                |
| `scores` | The scores to set, produced by `TextCategorizer.predict`. |

## TextCategorizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects containing the
predictions and gold-standard annotations, and update the component's model.
Delegates to [`predict`](/api/textcategorizer#predict) and
[`get_loss`](/api/textcategorizer#get_loss).

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> optimizer = nlp.initialize()
> losses = textcat.update(examples, sgd=optimizer)
> ```

| Name           | Description                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `examples`     | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                        |
| _keyword-only_ |                                                                                                                          |
| `drop`         | The dropout rate. ~~float~~                                                                                              |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~            |
| `losses`       | Optional record of the loss during training. Updated using the component name as the key. ~~Optional[Dict[str, float]]~~ |
| **RETURNS**    | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                    |

## TextCategorizer.rehearse {#rehearse tag="method,experimental" new="3"}

Perform a "rehearsal" update from a batch of data. Rehearsal updates teach the
current model to make predictions similar to an initial model to try to address
the "catastrophic forgetting" problem. This feature is experimental.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> optimizer = nlp.resume_training()
> losses = textcat.rehearse(examples, sgd=optimizer)
> ```

| Name           | Description                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `examples`     | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                        |
| _keyword-only_ |                                                                                                                          |
| `drop`         | The dropout rate. ~~float~~                                                                                              |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~            |
| `losses`       | Optional record of the loss during training. Updated using the component name as the key. ~~Optional[Dict[str, float]]~~ |
| **RETURNS**    | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                    |

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

| Name        | Description                                                                 |
| ----------- | --------------------------------------------------------------------------- |
| `examples`  | The batch of examples. ~~Iterable[Example]~~                                |
| `scores`    | Scores representing the model's predictions.                                |
| **RETURNS** | The loss and the gradient, i.e. `(loss, gradient)`. ~~Tuple[float, float]~~ |

## TextCategorizer.score {#score tag="method" new="3"}

Score a batch of examples.

> #### Example
>
> ```python
> scores = textcat.score(examples)
> ```

| Name           | Description                                                                                                          |
| -------------- | -------------------------------------------------------------------------------------------------------------------- |
| `examples`     | The examples to score. ~~Iterable[Example]~~                                                                         |
| _keyword-only_ |                                                                                                                      |
| **RETURNS**    | The scores, produced by [`Scorer.score_cats`](/api/scorer#score_cats). ~~Dict[str, Union[float, Dict[str, float]]]~~ |

## TextCategorizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> optimizer = textcat.create_optimizer()
> ```

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The optimizer. ~~Optimizer~~ |

## TextCategorizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model to use the given parameter values.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> with textcat.use_params(optimizer.averages):
>     textcat.to_disk("/best_model")
> ```

| Name     | Description                                        |
| -------- | -------------------------------------------------- |
| `params` | The parameter values to use in the model. ~~dict~~ |

## TextCategorizer.add_label {#add_label tag="method"}

Add a new label to the pipe. Raises an error if the output dimension is already
set, or if the model has already been fully [initialized](#initialize). Note
that you don't have to call this method if you provide a **representative data
sample** to the [`initialize`](#initialize) method. In this case, all labels
found in the sample will be automatically added to the model, and the output
dimension will be [inferred](/usage/layers-architectures#thinc-shape-inference)
automatically.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> textcat.add_label("MY_LABEL")
> ```

| Name        | Description                                                 |
| ----------- | ----------------------------------------------------------- |
| `label`     | The label to add. ~~str~~                                   |
| **RETURNS** | `0` if the label is already present, otherwise `1`. ~~int~~ |

## TextCategorizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> textcat.to_disk("/path/to/textcat")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## TextCategorizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> textcat.from_disk("/path/to/textcat")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `TextCategorizer` object. ~~TextCategorizer~~                                      |

## TextCategorizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> textcat = nlp.add_pipe("textcat")
> textcat_bytes = textcat.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The serialized form of the `TextCategorizer` object. ~~bytes~~                              |

## TextCategorizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> textcat_bytes = textcat.to_bytes()
> textcat = nlp.add_pipe("textcat")
> textcat.from_bytes(textcat_bytes)
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                            |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `TextCategorizer` object. ~~TextCategorizer~~                                           |

## TextCategorizer.labels {#labels tag="property"}

The labels currently added to the component.

> #### Example
>
> ```python
> textcat.add_label("MY_LABEL")
> assert "MY_LABEL" in textcat.labels
> ```

| Name        | Description                                            |
| ----------- | ------------------------------------------------------ |
| **RETURNS** | The labels added to the component. ~~Tuple[str, ...]~~ |

## TextCategorizer.label_data {#label_data tag="property" new="3"}

The labels currently added to the component and their internal meta information.
This is the data generated by [`init labels`](/api/cli#init-labels) and used by
[`TextCategorizer.initialize`](/api/textcategorizer#initialize) to initialize
the model with a pre-defined label set.

> #### Example
>
> ```python
> labels = textcat.label_data
> textcat.initialize(lambda: [], nlp=nlp, labels=labels)
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
> data = textcat.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
