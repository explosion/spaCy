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

This pipeline component lets you use transformer models in your pipeline. The
component assigns the output of the transformer to the Doc's extension
attributes. We also calculate an alignment between the word-piece tokens and the
spaCy tokenization, so that we can use the last hidden states to set the
`Doc.tensor` attribute. When multiple word-piece tokens align to the same spaCy
token, the spaCy token receives the sum of their values. To access the values,
you can use the custom [`Doc._.trf_data`](#custom-attributes) attribute. For
more details, see the [usage documentation](/usage/transformers).

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

| Setting             | Type                                       | Description                     | Default                                                             |
| ------------------- | ------------------------------------------ | ------------------------------- | ------------------------------------------------------------------- |
| `max_batch_items`   | int                                        | Maximum size of a padded batch. | `4096`                                                              |
| `annotation_setter` | Callable                                   | <!-- TODO: -->                  | [`null_annotation_setter`](/api/transformer#null_annotation_setter) |
| `model`             | [`Model`](https://thinc.ai/docs/api-model) | The model to use.               | [TransformerModel](/api/architectures#TransformerModel)             |

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
> # Construction via add_pipe with custom model
> config = {"model": {"@architectures": "my_transformer"}}
> trf = nlp.add_pipe("transformer", config=config)
>
> # Construction from class
> from spacy_transformers import Transformer
> trf = Transformer(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#create_pipe).

| Name                | Type                                       | Description                                                                                 |
| ------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `vocab`             | `Vocab`                                    | The shared vocabulary.                                                                      |
| `model`             | [`Model`](https://thinc.ai/docs/api-model) | The Thinc [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.       |
| `annotation_setter` | `Callable`                                 | <!-- TODO: -->                                                                              |
| _keyword-only_      |                                            |                                                                                             |
| `name`              | str                                        | String name of the component instance. Used to add entries to the `losses` during training. |
| `max_batch_items`   | int                                        | Maximum size of a padded batch. Defaults to `128*32`.                                       |

<!-- TODO: document rest -->

## TransformerData {#transformerdata tag="dataclass"}

## FullTransformerBatch {#fulltransformerbatch tag="dataclass"}

## Custom attributes {#custom-attributes}

The component sets the following
[custom extension attributes](/usage/processing-pipeline#custom-components-attributes):

| Name           | Type              | Description    |
| -------------- | ----------------- | -------------- |
| `Doc.trf_data` | `TransformerData` | <!-- TODO: --> |
