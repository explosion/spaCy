---
title: Model Architectures
teaser: Pre-defined model architectures included with the core library
source: spacy/ml/models
menu:
  - ['Tok2Vec', 'tok2vec']
  - ['Transformers', 'transformers']
  - ['Parser & NER', 'parser']
  - ['Text Classification', 'textcat']
  - ['Entity Linking', 'entitylinker']
---

TODO: intro and how architectures work, link to
[`registry`](/api/top-level#registry),
[custom models](/usage/training#custom-models) usage etc.

## Tok2Vec architectures {#tok2vec source="spacy/ml/models/tok2vec.py"}

### spacy.HashEmbedCNN.v1 {#HashEmbedCNN}

### spacy.HashCharEmbedCNN.v1 {#HashCharEmbedCNN}

### spacy.HashCharEmbedBiLSTM.v1 {#HashCharEmbedBiLSTM}

## Transformer architectures {#transformers source="github.com/explosion/spacy-transformers/blob/master/spacy_transformers/architectures.py"}

The following architectures are provided by the package
[`spacy-transformers`](https://github.com/explosion/spacy-transformers). See the
[usage documentation](/usage/transformers) for how to integrate the
architectures into your training config.

### spacy-transformers.TransformerModel.v1 {#TransformerModel}

<!-- TODO: description -->

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy-transformers.TransformerModel.v1"
> name = "roberta-base"
> tokenizer_config = {"use_fast": true}
>
> [model.get_spans]
> @span_getters = "strided_spans.v1"
> window = 128
> stride = 96
> ```

| Name               | Type             | Description                                                                                                                                                                                                     |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`             | str              | Any model name that can be loaded by [`transformers.AutoModel`](https://huggingface.co/transformers/model_doc/auto.html#transformers.AutoModel).                                                                |
| `get_spans`        | `Callable`       | Function that takes a batch of [`Doc`](/api/doc) object and returns lists of [`Span`](/api) objects to process by the transformer. [See here](/api/transformer#span_getters) for built-in options and examples. |
| `tokenizer_config` | `Dict[str, Any]` | Tokenizer settings passed to [`transformers.AutoTokenizer`](https://huggingface.co/transformers/model_doc/auto.html#transformers.AutoTokenizer).                                                                |

### spacy-transformers.Tok2VecListener.v1 {#Tok2VecListener}

<!-- TODO: description -->

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy-transformers.Tok2VecListener.v1"
> grad_factor = 1.0
>
> [model.pooling]
> @layers = "reduce_mean.v1"
> ```

| Name          | Type                      | Description                                                                                    |
| ------------- | ------------------------- | ---------------------------------------------------------------------------------------------- |
| `grad_factor` | float                     | Factor for weighting the gradient if multiple components listen to the same transformer model. |
| `pooling`     | `Model[Ragged, Floats2d]` | Pooling layer to determine how the vector for each spaCy token will be computed.               |

## Parser & NER architectures {#parser source="spacy/ml/models/parser.py"}

### spacy.TransitionBasedParser.v1 {#TransitionBasedParser}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.TransitionBasedParser.v1"
> nr_feature_tokens = 6
> hidden_width = 64
> maxout_pieces = 2
>
> [model.tok2vec]
> # ...
> ```

| Name                | Type                                       | Description |
| ------------------- | ------------------------------------------ | ----------- |
| `tok2vec`           | [`Model`](https://thinc.ai/docs/api-model) |             |
| `nr_feature_tokens` | int                                        |             |
| `hidden_width`      | int                                        |             |
| `maxout_pieces`     | int                                        |             |
| `use_upper`         | bool                                       |             |
| `nO`                | int                                        |             |

## Text classification architectures {#textcat source="spacy/ml/models/textcat.py"}

### spacy.TextCatEnsemble.v1 {#TextCatEnsemble}

### spacy.TextCatBOW.v1 {#TextCatBOW}

### spacy.TextCatCNN.v1 {#TextCatCNN}

### spacy.TextCatLowData.v1 {#TextCatLowData}

## Entity linking architectures {#entitylinker source="spacy/ml/models/entity_linker.py"}

### spacy.EntityLinker.v1 {#EntityLinker}
