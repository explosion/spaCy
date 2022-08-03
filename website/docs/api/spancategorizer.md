---
title: SpanCategorizer
tag: class,experimental
source: spacy/pipeline/spancat.py
new: 3.1
teaser: 'Pipeline component for labeling potentially overlapping spans of text'
api_base_class: /api/pipe
api_string_name: spancat
api_trainable: true
---

A span categorizer consists of two parts: a [suggester function](#suggesters)
that proposes candidate spans, which may or may not overlap, and a labeler model
that predicts zero or more labels for each candidate.

Predicted spans will be saved in a [`SpanGroup`](/api/spangroup) on the doc.
Individual span scores can be found in `spangroup.attrs["scores"]`.

## Assigned Attributes {#assigned-attributes}

Predictions will be saved to `Doc.spans[spans_key]` as a
[`SpanGroup`](/api/spangroup). The scores for the spans in the `SpanGroup` will
be saved in `SpanGroup.attrs["scores"]`.

`spans_key` defaults to `"sc"`, but can be passed as a parameter.

| Location                               | Value                                                    |
| -------------------------------------- | -------------------------------------------------------- |
| `Doc.spans[spans_key]`                 | The annotated spans. ~~SpanGroup~~                       |
| `Doc.spans[spans_key].attrs["scores"]` | The score for each span in the `SpanGroup`. ~~Floats1d~~ |

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
> from spacy.pipeline.spancat import DEFAULT_SPANCAT_MODEL
> config = {
>     "threshold": 0.5,
>     "spans_key": "labeled_spans",
>     "max_positive": None,
>     "model": DEFAULT_SPANCAT_MODEL,
>     "suggester": {"@misc": "spacy.ngram_suggester.v1", "sizes": [1, 2, 3]},
> }
> nlp.add_pipe("spancat", config=config)
> ```

| Setting        | Description                                                                                                                                                                                                                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `suggester`    | A function that [suggests spans](#suggesters). Spans are returned as a ragged array with two integer columns, for the start and end positions. Defaults to [`ngram_suggester`](#ngram_suggester). ~~Callable[[Iterable[Doc], Optional[Ops]], Ragged]~~                                                  |
| `model`        | A model instance that is given a a list of documents and `(start, end)` indices representing candidate span offsets. The model predicts a probability for each category for each span. Defaults to [SpanCategorizer](/api/architectures#SpanCategorizer). ~~Model[Tuple[List[Doc], Ragged], Floats2d]~~ |
| `spans_key`    | Key of the [`Doc.spans`](/api/doc#spans) dict to save the spans under. During initialization and training, the component will look for spans on the reference document under the same key. Defaults to `"sc"`. ~~str~~                                                                                  |
| `threshold`    | Minimum probability to consider a prediction positive. Spans with a positive prediction will be saved on the Doc. Defaults to `0.5`. ~~float~~                                                                                                                                                          |
| `max_positive` | Maximum number of labels to consider positive per span. Defaults to `None`, indicating no limit. ~~Optional[int]~~                                                                                                                                                                                      |
| `scorer`       | The scoring method. Defaults to [`Scorer.score_spans`](/api/scorer#score_spans) for `Doc.spans[spans_key]` with overlapping spans allowed. ~~Optional[Callable]~~                                                                                                                                       |

```python
%%GITHUB_SPACY/spacy/pipeline/spancat.py
```

## SpanCategorizer.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> spancat = nlp.add_pipe("spancat")
>
> # Construction via add_pipe with custom model
> config = {"model": {"@architectures": "my_spancat"}}
> parser = nlp.add_pipe("spancat", config=config)
>
> # Construction from class
> from spacy.pipeline import SpanCategorizer
> spancat = SpanCategorizer(nlp.vocab, model, suggester)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#create_pipe).

| Name           | Description                                                                                                                                                                                                                          |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `vocab`        | The shared vocabulary. ~~Vocab~~                                                                                                                                                                                                     |
| `model`        | A model instance that is given a a list of documents and `(start, end)` indices representing candidate span offsets. The model predicts a probability for each category for each span. ~~Model[Tuple[List[Doc], Ragged], Floats2d]~~ |
| `suggester`    | A function that [suggests spans](#suggesters). Spans are returned as a ragged array with two integer columns, for the start and end positions. ~~Callable[[Iterable[Doc], Optional[Ops]], Ragged]~~                                  |
| `name`         | String name of the component instance. Used to add entries to the `losses` during training. ~~str~~                                                                                                                                  |
| _keyword-only_ |                                                                                                                                                                                                                                      |
| `spans_key`    | Key of the [`Doc.spans`](/api/doc#sans) dict to save the spans under. During initialization and training, the component will look for spans on the reference document under the same key. Defaults to `"sc"`. ~~str~~                |
| `threshold`    | Minimum probability to consider a prediction positive. Spans with a positive prediction will be saved on the Doc. Defaults to `0.5`. ~~float~~                                                                                       |
| `max_positive` | Maximum number of labels to consider positive per span. Defaults to `None`, indicating no limit. ~~Optional[int]~~                                                                                                                   |

## SpanCategorizer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/spancategorizer#call) and [`pipe`](/api/spancategorizer#pipe)
delegate to the [`predict`](/api/spancategorizer#predict) and
[`set_annotations`](/api/spancategorizer#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> spancat = nlp.add_pipe("spancat")
> # This usually happens under the hood
> processed = spancat(doc)
> ```

| Name        | Description                      |
| ----------- | -------------------------------- |
| `doc`       | The document to process. ~~Doc~~ |
| **RETURNS** | The processed document. ~~Doc~~  |

## SpanCategorizer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/spancategorizer#call) and
[`pipe`](/api/spancategorizer#pipe) delegate to the
[`predict`](/api/spancategorizer#predict) and
[`set_annotations`](/api/spancategorizer#set_annotations) methods.

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> for doc in spancat.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `stream`       | A stream of documents. ~~Iterable[Doc]~~                      |
| _keyword-only_ |                                                               |
| `batch_size`   | The number of documents to buffer. Defaults to `128`. ~~int~~ |
| **YIELDS**     | The processed documents in order. ~~Doc~~                     |

## SpanCategorizer.initialize {#initialize tag="method"}

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
> spancat = nlp.add_pipe("spancat")
> spancat.initialize(lambda: examples, nlp=nlp)
> ```
>
> ```ini
> ### config.cfg
> [initialize.components.spancat]
>
> [initialize.components.spancat.labels]
> @readers = "spacy.read_labels.v1"
> path = "corpus/labels/spancat.json
> ```

| Name           | Description                                                                                                                                                                                                                                                                                                                                                                                                |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. Must contain at least one `Example`. ~~Callable[[], Iterable[Example]]~~                                                                                                                                                                                                                                 |
| _keyword-only_ |                                                                                                                                                                                                                                                                                                                                                                                                            |
| `nlp`          | The current `nlp` object. Defaults to `None`. ~~Optional[Language]~~                                                                                                                                                                                                                                                                                                                                       |
| `labels`       | The label information to add to the component, as provided by the [`label_data`](#label_data) property after initialization. To generate a reusable JSON file from your data, you should run the [`init labels`](/api/cli#init-labels) command. If no labels are provided, the `get_examples` callback is used to extract the labels from the data, which may be a lot slower. ~~Optional[Iterable[str]]~~ |

## SpanCategorizer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects without
modifying them.

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> scores = spancat.predict([doc1, doc2])
> ```

| Name        | Description                                 |
| ----------- | ------------------------------------------- |
| `docs`      | The documents to predict. ~~Iterable[Doc]~~ |
| **RETURNS** | The model's prediction for each document.   |

## SpanCategorizer.set_annotations {#set_annotations tag="method"}

Modify a batch of [`Doc`](/api/doc) objects using pre-computed scores.

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> scores = spancat.predict(docs)
> spancat.set_annotations(docs, scores)
> ```

| Name     | Description                                               |
| -------- | --------------------------------------------------------- |
| `docs`   | The documents to modify. ~~Iterable[Doc]~~                |
| `scores` | The scores to set, produced by `SpanCategorizer.predict`. |

## SpanCategorizer.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects containing the
predictions and gold-standard annotations, and update the component's model.
Delegates to [`predict`](/api/spancategorizer#predict) and
[`get_loss`](/api/spancategorizer#get_loss).

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> optimizer = nlp.initialize()
> losses = spancat.update(examples, sgd=optimizer)
> ```

| Name           | Description                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `examples`     | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                        |
| _keyword-only_ |                                                                                                                          |
| `drop`         | The dropout rate. ~~float~~                                                                                              |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~            |
| `losses`       | Optional record of the loss during training. Updated using the component name as the key. ~~Optional[Dict[str, float]]~~ |
| **RETURNS**    | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                    |

## SpanCategorizer.set_candidates {#set_candidates tag="method", new="3.3"}

Use the suggester to add a list of [`Span`](/api/span) candidates to a list of
[`Doc`](/api/doc) objects. This method is intended to be used for debugging
purposes.

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> spancat.set_candidates(docs, "candidates")
> ```

| Name             | Description                                                          |
| ---------------- | -------------------------------------------------------------------- |
| `docs`           | The documents to modify. ~~Iterable[Doc]~~                           |
| `candidates_key` | Key of the Doc.spans dict to save the candidate spans under. ~~str~~ |

## SpanCategorizer.get_loss {#get_loss tag="method"}

Find the loss and gradient of loss for the batch of documents and their
predicted scores.

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> scores = spancat.predict([eg.predicted for eg in examples])
> loss, d_loss = spancat.get_loss(examples, scores)
> ```

| Name           | Description                                                                 |
| -------------- | --------------------------------------------------------------------------- |
| `examples`     | The batch of examples. ~~Iterable[Example]~~                                |
| `spans_scores` | Scores representing the model's predictions. ~~Tuple[Ragged, Floats2d]~~    |
| **RETURNS**    | The loss and the gradient, i.e. `(loss, gradient)`. ~~Tuple[float, float]~~ |

## SpanCategorizer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> optimizer = spancat.create_optimizer()
> ```

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The optimizer. ~~Optimizer~~ |

## SpanCategorizer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model to use the given parameter values.

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> with spancat.use_params(optimizer.averages):
>     spancat.to_disk("/best_model")
> ```

| Name     | Description                                        |
| -------- | -------------------------------------------------- |
| `params` | The parameter values to use in the model. ~~dict~~ |

## SpanCategorizer.add_label {#add_label tag="method"}

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
> spancat = nlp.add_pipe("spancat")
> spancat.add_label("MY_LABEL")
> ```

| Name        | Description                                                 |
| ----------- | ----------------------------------------------------------- |
| `label`     | The label to add. ~~str~~                                   |
| **RETURNS** | `0` if the label is already present, otherwise `1`. ~~int~~ |

## SpanCategorizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> spancat.to_disk("/path/to/spancat")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## SpanCategorizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> spancat.from_disk("/path/to/spancat")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `SpanCategorizer` object. ~~SpanCategorizer~~                                      |

## SpanCategorizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> spancat = nlp.add_pipe("spancat")
> spancat_bytes = spancat.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The serialized form of the `SpanCategorizer` object. ~~bytes~~                              |

## SpanCategorizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> spancat_bytes = spancat.to_bytes()
> spancat = nlp.add_pipe("spancat")
> spancat.from_bytes(spancat_bytes)
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                            |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `SpanCategorizer` object. ~~SpanCategorizer~~                                           |

## SpanCategorizer.labels {#labels tag="property"}

The labels currently added to the component.

> #### Example
>
> ```python
> spancat.add_label("MY_LABEL")
> assert "MY_LABEL" in spancat.labels
> ```

| Name        | Description                                            |
| ----------- | ------------------------------------------------------ |
| **RETURNS** | The labels added to the component. ~~Tuple[str, ...]~~ |

## SpanCategorizer.label_data {#label_data tag="property"}

The labels currently added to the component and their internal meta information.
This is the data generated by [`init labels`](/api/cli#init-labels) and used by
[`SpanCategorizer.initialize`](/api/spancategorizer#initialize) to initialize
the model with a pre-defined label set.

> #### Example
>
> ```python
> labels = spancat.label_data
> spancat.initialize(lambda: [], nlp=nlp, labels=labels)
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
> data = spancat.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |

## Suggesters {#suggesters tag="registered functions" source="spacy/pipeline/spancat.py"}

### spacy.ngram_suggester.v1 {#ngram_suggester}

> #### Example Config
>
> ```ini
> [components.spancat.suggester]
> @misc = "spacy.ngram_suggester.v1"
> sizes = [1, 2, 3]
> ```

Suggest all spans of the given lengths. Spans are returned as a ragged array of
integers. The array has two columns, indicating the start and end position.

| Name        | Description                                                                                                          |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| `sizes`     | The phrase lengths to suggest. For example, `[1, 2]` will suggest phrases consisting of 1 or 2 tokens. ~~List[int]~~ |
| **CREATES** | The suggester function. ~~Callable[[Iterable[Doc], Optional[Ops]], Ragged]~~                                         |

### spacy.ngram_range_suggester.v1 {#ngram_range_suggester}

> #### Example Config
>
> ```ini
> [components.spancat.suggester]
> @misc = "spacy.ngram_range_suggester.v1"
> min_size = 2
> max_size = 4
> ```

Suggest all spans of at least length `min_size` and at most length `max_size`
(both inclusive). Spans are returned as a ragged array of integers. The array
has two columns, indicating the start and end position.

| Name        | Description                                                                  |
| ----------- | ---------------------------------------------------------------------------- |
| `min_size`  | The minimal phrase lengths to suggest (inclusive). ~~[int]~~                 |
| `max_size`  | The maximal phrase lengths to suggest (exclusive). ~~[int]~~                 |
| **CREATES** | The suggester function. ~~Callable[[Iterable[Doc], Optional[Ops]], Ragged]~~ |
