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
> $ pip install -U %%SPACY_PKG_NAME[transformers] %%SPACY_PKG_FLAGS
> ```

<Infobox title="Important note" variant="warning">

This component is available via the extension package
[`spacy-transformers`](https://github.com/explosion/spacy-transformers). It
exposes the component via entry points, so if you have the package installed,
using `factory = "transformer"` in your
[training config](/usage/training#config) or `nlp.add_pipe("transformer")` will
work out-of-the-box.

</Infobox>

This pipeline component lets you use transformer models in your pipeline. It
supports all models that are available via the
[HuggingFace `transformers`](https://huggingface.co/transformers) library.
Usually you will connect subsequent components to the shared transformer using
the [TransformerListener](/api/architectures#TransformerListener) layer. This
works similarly to spaCy's [Tok2Vec](/api/tok2vec) component and
[Tok2VecListener](/api/architectures/#Tok2VecListener) sublayer.

The component assigns the output of the transformer to the `Doc`'s extension
attributes. We also calculate an alignment between the word-piece tokens and the
spaCy tokenization, so that we can use the last hidden states to set the
`Doc.tensor` attribute. When multiple word-piece tokens align to the same spaCy
token, the spaCy token receives the sum of their values. To access the values,
you can use the custom [`Doc._.trf_data`](#assigned-attributes) attribute. The
package also adds the function registries [`@span_getters`](#span_getters) and
[`@annotation_setters`](#annotation_setters) with several built-in registered
functions. For more details, see the
[usage documentation](/usage/embeddings-transformers).

## Assigned Attributes {#assigned-attributes}

The component sets the following
[custom extension attribute](/usage/processing-pipeline#custom-components-attributes):

| Location         | Value                                                                    |
| ---------------- | ------------------------------------------------------------------------ |
| `Doc._.trf_data` | Transformer tokens and outputs for the `Doc` object. ~~TransformerData~~ |

## Config and implementation {#config}

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config). See the
[model architectures](/api/architectures#transformers) documentation for details
on the transformer architectures and their arguments and hyperparameters.

> #### Example
>
> ```python
> from spacy_transformers import Transformer
> from spacy_transformers.pipeline_component import DEFAULT_CONFIG
>
> nlp.add_pipe("transformer", config=DEFAULT_CONFIG["transformer"])
> ```

| Setting                 | Description                                                                                                                                                                                                                                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `max_batch_items`       | Maximum size of a padded batch. Defaults to `4096`. ~~int~~                                                                                                                                                                                                                                                   |
| `set_extra_annotations` | Function that takes a batch of `Doc` objects and transformer outputs to set additional annotations on the `Doc`. The `Doc._.trf_data` attribute is set prior to calling the callback. Defaults to `null_annotation_setter` (no additional annotations). ~~Callable[[List[Doc], FullTransformerBatch], None]~~ |
| `model`                 | The Thinc [`Model`](https://thinc.ai/docs/api-model) wrapping the transformer. Defaults to [TransformerModel](/api/architectures#TransformerModel). ~~Model[List[Doc], FullTransformerBatch]~~                                                                                                                |

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
>         "@architectures": "spacy-transformers.TransformerModel.v3",
>         "name": "bert-base-uncased",
>         "tokenizer_config": {"use_fast": True},
>         "transformer_config": {"output_attentions": True},
>         "mixed_precision": True,
>         "grad_scaler_config": {"init_scale": 32768}
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
transformer are saved in the [`Doc._.trf_data`](#assigned-attributes) extension
attribute. You can also provide a callback to set additional annotations. In
your application, you would normally use a shortcut for this and instantiate the
component using its string name and [`nlp.add_pipe`](/api/language#create_pipe).

| Name                    | Description                                                                                                                                                                                                                                                                             |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`                 | The shared vocabulary. ~~Vocab~~                                                                                                                                                                                                                                                        |
| `model`                 | The Thinc [`Model`](https://thinc.ai/docs/api-model) wrapping the transformer. Usually you will want to use the [TransformerModel](/api/architectures#TransformerModel) layer for this. ~~Model[List[Doc], FullTransformerBatch]~~                                                      |
| `set_extra_annotations` | Function that takes a batch of `Doc` objects and transformer outputs and stores the annotations on the `Doc`. The `Doc._.trf_data` attribute is set prior to calling the callback. By default, no additional annotations are set. ~~Callable[[List[Doc], FullTransformerBatch], None]~~ |
| _keyword-only_          |                                                                                                                                                                                                                                                                                         |
| `name`                  | String name of the component instance. Used to add entries to the `losses` during training. ~~str~~                                                                                                                                                                                     |
| `max_batch_items`       | Maximum size of a padded batch. Defaults to `128*32`. ~~int~~                                                                                                                                                                                                                           |

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

| Name        | Description                      |
| ----------- | -------------------------------- |
| `doc`       | The document to process. ~~Doc~~ |
| **RETURNS** | The processed document. ~~Doc~~  |

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

| Name           | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `stream`       | A stream of documents. ~~Iterable[Doc]~~                      |
| _keyword-only_ |                                                               |
| `batch_size`   | The number of documents to buffer. Defaults to `128`. ~~int~~ |
| **YIELDS**     | The processed documents in order. ~~Doc~~                     |

## Transformer.initialize {#initialize tag="method"}

Initialize the component for training and return an
[`Optimizer`](https://thinc.ai/docs/api-optimizers). `get_examples` should be a
function that returns an iterable of [`Example`](/api/example) objects. **At
least one example should be supplied.** The data examples are used to
**initialize the model** of the component and can either be the full training
data or a representative sample. Initialization includes validating the network,
[inferring missing shapes](https://thinc.ai/docs/usage-models#validation) and
setting up the label scheme based on the data. This method is typically called
by [`Language.initialize`](/api/language#initialize).

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> trf.initialize(lambda: examples, nlp=nlp)
> ```

| Name           | Description                                                                                                                                                                |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. Must contain at least one `Example`. ~~Callable[[], Iterable[Example]]~~ |
| _keyword-only_ |                                                                                                                                                                            |
| `nlp`          | The current `nlp` object. Defaults to `None`. ~~Optional[Language]~~                                                                                                       |

## Transformer.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects without
modifying them.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> scores = trf.predict([doc1, doc2])
> ```

| Name        | Description                                 |
| ----------- | ------------------------------------------- |
| `docs`      | The documents to predict. ~~Iterable[Doc]~~ |
| **RETURNS** | The model's prediction for each document.   |

## Transformer.set_annotations {#set_annotations tag="method"}

Assign the extracted features to the `Doc` objects. By default, the
[`TransformerData`](/api/transformer#transformerdata) object is written to the
[`Doc._.trf_data`](#assigned-attributes) attribute. Your `set_extra_annotations`
callback is then called, if provided.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> scores = trf.predict(docs)
> trf.set_annotations(docs, scores)
> ```

| Name     | Description                                           |
| -------- | ----------------------------------------------------- |
| `docs`   | The documents to modify. ~~Iterable[Doc]~~            |
| `scores` | The scores to set, produced by `Transformer.predict`. |

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
> optimizer = nlp.initialize()
> losses = trf.update(examples, sgd=optimizer)
> ```

| Name           | Description                                                                                                                                                                      |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`     | A batch of [`Example`](/api/example) objects. Only the [`Example.predicted`](/api/example#predicted) `Doc` object is used, the reference `Doc` is ignored. ~~Iterable[Example]~~ |
| _keyword-only_ |                                                                                                                                                                                  |
| `drop`         | The dropout rate. ~~float~~                                                                                                                                                      |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~                                                                    |
| `losses`       | Optional record of the loss during training. Updated using the component name as the key. ~~Optional[Dict[str, float]]~~                                                         |
| **RETURNS**    | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                                                                            |

## Transformer.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> optimizer = trf.create_optimizer()
> ```

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The optimizer. ~~Optimizer~~ |

## Transformer.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> with trf.use_params(optimizer.averages):
>     trf.to_disk("/best_model")
> ```

| Name     | Description                                        |
| -------- | -------------------------------------------------- |
| `params` | The parameter values to use in the model. ~~dict~~ |

## Transformer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> trf.to_disk("/path/to/transformer")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## Transformer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> trf.from_disk("/path/to/transformer")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `Transformer` object. ~~Transformer~~                                              |

## Transformer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> trf = nlp.add_pipe("transformer")
> trf_bytes = trf.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The serialized form of the `Transformer` object. ~~bytes~~                                  |

## Transformer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> trf_bytes = trf.to_bytes()
> trf = nlp.add_pipe("transformer")
> trf.from_bytes(trf_bytes)
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                            |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `Transformer` object. ~~Transformer~~                                                   |

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

Transformer tokens and outputs for one `Doc` object. The transformer models
return tensors that refer to a whole padded batch of documents. These tensors
are wrapped into the
[FullTransformerBatch](/api/transformer#fulltransformerbatch) object. The
`FullTransformerBatch` then splits out the per-document data, which is handled
by this class. Instances of this class are typically assigned to the
[`Doc._.trf_data`](/api/transformer#assigned-attributes) extension attribute.

| Name           | Description                                                                                                                                                                                                                                                                                                                          |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `tokens`       | A slice of the tokens data produced by the tokenizer. This may have several fields, including the token IDs, the texts and the attention mask. See the [`transformers.BatchEncoding`](https://huggingface.co/transformers/main_classes/tokenizer.html#transformers.BatchEncoding) object for details. ~~dict~~                       |
| `model_output` | The model output from the transformer model, determined by the model and transformer config. New in `spacy-transformers` v1.1.0. ~~transformers.file_utils.ModelOutput~~                                                                                                                                                             |
| `tensors`      | The `model_output` in the earlier `transformers` tuple format converted using [`ModelOutput.to_tuple()`](https://huggingface.co/transformers/main_classes/output.html#transformers.file_utils.ModelOutput.to_tuple). Returns `Tuple` instead of `List` as of `spacy-transformers` v1.1.0. ~~Tuple[Union[FloatsXd, List[FloatsXd]]]~~ |
| `align`        | Alignment from the `Doc`'s tokenization to the wordpieces. This is a ragged array, where `align.lengths[i]` indicates the number of wordpiece tokens that token `i` aligns against. The actual indices are provided at `align[i].dataXd`. ~~Ragged~~                                                                                 |
| `width`        | The width of the last hidden layer. ~~int~~                                                                                                                                                                                                                                                                                          |

### TransformerData.empty {#transformerdata-emoty tag="classmethod"}

Create an empty `TransformerData` container.

| Name        | Description                        |
| ----------- | ---------------------------------- |
| **RETURNS** | The container. ~~TransformerData~~ |

<Accordion title="Previous versions of TransformerData" spaced>

In `spacy-transformers` v1.0, the model output is stored in
`TransformerData.tensors` as `List[Union[FloatsXd]]` and only includes the
activations for the `Doc` from the transformer. Usually the last tensor that is
3-dimensional will be the most important, as that will provide the final hidden
state. Generally activations that are 2-dimensional will be attention weights.
Details of this variable will differ depending on the underlying transformer
model.

</Accordion>

## FullTransformerBatch {#fulltransformerbatch tag="dataclass"}

Holds a batch of input and output objects for a transformer model. The data can
then be split to a list of [`TransformerData`](/api/transformer#transformerdata)
objects to associate the outputs to each [`Doc`](/api/doc) in the batch.

| Name           | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `spans`        | The batch of input spans. The outer list refers to the Doc objects in the batch, and the inner list are the spans for that `Doc`. Note that spans are allowed to overlap or exclude tokens, but each `Span` can only refer to one `Doc` (by definition). This means that within a `Doc`, the regions of the output tensors that correspond to each `Span` may overlap or have gaps, but for each `Doc`, there is a non-overlapping contiguous slice of the outputs. ~~List[List[Span]]~~ |
| `tokens`       | The output of the tokenizer. ~~transformers.BatchEncoding~~                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `model_output` | The model output from the transformer model, determined by the model and transformer config. New in `spacy-transformers` v1.1.0. ~~transformers.file_utils.ModelOutput~~                                                                                                                                                                                                                                                                                                                 |
| `tensors`      | The `model_output` in the earlier `transformers` tuple format converted using [`ModelOutput.to_tuple()`](https://huggingface.co/transformers/main_classes/output.html#transformers.file_utils.ModelOutput.to_tuple). Returns `Tuple` instead of `List` as of `spacy-transformers` v1.1.0. ~~Tuple[Union[torch.Tensor, Tuple[torch.Tensor]]]~~                                                                                                                                            |
| `align`        | Alignment from the spaCy tokenization to the wordpieces. This is a ragged array, where `align.lengths[i]` indicates the number of wordpiece tokens that token `i` aligns against. The actual indices are provided at `align[i].dataXd`. ~~Ragged~~                                                                                                                                                                                                                                       |
| `doc_data`     | The outputs, split per `Doc` object. ~~List[TransformerData]~~                                                                                                                                                                                                                                                                                                                                                                                                                           |

### FullTransformerBatch.unsplit_by_doc {#fulltransformerbatch-unsplit_by_doc tag="method"}

Return a new `FullTransformerBatch` from a split batch of activations, using the
current object's spans, tokens and alignment. This is used during the backward
pass, in order to construct the gradients to pass back into the transformer
model.

| Name        | Description                                              |
| ----------- | -------------------------------------------------------- |
| `arrays`    | The split batch of activations. ~~List[List[Floats3d]]~~ |
| **RETURNS** | The transformer batch. ~~FullTransformerBatch~~          |

### FullTransformerBatch.split_by_doc {#fulltransformerbatch-split_by_doc tag="method"}

Split a `TransformerData` object that represents a batch into a list with one
`TransformerData` per `Doc`.

| Name        | Description                                |
| ----------- | ------------------------------------------ |
| **RETURNS** | The split batch. ~~List[TransformerData]~~ |

<Accordion title="Previous versions of FullTransformerBatch" spaced>

In `spacy-transformers` v1.0, the model output is stored in
`FullTransformerBatch.tensors` as `List[torch.Tensor]`.

</Accordion>

## Span getters {#span_getters source="github.com/explosion/spacy-transformers/blob/master/spacy_transformers/span_getters.py"}

Span getters are functions that take a batch of [`Doc`](/api/doc) objects and
return a lists of [`Span`](/api/span) objects for each doc to be processed by
the transformer. This is used to manage long documents by cutting them into
smaller sequences before running the transformer. The spans are allowed to
overlap, and you can also omit sections of the `Doc` if they are not relevant.

Span getters can be referenced in the `[components.transformer.model.get_spans]`
block of the config to customize the sequences processed by the transformer. You
can also register
[custom span getters](/usage/embeddings-transformers#transformers-training-custom-settings)
using the `@spacy.registry.span_getters` decorator.

> #### Example
>
> ```python
> @spacy.registry.span_getters("custom_sent_spans")
> def configure_get_sent_spans() -> Callable:
>     def get_sent_spans(docs: Iterable[Doc]) -> List[List[Span]]:
>         return [list(doc.sents) for doc in docs]
>
>     return get_sent_spans
> ```

| Name        | Description                                                   |
| ----------- | ------------------------------------------------------------- |
| `docs`      | A batch of `Doc` objects. ~~Iterable[Doc]~~                   |
| **RETURNS** | The spans to process by the transformer. ~~List[List[Span]]~~ |

### doc_spans.v1 {#doc_spans tag="registered function"}

> #### Example config
>
> ```ini
> [transformer.model.get_spans]
> @span_getters = "spacy-transformers.doc_spans.v1"
> ```

Create a span getter that uses the whole document as its spans. This is the best
approach if your [`Doc`](/api/doc) objects already refer to relatively short
texts.

### sent_spans.v1 {#sent_spans tag="registered function"}

> #### Example config
>
> ```ini
> [transformer.model.get_spans]
> @span_getters = "spacy-transformers.sent_spans.v1"
> ```

Create a span getter that uses sentence boundary markers to extract the spans.
This requires sentence boundaries to be set (e.g. by the
[`Sentencizer`](/api/sentencizer)), and may result in somewhat uneven batches,
depending on the sentence lengths. However, it does provide the transformer with
more meaningful windows to attend over.

To set sentence boundaries with the `sentencizer` during training, add a
`sentencizer` to the beginning of the pipeline and include it in
[`[training.annotating_components]`](/usage/training#annotating-components) to
have it set the sentence boundaries before the `transformer` component runs.

### strided_spans.v1 {#strided_spans tag="registered function"}

> #### Example config
>
> ```ini
> [transformer.model.get_spans]
> @span_getters = "spacy-transformers.strided_spans.v1"
> window = 128
> stride = 96
> ```

Create a span getter for strided spans. If you set the `window` and `stride` to
the same value, the spans will cover each token once. Setting `stride` lower
than `window` will allow for an overlap, so that some tokens are counted twice.
This can be desirable, because it allows all tokens to have both a left and
right context.

| Name     | Description              |
| -------- | ------------------------ |
| `window` | The window size. ~~int~~ |
| `stride` | The stride size. ~~int~~ |

## Annotation setters {#annotation_setters tag="registered functions" source="github.com/explosion/spacy-transformers/blob/master/spacy_transformers/annotation_setters.py"}

Annotation setters are functions that take a batch of `Doc` objects and a
[`FullTransformerBatch`](/api/transformer#fulltransformerbatch) and can set
additional annotations on the `Doc`, e.g. to set custom or built-in attributes.
You can register custom annotation setters using the
`@registry.annotation_setters` decorator.

> #### Example
>
> ```python
> @registry.annotation_setters("spacy-transformers.null_annotation_setter.v1")
> def configure_null_annotation_setter() -> Callable:
>     def setter(docs: List[Doc], trf_data: FullTransformerBatch) -> None:
>         pass
>
>     return setter
> ```

| Name       | Description                                                   |
| ---------- | ------------------------------------------------------------- |
| `docs`     | A batch of `Doc` objects. ~~List[Doc]~~                       |
| `trf_data` | The transformers data for the batch. ~~FullTransformerBatch~~ |

The following built-in functions are available:

| Name                                           | Description                           |
| ---------------------------------------------- | ------------------------------------- |
| `spacy-transformers.null_annotation_setter.v1` | Don't set any additional annotations. |
