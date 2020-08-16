---
title: Model Architectures
teaser: Pre-defined model architectures included with the core library
source: spacy/ml/models
menu:
  - ['Tok2Vec', 'tok2vec-arch']
  - ['Transformers', 'transformers']
  - ['Parser & NER', 'parser']
  - ['Tagging', 'tagger']
  - ['Text Classification', 'textcat']
  - ['Entity Linking', 'entitylinker']
---

TODO: intro and how architectures work, link to
[`registry`](/api/top-level#registry),
[custom models](/usage/training#custom-models) usage etc.

## Tok2Vec architectures {#tok2vec-arch source="spacy/ml/models/tok2vec.py"}

### spacy.HashEmbedCNN.v1 {#HashEmbedCNN}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.HashEmbedCNN.v1"
> pretrained_vectors = null
> width = 96
> depth = 4
> embed_size = 2000
> window_size = 1
> maxout_pieces = 3
> subword_features = true
> ```

Build spaCy's 'standard' tok2vec layer, which uses hash embedding with subword
features and a CNN with layer-normalized maxout.

| Name                 | Type | Description                                                                                                                                                                                                                                                           |
| -------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`              | int  | The width of the input and output. These are required to be the same, so that residual connections can be used. Recommended values are `96`, `128` or `300`.                                                                                                          |
| `depth`              | int  | The number of convolutional layers to use. Recommended values are between `2` and `8`.                                                                                                                                                                                |
| `embed_size`         | int  | The number of rows in the hash embedding tables. This can be surprisingly small, due to the use of the hash embeddings. Recommended values are between `2000` and `10000`.                                                                                            |
| `window_size`        | int  | The number of tokens on either side to concatenate during the convolutions. The receptive field of the CNN will be `depth * (window_size * 2 + 1)`, so a 4-layer network with a window size of `2` will be sensitive to 17 words at a time. Recommended value is `1`. |
| `maxout_pieces`      | int  | The number of pieces to use in the maxout non-linearity. If `1`, the [`Mish`](https://thinc.ai/docs/api-layers#mish) non-linearity is used instead. Recommended values are `1`-`3`.                                                                                   |
| `subword_features`   | bool | Whether to also embed subword features, specifically the prefix, suffix and word shape. This is recommended for alphabetic languages like English, but not if single-character tokens are used for a language such as Chinese.                                        |
| `pretrained_vectors` | bool | Whether to also use static vectors.                                                                                                                                                                                                                                   |

### spacy.Tok2Vec.v1 {#Tok2Vec}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.Tok2Vec.v1"
>
> [model.embed]
> @architectures = "spacy.CharacterEmbed.v1"
> # ...
>
> [model.encode]
> @architectures = "spacy.MaxoutWindowEncoder.v1"
> # ...
> ```

Construct a tok2vec model out of embedding and encoding subnetworks. See the
["Embed, Encode, Attend, Predict"](https://explosion.ai/blog/deep-learning-formula-nlp)
blog post for background.

| Name     | Type                                       | Description                                                                                                                                                                                                                                      |
| -------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `embed`  | [`Model`](https://thinc.ai/docs/api-model) | **Input:** `List[Doc]`. **Output:** `List[Floats2d]`. Embed tokens into context-independent word vector representations. For example, [CharacterEmbed](/api/architectures#CharacterEmbed) or [MultiHashEmbed](/api/architectures#MultiHashEmbed) |
| `encode` | [`Model`](https://thinc.ai/docs/api-model) | **Input:** `List[Floats2d]`. **Output:** `List[Floats2d]`. Encode context into the embeddings, using an architecture such as a CNN, BiLSTM or transformer. For example, [MaxoutWindowEncoder](/api/architectures#MaxoutWindowEncoder).           |

### spacy.Tok2VecListener.v1 {#Tok2VecListener}

> #### Example config
>
> ```ini
> [components.tok2vec]
> factory = "tok2vec"
>
> [components.tok2vec.model]
> @architectures = "spacy.HashEmbedCNN.v1"
> width = 342
>
> [components.tagger]
> factory = "tagger"
>
> [components.tagger.model]
> @architectures = "spacy.Tagger.v1"
>
> [components.tagger.model.tok2vec]
> @architectures = "spacy.Tok2VecListener.v1"
> width = ${components.tok2vec.model:width}
> ```

A listener is used as a sublayer within a component such as a
[`DependencyParser`](/api/dependencyparser),
[`EntityRecognizer`](/api/entityrecognizer)or
[`TextCategorizer`](/api/textcategorizer). Usually you'll have multiple
listeners connecting to a single upstream [`Tok2Vec`](/api/tok2vec) component
that's earlier in the pipeline. The listener layers act as **proxies**, passing
the predictions from the `Tok2Vec` component into downstream components, and
communicating gradients back upstream.

Instead of defining its own `Tok2Vec` instance, a model architecture like
[Tagger](/api/architectures#tagger) can define a listener as its `tok2vec`
argument that connects to the shared `tok2vec` component in the pipeline.

| Name       | Type | Description                                                                                                                                                                                                                                                                                            |
| ---------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `width`    | int  | The width of the vectors produced by the "upstream" [`Tok2Vec`](/api/tok2vec) component.                                                                                                                                                                                                               |
| `upstream` | str  | A string to identify the "upstream" `Tok2Vec` component to communicate with. The upstream name should either be the wildcard string `"*"`, or the name of the `Tok2Vec` component. You'll almost never have multiple upstream `Tok2Vec` components, so the wildcard string will almost always be fine. |

### spacy.MultiHashEmbed.v1 {#MultiHashEmbed}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.MultiHashEmbed.v1"
> width = 64
> rows = 2000
> also_embed_subwords = false
> also_use_static_vectors = false
> ```

Construct an embedding layer that separately embeds a number of lexical
attributes using hash embedding, concatenates the results, and passes it through
a feed-forward subnetwork to build a mixed representations. The features used
are the `NORM`, `PREFIX`, `SUFFIX` and `SHAPE`, which can have varying
definitions depending on the `Vocab` of the `Doc` object passed in. Vectors from
pretrained static vectors can also be incorporated into the concatenated
representation.

| Name                      | Type | Description                                                                                                                                                                                               |
| ------------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`                   | int  | The output width. Also used as the width of the embedding tables. Recommended values are between `64` and `300`.                                                                                          |
| `rows`                    | int  | The number of rows for the embedding tables. Can be low, due to the hashing trick. Embeddings for prefix, suffix and word shape use half as many rows. Recommended values are between `2000` and `10000`. |
| `also_embed_subwords`     | bool | Whether to use the `PREFIX`, `SUFFIX` and `SHAPE` features in the embeddings. If not using these, you may need more rows in your hash embeddings, as there will be increased chance of collisions.        |
| `also_use_static_vectors` | bool | Whether to also use static word vectors. Requires a vectors table to be loaded in the [Doc](/api/doc) objects' vocab.                                                                                     |

### spacy.CharacterEmbed.v1 {#CharacterEmbed}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.CharacterEmbed.v1"
> width = 128
> rows = 7000
> nM = 64
> nC = 8
> ```

Construct an embedded representations based on character embeddings, using a
feed-forward network. A fixed number of UTF-8 byte characters are used for each
word, taken from the beginning and end of the word equally. Padding is used in
the center for words that are too short.

For instance, let's say `nC=4`, and the word is "jumping". The characters used
will be `"jung"` (two from the start, two from the end). If we had `nC=8`, the
characters would be `"jumpping"`: 4 from the start, 4 from the end. This ensures
that the final character is always in the last position, instead of being in an
arbitrary position depending on the word length.

The characters are embedded in a embedding table with 256 rows, and the vectors
concatenated. A hash-embedded vector of the `NORM` of the word is also
concatenated on, and the result is then passed through a feed-forward network to
construct a single vector to represent the information.

| Name    | Type | Description                                                                                                                                             |
| ------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width` | int  | The width of the output vector and the `NORM` hash embedding.                                                                                           |
| `rows`  | int  | The number of rows in the `NORM` hash embedding table.                                                                                                  |
| `nM`    | int  | The dimensionality of the character embeddings. Recommended values are between `16` and `64`.                                                           |
| `nC`    | int  | The number of UTF-8 bytes to embed per word. Recommended values are between `3` and `8`, although it may depend on the length of words in the language. |

### spacy.MaxoutWindowEncoder.v1 {#MaxoutWindowEncoder}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.MaxoutWindowEncoder.v1"
> width = 128
> window_size = 1
> maxout_pieces = 3
> depth = 4
> ```

Encode context using convolutions with maxout activation, layer normalization
and residual connections.

| Name            | Type | Description                                                                                                                                                                                            |
| --------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `width`         | int  | The input and output width. These are required to be the same, to allow residual connections. This value will be determined by the width of the inputs. Recommended values are between `64` and `300`. |
| `window_size`   | int  | The number of words to concatenate around each token to construct the convolution. Recommended value is `1`.                                                                                           |
| `maxout_pieces` | int  | The number of maxout pieces to use. Recommended values are `2` or `3`.                                                                                                                                 |
| `depth`         | int  | The number of convolutional layers. Recommended value is `4`.                                                                                                                                          |

### spacy.MishWindowEncoder.v1 {#MishWindowEncoder}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.MishWindowEncoder.v1"
> width = 64
> window_size = 1
> depth = 4
> ```

Encode context using convolutions with
[`Mish`](https://thinc.ai/docs/api-layers#mish) activation, layer normalization
and residual connections.

| Name          | Type | Description                                                                                                                                                                                            |
| ------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `width`       | int  | The input and output width. These are required to be the same, to allow residual connections. This value will be determined by the width of the inputs. Recommended values are between `64` and `300`. |
| `window_size` | int  | The number of words to concatenate around each token to construct the convolution. Recommended value is `1`.                                                                                           |
| `depth`       | int  | The number of convolutional layers. Recommended value is `4`.                                                                                                                                          |

### spacy.TorchBiLSTMEncoder.v1 {#TorchBiLSTMEncoder}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.TorchBiLSTMEncoder.v1"
> width = 64
> window_size = 1
> depth = 4
> ```

Encode context using bidirectional LSTM layers. Requires
[PyTorch](https://pytorch.org).

| Name          | Type | Description                                                                                                                                                                                            |
| ------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `width`       | int  | The input and output width. These are required to be the same, to allow residual connections. This value will be determined by the width of the inputs. Recommended values are between `64` and `300`. |
| `window_size` | int  | The number of words to concatenate around each token to construct the convolution. Recommended value is `1`.                                                                                           |
| `depth`       | int  | The number of convolutional layers. Recommended value is `4`.                                                                                                                                          |

## Transformer architectures {#transformers source="github.com/explosion/spacy-transformers/blob/master/spacy_transformers/architectures.py"}

The following architectures are provided by the package
[`spacy-transformers`](https://github.com/explosion/spacy-transformers). See the
[usage documentation](/usage/transformers) for how to integrate the
architectures into your training config.

### spacy-transformers.TransformerModel.v1 {#TransformerModel}

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

<!-- TODO: description -->

| Name               | Type             | Description                                                                                                                                                                                                     |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`             | str              | Any model name that can be loaded by [`transformers.AutoModel`](https://huggingface.co/transformers/model_doc/auto.html#transformers.AutoModel).                                                                |
| `get_spans`        | `Callable`       | Function that takes a batch of [`Doc`](/api/doc) object and returns lists of [`Span`](/api) objects to process by the transformer. [See here](/api/transformer#span_getters) for built-in options and examples. |
| `tokenizer_config` | `Dict[str, Any]` | Tokenizer settings passed to [`transformers.AutoTokenizer`](https://huggingface.co/transformers/model_doc/auto.html#transformers.AutoTokenizer).                                                                |

### spacy-transformers.Tok2VecListener.v1 {#transformers-Tok2VecListener}

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

Create a `TransformerListener` layer, which will connect to a
[`Transformer`](/api/transformer) component earlier in the pipeline. The layer
takes a list of [`Doc`](/api/doc) objects as input, and produces a list of
2-dimensional arrays as output, with each array having one row per token. Most
spaCy models expect a sublayer with this signature, making it easy to connect
them to a transformer model via this sublayer. Transformer models usually
operate over wordpieces, which usually don't align one-to-one against spaCy
tokens. The layer therefore requires a reduction operation in order to calculate
a single token vector given zero or more wordpiece vectors.

| Name          | Type                                       | Description                                                                                                                                                                                                                                                         |
| ------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pooling`     | [`Model`](https://thinc.ai/docs/api-model) | **Input:** [`Ragged`](https://thinc.ai/docs/api-types#ragged). **Output:** [`Floats2d`](https://thinc.ai/docs/api-types#types)                                                                                                                                      | A reduction layer used to calculate the token vectors based on zero or more wordpiece vectors. If in doubt, mean pooling (see [`reduce_mean`](https://thinc.ai/docs/api-layers#reduce_mean)) is usually a good choice. |
| `grad_factor` | float                                      | Reweight gradients from the component before passing them upstream. You can set this to `0` to "freeze" the transformer weights with respect to the component, or use it to make some components more significant than others. Leaving it at `1.0` is usually fine. |

### spacy-transformers.Tok2VecTransformer.v1 {#Tok2VecTransformer}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.Tok2VecTransformer.v1"
> name = "albert-base-v2"
> tokenizer_config = {"use_fast": false}
> grad_factor = 1.0
> ```

Use a transformer as a [`Tok2Vec`](/api/tok2vec) layer directly. This does
**not** allow multiple components to share the transformer weights, and does
**not** allow the transformer to set annotations into the [`Doc`](/api/doc)
object, but it's a **simpler solution** if you only need the transformer within
one component.

| Name               | Type                                       | Description                                                                                                                                                                                                                                                         |
| ------------------ | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_spans`        | callable                                   | Function that takes a batch of [`Doc`](/api/doc) object and returns lists of [`Span`](/api) objects to process by the transformer. [See here](/api/transformer#span_getters) for built-in options and examples.                                                     |
| `tokenizer_config` | `Dict[str, Any]`                           | Tokenizer settings passed to [`transformers.AutoTokenizer`](https://huggingface.co/transformers/model_doc/auto.html#transformers.AutoTokenizer).                                                                                                                    |
| `pooling`          | [`Model`](https://thinc.ai/docs/api-model) | **Input:** [`Ragged`](https://thinc.ai/docs/api-types#ragged). **Output:** [`Floats2d`](https://thinc.ai/docs/api-types#types)                                                                                                                                      | A reduction layer used to calculate the token vectors based on zero or more wordpiece vectors. If in doubt, mean pooling (see [`reduce_mean`](https://thinc.ai/docs/api-layers#reduce_mean)) is usually a good choice. |
| `grad_factor`      | float                                      | Reweight gradients from the component before passing them upstream. You can set this to `0` to "freeze" the transformer weights with respect to the component, or use it to make some components more significant than others. Leaving it at `1.0` is usually fine. |

## Parser & NER architectures {#parser}

### spacy.TransitionBasedParser.v1 {#TransitionBasedParser source="spacy/ml/models/parser.py"}

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
> @architectures = "spacy.HashEmbedCNN.v1"
> pretrained_vectors = null
> width = 96
> depth = 4
> embed_size = 2000
> window_size = 1
> maxout_pieces = 3
> subword_features = true
> ```

Build a transition-based parser model. Can apply to NER or dependency-parsing.
Transition-based parsing is an approach to structured prediction where the task
of predicting the structure is mapped to a series of state transitions. You
might find [this tutorial](https://explosion.ai/blog/parsing-english-in-python)
helpful for background information. The neural network state prediction model
consists of either two or three subnetworks:

- **tok2vec**: Map each token into a vector representations. This subnetwork is
  run once for each batch.
- **lower**: Construct a feature-specific vector for each `(token, feature)`
  pair. This is also run once for each batch. Constructing the state
  representation is then simply a matter of summing the component features and
  applying the non-linearity.
- **upper** (optional): A feed-forward network that predicts scores from the
  state representation. If not present, the output from the lower model is used
  as action scores directly.

| Name                | Type                                       | Description                                                                                                                                                                                                                                                                                                                                                    |
| ------------------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tok2vec`           | [`Model`](https://thinc.ai/docs/api-model) | **Input:** `List[Doc]`. **Output:** `List[Floats2d]`. Subnetwork to map tokens into vector representations.                                                                                                                                                                                                                                                    |
| `nr_feature_tokens` | int                                        | The number of tokens in the context to use to construct the state vector. Valid choices are `1`, `2`, `3`, `6`, `8` and `13`. The `2`, `8` and `13` feature sets are designed for the parser, while the `3` and `6` feature sets are designed for the entity recognizer. The recommended feature sets are `3` for NER, and `8` for the dependency parser.      |
| `hidden_width`      | int                                        | The width of the hidden layer.                                                                                                                                                                                                                                                                                                                                 |
| `maxout_pieces`     | int                                        | How many pieces to use in the state prediction layer. Recommended values are `1`, `2` or `3`. If `1`, the maxout non-linearity is replaced with a [`Relu`](https://thinc.ai/docs/api-layers#relu) non-linearity if `use_upper` is `True`, and no non-linearity if `False`.                                                                                     |
| `use_upper`         | bool                                       | Whether to use an additional hidden layer after the state vector in order to predict the action scores. It is recommended to set this to `False` for large pretrained models such as transformers, and `True` for smaller networks. The upper layer is computed on CPU, which becomes a bottleneck on larger GPU-based models, where it's also less necessary. |
| `nO`                | int                                        | The number of actions the model will predict between. Usually inferred from data at the beginning of training, or loaded from disk.                                                                                                                                                                                                                            |

### spacy.BILUOTagger.v1 {#BILUOTagger source="spacy/ml/models/simple_ner.py"}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.BILUOTagger.v1 "
>
> [model.tok2vec]
> @architectures = "spacy.HashEmbedCNN.v1"
> # etc.
> ```

Construct a simple NER tagger that predicts
[BILUO](/usage/linguistic-features#accessing-ner) tag scores for each token and
uses greedy decoding with transition-constraints to return a valid BILUO tag
sequence. A BILUO tag sequence encodes a sequence of non-overlapping labelled
spans into tags assigned to each token. The first token of a span is given the
tag `B-LABEL`, the last token of the span is given the tag `L-LABEL`, and tokens
within the span are given the tag `U-LABEL`. Single-token spans are given the
tag `U-LABEL`. All other tokens are assigned the tag `O`. The BILUO tag scheme
generally results in better linear separation between classes, especially for
non-CRF models, because there are more distinct classes for the different
situations ([Ratinov et al., 2009](https://www.aclweb.org/anthology/W09-1119/)).

| Name      | Type                                       | Description                                                                                                 |
| --------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `tok2vec` | [`Model`](https://thinc.ai/docs/api-model) | **Input:** `List[Doc]`. **Output:** `List[Floats2d]`. Subnetwork to map tokens into vector representations. |

### spacy.IOBTagger.v1 {#IOBTagger source="spacy/ml/models/simple_ner.py"}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.IOBTagger.v1 "
>
> [model.tok2vec]
> @architectures = "spacy.HashEmbedCNN.v1"
> # etc.
> ```

Construct a simple NER tagger, that predicts
[IOB](/usage/linguistic-features#accessing-ner) tag scores for each token and
uses greedy decoding with transition-constraints to return a valid IOB tag
sequence. An IOB tag sequence encodes a sequence of non-overlapping labeled
spans into tags assigned to each token. The first token of a span is given the
tag B-LABEL, and subsequent tokens are given the tag I-LABEL. All other tokens
are assigned the tag O.

| Name      | Type                                       | Description                                                                                                 |
| --------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `tok2vec` | [`Model`](https://thinc.ai/docs/api-model) | **Input:** `List[Doc]`. **Output:** `List[Floats2d]`. Subnetwork to map tokens into vector representations. |

## Tagging architectures {#tagger source="spacy/ml/models/tagger.py"}

### spacy.Tagger.v1 {#Tagger}

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

Build a tagger model, using a provided token-to-vector component. The tagger
model simply adds a linear layer with softmax activation to predict scores given
the token vectors.

| Name      | Type                                       | Description                                                                                                 |
| --------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `tok2vec` | [`Model`](https://thinc.ai/docs/api-model) | **Input:** `List[Doc]`. **Output:** `List[Floats2d]`. Subnetwork to map tokens into vector representations. |
| `nO`      | int                                        | The number of tags to output. Inferred from the data if `None`.                                             |

## Text classification architectures {#textcat source="spacy/ml/models/textcat.py"}

A text classification architecture needs to take a [`Doc`](/api/doc) as input,
and produce a score for each potential label class. Textcat challenges can be
binary (e.g. sentiment analysis) or involve multiple possible labels.
Multi-label challenges can either have mutually exclusive labels (each example
has exactly one label), or multiple labels may be applicable at the same time.

As the properties of text classification problems can vary widely, we provide
several different built-in architectures. It is recommended to experiment with
different architectures and settings to determine what works best on your
specific data and challenge.

### spacy.TextCatEnsemble.v1 {#TextCatEnsemble}

Stacked ensemble of a bag-of-words model and a neural network model. The neural
network has an internal CNN Tok2Vec layer and uses attention.

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.TextCatEnsemble.v1"
> exclusive_classes = false
> pretrained_vectors = null
> width = 64
> embed_size = 2000
> conv_depth = 2
> window_size = 1
> ngram_size = 1
> dropout = null
> nO = null
> ```

| Name                        | Type  | Description                                                                                                                                              |
| --------------------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exclusive_classes`         | bool  | Whether or not categories are mutually exclusive.                                                                                                        |
| `pretrained_vectors`        | bool  | Whether or not pretrained vectors will be used in addition to the feature vectors.                                                                       |
| `width`                     | int   | Output dimension of the feature encoding step.                                                                                                           |
| `embed_size`                | int   | Input dimension of the feature encoding step.                                                                                                            |
| `conv_depth`                | int   | Depth of the Tok2Vec layer.                                                                                                                              |
| `window_size`               | int   | The number of contextual vectors to [concatenate](https://thinc.ai/docs/api-layers#expand_window) from the left and from the right.                      |
| `ngram_size`                | int   | Determines the maximum length of the n-grams in the BOW model. For instance, `ngram_size=3`would give unigram, trigram and bigram features.              |
| `dropout`                   | float | The dropout rate.                                                                                                                                        |
| `nO`                        | int   | Output dimension, determined by the number of different labels. If not set, the the [`TextCategorizer`](/api/textcategorizer) component will set it when |
| `begin_training` is called. |

### spacy.TextCatCNN.v1 {#TextCatCNN}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.TextCatCNN.v1"
> exclusive_classes = false
> nO = null
>
> [model.tok2vec]
> @architectures = "spacy.HashEmbedCNN.v1"
> pretrained_vectors = null
> width = 96
> depth = 4
> embed_size = 2000
> window_size = 1
> maxout_pieces = 3
> subword_features = true
> ```

A neural network model where token vectors are calculated using a CNN. The
vectors are mean pooled and used as features in a feed-forward network. This
architecture is usually less accurate than the ensemble, but runs faster.

| Name                | Type                                       | Description                                                                                                                                                                          |
| ------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `exclusive_classes` | bool                                       | Whether or not categories are mutually exclusive.                                                                                                                                    |
| `tok2vec`           | [`Model`](https://thinc.ai/docs/api-model) | The [`tok2vec`](#tok2vec) layer of the model.                                                                                                                                        |
| `nO`                | int                                        | Output dimension, determined by the number of different labels. If not set, the the [`TextCategorizer`](/api/textcategorizer) component will set it when `begin_training` is called. |

### spacy.TextCatBOW.v1 {#TextCatBOW}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.TextCatBOW.v1"
> exclusive_classes = false
> ngram_size = 1
> no_output_layer = false
> nO = null
> ```

An ngram "bag-of-words" model. This architecture should run much faster than the
others, but may not be as accurate, especially if texts are short.

| Name                | Type  | Description                                                                                                                                                                          |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `exclusive_classes` | bool  | Whether or not categories are mutually exclusive.                                                                                                                                    |
| `ngram_size`        | int   | Determines the maximum length of the n-grams in the BOW model. For instance, `ngram_size=3`would give unigram, trigram and bigram features.                                          |
| `no_output_layer`   | float | Whether or not to add an output layer to the model (`Softmax` activation if `exclusive_classes=True`, else `Logistic`.                                                               |
| `nO`                | int   | Output dimension, determined by the number of different labels. If not set, the the [`TextCategorizer`](/api/textcategorizer) component will set it when `begin_training` is called. |

## Entity linking architectures {#entitylinker source="spacy/ml/models/entity_linker.py"}

An [`EntityLinker`](/api/entitylinker) component disambiguates textual mentions
(tagged as named entities) to unique identifiers, grounding the named entities
into the "real world". This requires 3 main components:

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

A function that creates a default, empty `KnowledgeBase` from a
[`Vocab`](/api/vocab) instance.

| Name                   | Type | Description                                                               |
| ---------------------- | ---- | ------------------------------------------------------------------------- |
| `entity_vector_length` | int  | The length of the vectors encoding each entity in the KB - 64 by default. |

### spacy.CandidateGenerator.v1 {#CandidateGenerator}

A function that takes as input a [`KnowledgeBase`](/api/kb) and a
[`Span`](/api/span) object denoting a named entity, and returns a list of
plausible [`Candidate` objects](/api/kb/#candidate_init). The default
`CandidateGenerator` simply uses the text of a mention to find its potential
aliases in the `KnowledgeBase`. Note that this function is case-dependent.
