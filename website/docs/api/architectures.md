---
title: Model Architectures
teaser: Pre-defined model architectures included with the core library
source: spacy/ml/models
menu:
  - ['Tok2Vec', 'tok2vec']
  - ['Parser & NER', 'parser']
  - ['Text Classification', 'textcat']
  - ['Entity Linking', 'entitylinker']
---

TODO: intro and how architectures work, link to
[`registry`](/api/top-level#registry),
[custom models](/usage/training#custom-models) usage etc.

## Tok2Vec architectures {#tok2vec source="spacy/ml/models/tok2vec.py"}}

### spacy.HashEmbedCNN.v1 {#HashEmbedCNN}

### spacy.HashCharEmbedCNN.v1 {#HashCharEmbedCNN}

### spacy.HashCharEmbedBiLSTM.v1 {#HashCharEmbedBiLSTM}

## Parser & NER architectures {#parser source="spacy/ml/models/parser.py"}

### spacy.TransitionBasedParser.v1 {#TransitionBasedParser}

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

## Text classification architectures {#textcat source="spacy/ml/models/textcat.py"}

### spacy.TextCatEnsemble.v1 {#TextCatEnsemble}

### spacy.TextCatBOW.v1 {#TextCatBOW}

### spacy.TextCatCNN.v1 {#TextCatCNN}

### spacy.TextCatLowData.v1 {#TextCatLowData}

## Entity linking architectures {#entitylinker source="spacy/ml/models/entity_linker.py"}

### spacy.EntityLinker.v1 {#EntityLinker}
