---
title: Model Architectures
teaser: Pre-defined model architectures included with the core library
source: spacy/ml/models
menu:
  - ['Tok2Vec', 'tok2vec']
  - ['Transformers', 'transformers']
  - ['Parser & NER', 'parser']
  - ['Tagging', 'tagger']
  - ['Text Classification', 'textcat']
  - ['Entity Linking', 'entitylinker']
---

TODO: intro and how architectures work, link to
[`registry`](/api/top-level#registry),
[custom models](/usage/training#custom-models) usage etc.

## Tok2Vec architectures {#tok2vec source="spacy/ml/models/tok2vec.py"}

### spacy.HashEmbedCNN.v1 {#HashEmbedCNN}

<!-- TODO: intro -->

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.HashEmbedCNN.v1"
> # TODO: ...
>
> [model.tok2vec]
> # ...
> ```

| Name                 | Type  | Description |
| -------------------- | ----- | ----------- |
| `width`              | int   |             |
| `depth`              | int   |             |
| `embed_size`         | int   |             |
| `window_size`        | int   |             |
| `maxout_pieces`      | int   |             |
| `subword_features`   | bool  |             |
| `dropout`            | float |             |
| `pretrained_vectors` | bool  |             |

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

## Tagging architectures {#tagger source="spacy/ml/models/tagger.py"}

### spacy.Tagger.v1 {#Tagger}

<!-- TODO: intro -->

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.Tagger.v1"
> nO = null
>
> [model.tok2vec]
> # ...
> ```

| Name      | Type                                       | Description |
| --------- | ------------------------------------------ | ----------- |
| `tok2vec` | [`Model`](https://thinc.ai/docs/api-model) |             |
| `nO`      | int                                        |             |

## Text classification architectures {#textcat source="spacy/ml/models/textcat.py"}

### spacy.TextCatEnsemble.v1 {#TextCatEnsemble}

### spacy.TextCatBOW.v1 {#TextCatBOW}

### spacy.TextCatCNN.v1 {#TextCatCNN}

### spacy.TextCatLowData.v1 {#TextCatLowData}

## Entity linking architectures {#entitylinker source="spacy/ml/models/entity_linker.py"}

An Entity Linker component disambiguates textual mentions (tagged as named
entities) to unique identifiers, grounding the named entities into the "real
world". This requires 3 main components:

- A [`KnowledgeBase`](/api/kb) (KB) holding the unique identifiers, potential
  synonyms and prior probabilities.
- A candidate generation step to produce a set of likely identifiers, given a
  certain textual mention.
- A Machine learning [`Model`](https://thinc.ai/docs/api-model) that picks the
  most plausible ID from the set of candidates.

### spacy.EntityLinker.v1 {#EntityLinker}

The `EntityLinker` model architecture is a `Thinc` `Model` with a Linear output
layer.

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.EntityLinker.v1"
> nO = null
>
> [model.tok2vec]
> @architectures = "spacy.HashEmbedCNN.v1"
> pretrained_vectors = null
> width = 96
> depth = 2
> embed_size = 300
> window_size = 1
> maxout_pieces = 3
> subword_features = true
> dropout = null
> 
> [kb_loader]
> @assets = "spacy.EmptyKB.v1"
> entity_vector_length = 64
> 
> [get_candidates]
> @assets = "spacy.CandidateGenerator.v1"
> ```

| Name      | Type                                       | Description                                                                              |
| --------- | ------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `tok2vec` | [`Model`](https://thinc.ai/docs/api-model) | The [`tok2vec`](#tok2vec) layer of the model.                                            |
| `nO`      | int                                        | Output dimension, determined by the length of the vectors encoding each entity in the KB |

If the `nO` dimension is not set, the Entity Linking component will set it when
`begin_training` is called.

### spacy.EmptyKB.v1 {#EmptyKB}

A function that creates a default, empty Knowledge Base from a [`Vocab`](/api/vocab) instance.

| Name                   | Type | Description                                              |
| ---------------------- | ---- | -------------------------------------------------------- |
| `entity_vector_length` | int  | The length of the vectors encoding each entity in the KB - 64 by default. |

### spacy.CandidateGenerator.v1 {#CandidateGenerator}

A function that takes as input a [`KnowledgeBase`](/api/kb) and a [`Span`](/api/span) object denoting a
named entity, and returns a list of plausible
[`Candidate` objects](/api/kb/#candidate_init).

The default `CandidateGenerator` simply uses the text of a mention to find its
potential aliases in the Knowledgebase. Note that this function is
case-dependent.
