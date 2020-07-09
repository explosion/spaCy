---
title: Model Architectures
teaser: Pre-defined model architectures included with the core library
source: spacy/ml/models
---

TODO: intro and how architectures work, link to
[`registry`](/api/top-level#registry),
[custom models](/usage/training#custom-models) usage etc.

## Parser architectures {source="spacy/ml/models/parser.py"}

### spacy.TransitionBasedParser.v1

<!-- TODO: intro -->

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
