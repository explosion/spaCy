---
title: Transformer
teaser: Pipeline component for multi-task learning with transformer models
tag: class
source: github.com/explosion/spacy-transformers/blob/master/spacy_transformers/pipeline_component.py
new: 3
api_base_class: /api/pipe
api_string_name: transformer
---

> #### Installation
>
> ```bash
> $ pip install spacy-transformers
> ```

<Infobox title="Important note" variant="warning">

This component is available via the extension package
[`spacy-transformers`](https://github.com/explosion/spacy-transformers). It
exposes the component via entry points, so if you have the package installed,
using `factory = "transformer"` in your
[training config](/usage/training#config) or `nlp.add_pipe("transformer")` will
work out-of-the-box.

</Infobox>

This pipeline component lets you use transformer models in your pipeline.
Supports all models that are available via the
[HuggingFace `transformers`](https://huggingface.co/transformers) library.
Usually you will connect subsequent components to the shared transformer using
the [TransformerListener](/api/architectures#TransformerListener) layer. This
works similarly to spaCy's [Tok2Vec](/api/tok2vec) component and
[Tok2VecListener](/api/architectures/Tok2VecListener) sublayer.

The component assigns the output of the transformer to the `Doc`'s extension
attributes. We also calculate an alignment between the word-piece tokens and the
spaCy tokenization, so that we can use the last hidden states to set the
`Doc.tensor` attribute. When multiple word-piece tokens align to the same spaCy
token, the spaCy token receives the sum of their values. To access the values,
you can use the custom [`Doc._.trf_data`](#custom-attributes) attribute. The
package also adds the function registries [`@span_getters`](#span_getters) and
[`@annotation_setters`](#annotation_setters) with several built-in registered
functions. For more details, see the [usage documentation](/usage/transformers).

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
> from spacy_transformers import Transformer, DEFAULT_CONFIG
>
> nlp.add_pipe("transformer", config=DEFAULT_CONFIG)
> ```

| Setting             | Type                                       | Description                                                                                                                                                                                                                                                                                     | Default                                                 |
| ------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `max_batch_items`   | int                                        | Maximum size of a padded batch.                                                                                                                                                                                                                                                                 | `4096`                                                  |
| `annotation_setter` | Callable                                   | Function that takes a batch of `Doc` objects and a [`FullTransformerBatch`](/api/transformer#fulltransformerbatch) and can set additional annotations on the `Doc`. The `Doc._.transformer_data` attribute is set prior to calling the callback. By default, no additional annotations are set. | `null_annotation_setter`                                |
| `model`             | [`Model`](https://thinc.ai/docs/api-model) | **Input:** `List[Doc]`. **Output:** [`FullTransformerBatch`](/api/transformer#fulltransformerbatch). The Thinc [`Model`](https://thinc.ai/docs/api-model) wrapping the transformer.                                                                                                             | [TransformerModel](/api/architectures#TransformerModel) |

```python
https://github.com/explosion/spacy-transformers/blob/master/spacy_transformers/pipeline_component.py
```

## Transformer.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> trf = nlp.add_pipe("transformer")
>
> # Construction via add_pipe with custom config
> config = {
>     "model": {
>         "@architectures": "spacy-transformers.TransformerModel.v1",
>         "name": "bert-base-uncased",
>         "tokenizer_config": {"use_fast": True}
>     }
> }
> trf = nlp.add_pipe("transformer", config=config)
>
> # Construction from class
> from spacy_transformers import Transformer
> trf = Transformer(nlp.vocab, model)
> ```

Construct a `Transformer` component. One or more subsequent spaCy components can
use the transformer outputs as features in its model, with gradients
backpropagated to the single shared weights. The activations from the
transformer are saved in the [`Doc._.trf_data`](#custom-attributes) extension
attribute. You can also provide a callback to set additional annotations. In
your application, you would normally use a shortcut for this and instantiate the
component using its string name and [`nlp.add_pipe`](/api/language#create_pipe).

| Name                | Type                                       | Description                                                                                                                                                                                                                                                                                     |
| ------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`             | `Vocab`                                    | The shared vocabulary.                                                                                                                                                                                                                                                                          |
| `model`             | [`Model`](https://thinc.ai/docs/api-model) | **Input:** `List[Doc]`. **Output:** [`FullTransformerBatch`](/api/transformer#fulltransformerbatch). The Thinc [`Model`](https://thinc.ai/docs/api-model) wrapping the transformer. Usually you will want to use the [TransformerModel](/api/architectures#TransformerModel) layer for this.    |
| `annotation_setter` | `Callable`                                 | Function that takes a batch of `Doc` objects and a [`FullTransformerBatch`](/api/transformer#fulltransformerbatch) and can set additional annotations on the `Doc`. The `Doc._.transformer_data` attribute is set prior to calling the callback. By default, no additional annotations are set. |
| _keyword-only_      |                                            |                                                                                                                                                                                                                                                                                                 |
| `name`              | str                                        | String name of the component instance. Used to add entries to the `losses` during training.                                                                                                                                                                                                     |
| `max_batch_items`   | int                                        | Maximum size of a padded batch. Defaults to `128*32`.                                                                                                                                                                                                                                           |

## Transformer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/transformer#call) and [`pipe`](/api/transformer#pipe) delegate
to the [`predict`](/api/transformer#predict) and
[`set_annotations`](/api/transformer#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> trf = nlp.add_pipe("transformer")
> # This usually happens under the hood
> processed = transformer(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## Transformer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/transformer#call) and
[`pipe`](/api/transformer#pipe) delegate to the
[`predict`](/api/transformer#predict) and
[`set_annotations`](/api/transformer#set_annotations) methods.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> for doc in trf.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                           |
| -------------- | --------------- | ----------------------------------------------------- |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                |
| _keyword-only_ |                 |                                                       |
| `batch_size`   | int             | The number of documents to buffer. Defaults to `128`. |
| **YIELDS**     | `Doc`           | The processed documents in order.                     |

## Transformer.begin_training {#begin_training tag="method"}

Initialize the pipe for training, using data examples if available. Returns an
[`Optimizer`](https://thinc.ai/docs/api-optimizers) object.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> optimizer = trf.begin_training(pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                    |
| -------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects.     |
| _keyword-only_ |                                                     |                                                                                                                |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                           |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/transformer#create_optimizer) if not set. |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                 |

## Transformer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> scores = trf.predict([doc1, doc2])
> ```

| Name        | Type            | Description                               |
| ----------- | --------------- | ----------------------------------------- |
| `docs`      | `Iterable[Doc]` | The documents to predict.                 |
| **RETURNS** | -               | The model's prediction for each document. |

## Transformer.set_annotations {#set_annotations tag="method"}

Assign the extracted features to the Doc objects. By default, the
[`TransformerData`](/api/transformer#transformerdata) object is written to the
[`Doc._.trf_data`](#custom-attributes) attribute. Your annotation_setter
callback is then called, if provided.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> scores = trf.predict(docs)
> trf.set_annotations(docs, scores)
> ```

| Name     | Type            | Description                                           |
| -------- | --------------- | ----------------------------------------------------- |
| `docs`   | `Iterable[Doc]` | The documents to modify.                              |
| `scores` | -               | The scores to set, produced by `Transformer.predict`. |

## Transformer.update {#update tag="method"}

Prepare for an update to the transformer. Like the [`Tok2Vec`](/api/tok2vec)
component, the `Transformer` component is unusual in that it does not receive
"gold standard" annotations to calculate a weight update. The optimal output of
the transformer data is unknown – it's a hidden layer inside the network that is
updated by backpropagating from output layers.

The `Transformer` component therefore does **not** perform a weight update
during its own `update` method. Instead, it runs its transformer model and
communicates the output and the backpropagation callback to any **downstream
components** that have been connected to it via the
[TransformerListener](/api/architectures#TransformerListener) sublayer. If there
are multiple listeners, the last layer will actually backprop to the transformer
and call the optimizer, while the others simply increment the gradients.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> optimizer = nlp.begin_training()
> losses = trf.update(examples, sgd=optimizer)
> ```

| Name              | Type                                                | Description                                                                                                                                                |
| ----------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects. Only the [`Example.predicted`](/api/example#predicted) `Doc` object is used, the reference `Doc` is ignored. |
| _keyword-only_    |                                                     |                                                                                                                                                            |
| `drop`            | float                                               | The dropout rate.                                                                                                                                          |
| `set_annotations` | bool                                                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/transformer#set_annotations).                  |
| `sgd`             | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                                                             |
| `losses`          | `Dict[str, float]`                                  | Optional record of the loss during training. Updated using the component name as the key.                                                                  |
| **RETURNS**       | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                                                                                           |

## Transformer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> optimizer = trf.create_optimizer()
> ```

| Name        | Type                                                | Description    |
| ----------- | --------------------------------------------------- | -------------- |
| **RETURNS** | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer. |

## Transformer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> with trf.use_params(optimizer.averages):
>     trf.to_disk("/best_model")
> ```

| Name     | Type | Description                               |
| -------- | ---- | ----------------------------------------- |
| `params` | dict | The parameter values to use in the model. |

## Transformer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> trf.to_disk("/path/to/transformer")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## Transformer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> trf.from_disk("/path/to/transformer")
> ```

| Name           | Type            | Description                                                                |
| -------------- | --------------- | -------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                            |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `Tok2Vec`       | The modified `Tok2Vec` object.                                             |

## Transformer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> trf_bytes = trf.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the `Tok2Vec` object.                              |

## Transformer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> trf_bytes = trf.to_bytes()
> trf = nlp.add_pipe("transformer")
> trf.from_bytes(trf_bytes)
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
> data = trf.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |

## TransformerData {#transformerdata tag="dataclass"}

Transformer tokens and outputs for one `Doc` object.

<!-- TODO: finish API docs, also mention "width" is property -->

| Name      | Type                                               | Description |
| --------- | -------------------------------------------------- | ----------- |
| `tokens`  | `Dict`                                             |             |
| `tensors` | `List[FloatsXd]`                                   |             |
| `align`   | [`Ragged`](https://thinc.ai/docs/api-types#ragged) |             |
| `width`   | int                                                |             |

### TransformerData.empty {#transformerdata-emoty tag="classmethod"}

<!-- TODO: finish API docs -->

| Name        | Type              | Description |
| ----------- | ----------------- | ----------- |
| **RETURNS** | `TransformerData` |             |

## FullTransformerBatch {#fulltransformerbatch tag="dataclass"}

<!-- TODO: write, also mention doc_data is property -->

| Name       | Type                                                                                                                       | Description |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `spans`    | `List[List[Span]]`                                                                                                         |             |
| `tokens`   | [`transformers.BatchEncoding`](https://huggingface.co/transformers/main_classes/tokenizer.html#transformers.BatchEncoding) |             |
| `tensors`  | `List[torch.Tensor]`                                                                                                       |             |
| `align`    | [`Ragged`](https://thinc.ai/docs/api-types#ragged)                                                                         |             |
| `doc_data` | `List[TransformerData]`                                                                                                    |             |

### FullTransformerBatch.unsplit_by_doc {#fulltransformerbatch-unsplit_by_doc tag="method"}

<!-- TODO: write -->

| Name        | Type                   | Description |
| ----------- | ---------------------- | ----------- |
| `arrays`    | `List[List[Floats3d]]` |             |
| **RETURNS** | `FullTransformerBatch` |             |

### FullTransformerBatch.split_by_doc {#fulltransformerbatch-split_by_doc tag="method"}

Split a `TransformerData` object that represents a batch into a list with one
`TransformerData` per `Doc`.

| Name        | Type                    | Description |
| ----------- | ----------------------- | ----------- |
| **RETURNS** | `List[TransformerData]` |             |

## Span getters {#span_getters source="github.com/explosion/spacy-transformers/blob/master/spacy_transformers/span_getters.py"}

Span getters are functions that take a batch of [`Doc`](/api/doc) objects and
return a lists of [`Span`](/api/span) objects for each doc, to be processed by
the transformer. This is used to manage long documents, by cutting them into
smaller sequences before running the transformer. The spans are allowed to
overlap, and you can also omit sections of the Doc if they are not relevant.

Span getters can be referenced in the `[components.transformer.model.get_spans]`
block of the config to customize the sequences processed by the transformer. You
can also register custom span getters using the `@spacy.registry.span_getters`
decorator.

> #### Example
>
> ```python
> @spacy.registry.span_getters("sent_spans.v1")
> def configure_get_sent_spans() -> Callable:
>     def get_sent_spans(docs: Iterable[Doc]) -> List[List[Span]]:
>         return [list(doc.sents) for doc in docs]
>
>     return get_sent_spans
> ```

| Name        | Type               | Description                              |
| ----------- | ------------------ | ---------------------------------------- |
| `docs`      | `Iterable[Doc]`    | A batch of `Doc` objects.                |
| **RETURNS** | `List[List[Span]]` | The spans to process by the transformer. |

### doc_spans.v1 {#doc_spans tag="registered function"}

> #### Example config
>
> ```ini
> [transformer.model.get_spans]
> @span_getters = "doc_spans.v1"
> ```

Create a span getter that uses the whole document as its spans. This is the best
approach if your [`Doc`](/api/doc) objects already refer to relatively short
texts.

### sent_spans.v1 {#sent_spans tag="registered function"}

> #### Example config
>
> ```ini
> [transformer.model.get_spans]
> @span_getters = "sent_spans.v1"
> ```

Create a span getter that uses sentence boundary markers to extract the spans.
This requires sentence boundaries to be set (e.g. by the
[`Sentencizer`](/api/sentencizer)), and may result in somewhat uneven batches,
depending on the sentence lengths. However, it does provide the transformer with
more meaningful windows to attend over.

### strided_spans.v1 {#strided_spans tag="registered function"}

> #### Example config
>
> ```ini
> [transformer.model.get_spans]
> @span_getters = "strided_spans.v1"
> window = 128
> stride = 96
> ```

Create a span getter for strided spans. If you set the `window` and `stride` to
the same value, the spans will cover each token once. Setting `stride` lower
than `window` will allow for an overlap, so that some tokens are counted twice.
This can be desirable, because it allows all tokens to have both a left and
right context.

| Name      | Type | Description      |
| --------- | ---- | ---------------- |
|  `window` | int  | The window size. |
| `stride`  | int  | The stride size. |

## Annotation setters {#annotation_setters tag="registered functions" source="github.com/explosion/spacy-transformers/blob/master/spacy_transformers/annotation_setters.py"}

Annotation setters are functions that that take a batch of `Doc` objects and a
[`FullTransformerBatch`](/api/transformer#fulltransformerbatch) and can set
additional annotations on the `Doc`, e.g. to set custom or built-in attributes.
You can register custom annotation setters using the
`@registry.annotation_setters` decorator.

> #### Example
>
> ```python
> @registry.annotation_setters("spacy-transformer.null_annotation_setter.v1")
> def configure_null_annotation_setter() -> Callable:
>     def setter(docs: List[Doc], trf_data: FullTransformerBatch) -> None:
>         pass
>
>     return setter
> ```

| Name       | Type                   | Description                          |
| ---------- | ---------------------- | ------------------------------------ |
| `docs`     | `List[Doc]`            | A batch of `Doc` objects.            |
| `trf_data` | `FullTransformerBatch` | The transformers data for the batch. |

The following built-in functions are available:

| Name                                          | Description                           |
| --------------------------------------------- | ------------------------------------- |
| `spacy-transformer.null_annotation_setter.v1` | Don't set any additional annotations. |

## Custom attributes {#custom-attributes}

The component sets the following
[custom extension attributes](/usage/processing-pipeline#custom-components-attributes):

| Name           | Type                                                  | Description                                          |
| -------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| `Doc.trf_data` | [`TransformerData`](/api/transformer#transformerdata) | Transformer tokens and outputs for the `Doc` object. |
