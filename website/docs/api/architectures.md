---
title: Model Architectures
teaser: Pre-defined model architectures included with the core library
source: spacy/ml/models
menu:
  - ['Tok2Vec', 'tok2vec-arch']
  - ['Transformers', 'transformers']
  - ['Pretraining', 'pretrain']
  - ['Parser & NER', 'parser']
  - ['Tagging', 'tagger']
  - ['Text Classification', 'textcat']
  - ['Span Classification', 'spancat']
  - ['Entity Linking', 'entitylinker']
---

A **model architecture** is a function that wires up a
[`Model`](https://thinc.ai/docs/api-model) instance, which you can then use in a
pipeline component or as a layer of a larger network. This page documents
spaCy's built-in architectures that are used for different NLP tasks. All
trainable [built-in components](/api#architecture-pipeline) expect a `model`
argument defined in the config and document their the default architecture.
Custom architectures can be registered using the
[`@spacy.registry.architectures`](/api/top-level#registry) decorator and used as
part of the [training config](/usage/training#custom-functions). Also see the
usage documentation on
[layers and model architectures](/usage/layers-architectures).

## Tok2Vec architectures {#tok2vec-arch source="spacy/ml/models/tok2vec.py"}

### spacy.Tok2Vec.v2 {#Tok2Vec}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.Tok2Vec.v2"
>
> [model.embed]
> @architectures = "spacy.CharacterEmbed.v2"
> # ...
>
> [model.encode]
> @architectures = "spacy.MaxoutWindowEncoder.v2"
> # ...
> ```

Construct a tok2vec model out of two subnetworks: one for embedding and one for
encoding. See the
["Embed, Encode, Attend, Predict"](https://explosion.ai/blog/deep-learning-formula-nlp)
blog post for background.

| Name        | Description                                                                                                                                                                                                                      |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `embed`     | Embed tokens into context-independent word vector representations. For example, [CharacterEmbed](/api/architectures#CharacterEmbed) or [MultiHashEmbed](/api/architectures#MultiHashEmbed). ~~Model[List[Doc], List[Floats2d]]~~ |
| `encode`    | Encode context into the embeddings, using an architecture such as a CNN, BiLSTM or transformer. For example, [MaxoutWindowEncoder](/api/architectures#MaxoutWindowEncoder). ~~Model[List[Floats2d], List[Floats2d]]~~            |
| **CREATES** | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                           |

### spacy.HashEmbedCNN.v2 {#HashEmbedCNN}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.HashEmbedCNN.v2"
> pretrained_vectors = null
> width = 96
> depth = 4
> embed_size = 2000
> window_size = 1
> maxout_pieces = 3
> subword_features = true
> ```

Build spaCy's "standard" tok2vec layer. This layer is defined by a
[MultiHashEmbed](/api/architectures#MultiHashEmbed) embedding layer that uses
subword features, and a
[MaxoutWindowEncoder](/api/architectures#MaxoutWindowEncoder) encoding layer
consisting of a CNN and a layer-normalized maxout activation function.

| Name                 | Description                                                                                                                                                                                                                                                                   |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`              | The width of the input and output. These are required to be the same, so that residual connections can be used. Recommended values are `96`, `128` or `300`. ~~int~~                                                                                                          |
| `depth`              | The number of convolutional layers to use. Recommended values are between `2` and `8`. ~~int~~                                                                                                                                                                                |
| `embed_size`         | The number of rows in the hash embedding tables. This can be surprisingly small, due to the use of the hash embeddings. Recommended values are between `2000` and `10000`. ~~int~~                                                                                            |
| `window_size`        | The number of tokens on either side to concatenate during the convolutions. The receptive field of the CNN will be `depth * (window_size * 2 + 1)`, so a 4-layer network with a window size of `2` will be sensitive to 20 words at a time. Recommended value is `1`. ~~int~~ |
| `maxout_pieces`      | The number of pieces to use in the maxout non-linearity. If `1`, the [`Mish`](https://thinc.ai/docs/api-layers#mish) non-linearity is used instead. Recommended values are `1`-`3`. ~~int~~                                                                                   |
| `subword_features`   | Whether to also embed subword features, specifically the prefix, suffix and word shape. This is recommended for alphabetic languages like English, but not if single-character tokens are used for a language such as Chinese. ~~bool~~                                       |
| `pretrained_vectors` | Whether to also use static vectors. ~~bool~~                                                                                                                                                                                                                                  |
| **CREATES**          | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                                                                        |

### spacy.Tok2VecListener.v1 {#Tok2VecListener}

> #### Example config
>
> ```ini
> [components.tok2vec]
> factory = "tok2vec"
>
> [components.tok2vec.model]
> @architectures = "spacy.HashEmbedCNN.v2"
> width = 342
>
> [components.tagger]
> factory = "tagger"
>
> [components.tagger.model]
> @architectures = "spacy.Tagger.v2"
>
> [components.tagger.model.tok2vec]
> @architectures = "spacy.Tok2VecListener.v1"
> width = ${components.tok2vec.model.width}
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

Listeners work by caching the `Tok2Vec` output for a given batch of `Doc`s. This
means that in order for a component to work with the listener, the batch of
`Doc`s passed to the listener must be the same as the batch of `Doc`s passed to
the `Tok2Vec`. As a result, any manipulation of the `Doc`s which would affect
`Tok2Vec` output, such as to create special contexts or remove `Doc`s for which
no prediction can be made, must happen inside the model, **after** the call to
the `Tok2Vec` component.

| Name        | Description                                                                                                                                                                                                                                                                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `width`     | The width of the vectors produced by the "upstream" [`Tok2Vec`](/api/tok2vec) component. ~~int~~                                                                                                                                                                                                                                     |
| `upstream`  | A string to identify the "upstream" `Tok2Vec` component to communicate with. By default, the upstream name is the wildcard string `"*"`, but you could also specify the name of the `Tok2Vec` component. You'll almost never have multiple upstream `Tok2Vec` components, so the wildcard string will almost always be fine. ~~str~~ |
| **CREATES** | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                                                                                                                               |

### spacy.MultiHashEmbed.v2 {#MultiHashEmbed}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.MultiHashEmbed.v2"
> width = 64
> attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
> rows = [2000, 1000, 1000, 1000]
> include_static_vectors = true
> ```

Construct an embedding layer that separately embeds a number of lexical
attributes using hash embedding, concatenates the results, and passes it through
a feed-forward subnetwork to build a mixed representation. The features used can
be configured with the `attrs` argument. The suggested attributes are `NORM`,
`PREFIX`, `SUFFIX` and `SHAPE`. This lets the model take into account some
subword information, without construction a fully character-based
representation. If pretrained vectors are available, they can be included in the
representation as well, with the vectors table kept static (i.e. it's not
updated).

| Name                     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`                  | The output width. Also used as the width of the embedding tables. Recommended values are between `64` and `300`. If static vectors are included, a learned linear layer is used to map the vectors to the specified width before concatenating it with the other embedding outputs. A single maxout layer is then used to reduce the concatenated vectors to the final width. ~~int~~                                                              |
| `attrs`                  | The token attributes to embed. A separate embedding table will be constructed for each attribute. ~~List[Union[int, str]]~~                                                                                                                                                                                                                                                                                                                        |
| `rows`                   | The number of rows for each embedding tables. Can be low, due to the hashing trick. Recommended values are between `1000` and `10000`. The layer needs surprisingly few rows, due to its use of the hashing trick. Generally between 2000 and 10000 rows is sufficient, even for very large vocabularies. A number of rows must be specified for each table, so the `rows` list must be of the same length as the `attrs` parameter. ~~List[int]~~ |
| `include_static_vectors` | Whether to also use static word vectors. Requires a vectors table to be loaded in the [`Doc`](/api/doc) objects' vocab. ~~bool~~                                                                                                                                                                                                                                                                                                                   |
| **CREATES**              | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                                                                                                                                                                                                                                             |

### spacy.CharacterEmbed.v2 {#CharacterEmbed}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.CharacterEmbed.v2"
> width = 128
> rows = 7000
> nM = 64
> nC = 8
> ```

Construct an embedded representation based on character embeddings, using a
feed-forward network. A fixed number of UTF-8 byte characters are used for each
word, taken from the beginning and end of the word equally. Padding is used in
the center for words that are too short.

For instance, let's say `nC=4`, and the word is "jumping". The characters used
will be `"jung"` (two from the start, two from the end). If we had `nC=8`, the
characters would be `"jumpping"`: 4 from the start, 4 from the end. This ensures
that the final character is always in the last position, instead of being in an
arbitrary position depending on the word length.

The characters are embedded in a embedding table with a given number of rows,
and the vectors concatenated. A hash-embedded vector of the `NORM` of the word
is also concatenated on, and the result is then passed through a feed-forward
network to construct a single vector to represent the information.

| Name        | Description                                                                                                                                                     |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`     | The width of the output vector and the `NORM` hash embedding. ~~int~~                                                                                           |
| `rows`      | The number of rows in the `NORM` hash embedding table. ~~int~~                                                                                                  |
| `nM`        | The dimensionality of the character embeddings. Recommended values are between `16` and `64`. ~~int~~                                                           |
| `nC`        | The number of UTF-8 bytes to embed per word. Recommended values are between `3` and `8`, although it may depend on the length of words in the language. ~~int~~ |
| **CREATES** | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                          |

### spacy.MaxoutWindowEncoder.v2 {#MaxoutWindowEncoder}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.MaxoutWindowEncoder.v2"
> width = 128
> window_size = 1
> maxout_pieces = 3
> depth = 4
> ```

Encode context using convolutions with maxout activation, layer normalization
and residual connections.

| Name            | Description                                                                                                                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`         | The input and output width. These are required to be the same, to allow residual connections. This value will be determined by the width of the inputs. Recommended values are between `64` and `300`. ~~int~~ |
| `window_size`   | The number of words to concatenate around each token to construct the convolution. Recommended value is `1`. ~~int~~                                                                                           |
| `maxout_pieces` | The number of maxout pieces to use. Recommended values are `2` or `3`. ~~int~~                                                                                                                                 |
| `depth`         | The number of convolutional layers. Recommended value is `4`. ~~int~~                                                                                                                                          |
| **CREATES**     | The model using the architecture. ~~Model[List[Floats2d], List[Floats2d]]~~                                                                                                                                    |

### spacy.MishWindowEncoder.v2 {#MishWindowEncoder}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.MishWindowEncoder.v2"
> width = 64
> window_size = 1
> depth = 4
> ```

Encode context using convolutions with
[`Mish`](https://thinc.ai/docs/api-layers#mish) activation, layer normalization
and residual connections.

| Name          | Description                                                                                                                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`       | The input and output width. These are required to be the same, to allow residual connections. This value will be determined by the width of the inputs. Recommended values are between `64` and `300`. ~~int~~ |
| `window_size` | The number of words to concatenate around each token to construct the convolution. Recommended value is `1`. ~~int~~                                                                                           |
| `depth`       | The number of convolutional layers. Recommended value is `4`. ~~int~~                                                                                                                                          |
| **CREATES**   | The model using the architecture. ~~Model[List[Floats2d], List[Floats2d]]~~                                                                                                                                    |

### spacy.TorchBiLSTMEncoder.v1 {#TorchBiLSTMEncoder}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.TorchBiLSTMEncoder.v1"
> width = 64
> depth = 2
> dropout = 0.0
> ```

Encode context using bidirectional LSTM layers. Requires
[PyTorch](https://pytorch.org).

| Name        | Description                                                                                                                                                                                                    |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`     | The input and output width. These are required to be the same, to allow residual connections. This value will be determined by the width of the inputs. Recommended values are between `64` and `300`. ~~int~~ |
| `depth`     | The number of recurrent layers, for instance `depth=2` results in stacking two LSTMs together. ~~int~~                                                                                                         |
| `dropout`   | Creates a Dropout layer on the outputs of each LSTM layer except the last layer. Set to 0.0 to disable this functionality. ~~float~~                                                                           |
| **CREATES** | The model using the architecture. ~~Model[List[Floats2d], List[Floats2d]]~~                                                                                                                                    |

### spacy.StaticVectors.v2 {#StaticVectors}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.StaticVectors.v2"
> nO = null
> nM = null
> dropout = 0.2
> key_attr = "ORTH"
>
> [model.init_W]
> @initializers = "glorot_uniform_init.v1"
> ```

Embed [`Doc`](/api/doc) objects with their vocab's vectors table, applying a
learned linear projection to control the dimensionality. Unknown tokens are
mapped to a zero vector. See the documentation on
[static vectors](/usage/embeddings-transformers#static-vectors) for details.

| Name        | Description                                                                                                                                                                                                             |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nO`        | The output width of the layer, after the linear projection. ~~Optional[int]~~                                                                                                                                           |
| `nM`        | The width of the static vectors. ~~Optional[int]~~                                                                                                                                                                      |
| `dropout`   | Optional dropout rate. If set, it's applied per dimension over the whole batch. Defaults to `None`. ~~Optional[float]~~                                                                                                 |
| `init_W`    | The [initialization function](https://thinc.ai/docs/api-initializers). Defaults to [`glorot_uniform_init`](https://thinc.ai/docs/api-initializers#glorot_uniform_init). ~~Callable[[Ops, Tuple[int, ...]]], FloatsXd]~~ |
| `key_attr`  | Defaults to `"ORTH"`. ~~str~~                                                                                                                                                                                           |
| **CREATES** | The model using the architecture. ~~Model[List[Doc], Ragged]~~                                                                                                                                                          |

### spacy.FeatureExtractor.v1 {#FeatureExtractor}

> #### Example config
>
> ```ini
> [model]
> @architectures = "spacy.FeatureExtractor.v1"
> columns = ["NORM", "PREFIX", "SUFFIX", "SHAPE", "ORTH"]
> ```

Extract arrays of input features from [`Doc`](/api/doc) objects. Expects a list
of feature names to extract, which should refer to token attributes.

| Name        | Description                                                              |
| ----------- | ------------------------------------------------------------------------ |
| `columns`   | The token attributes to extract. ~~List[Union[int, str]]~~               |
| **CREATES** | The created feature extraction layer. ~~Model[List[Doc], List[Ints2d]]~~ |

## Transformer architectures {#transformers source="github.com/explosion/spacy-transformers/blob/master/spacy_transformers/architectures.py"}

The following architectures are provided by the package
[`spacy-transformers`](https://github.com/explosion/spacy-transformers). See the
[usage documentation](/usage/embeddings-transformers#transformers) for how to
integrate the architectures into your training config.

<Infobox variant="warning">

Note that in order to use these architectures in your config, you need to
install the
[`spacy-transformers`](https://github.com/explosion/spacy-transformers). See the
[installation docs](/usage/embeddings-transformers#transformers-installation)
for details and system requirements.

</Infobox>

### spacy-transformers.TransformerModel.v3 {#TransformerModel}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy-transformers.TransformerModel.v3"
> name = "roberta-base"
> tokenizer_config = {"use_fast": true}
> transformer_config = {}
> mixed_precision = true
> grad_scaler_config = {"init_scale": 32768}
>
> [model.get_spans]
> @span_getters = "spacy-transformers.strided_spans.v1"
> window = 128
> stride = 96
> ```

Load and wrap a transformer model from the
[HuggingFace `transformers`](https://huggingface.co/transformers) library. You
can use any transformer that has pretrained weights and a PyTorch
implementation. The `name` variable is passed through to the underlying library,
so it can be either a string or a path. If it's a string, the pretrained weights
will be downloaded via the transformers library if they are not already
available locally.

In order to support longer documents, the
[TransformerModel](/api/architectures#TransformerModel) layer allows you to pass
in a `get_spans` function that will divide up the [`Doc`](/api/doc) objects
before passing them through the transformer. Your spans are allowed to overlap
or exclude tokens. This layer is usually used directly by the
[`Transformer`](/api/transformer) component, which allows you to share the
transformer weights across your pipeline. For a layer that's configured for use
in other components, see
[Tok2VecTransformer](/api/architectures#Tok2VecTransformer).

| Name                 | Description                                                                                                                                                                                                                                           |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`               | Any model name that can be loaded by [`transformers.AutoModel`](https://huggingface.co/transformers/model_doc/auto.html#transformers.AutoModel). ~~str~~                                                                                              |
| `get_spans`          | Function that takes a batch of [`Doc`](/api/doc) object and returns lists of [`Span`](/api) objects to process by the transformer. [See here](/api/transformer#span_getters) for built-in options and examples. ~~Callable[[List[Doc]], List[Span]]~~ |
| `tokenizer_config`   | Tokenizer settings passed to [`transformers.AutoTokenizer`](https://huggingface.co/transformers/model_doc/auto.html#transformers.AutoTokenizer). ~~Dict[str, Any]~~                                                                                   |
| `transformer_config` | Transformer settings passed to [`transformers.AutoConfig`](https://huggingface.co/transformers/model_doc/auto.html?highlight=autoconfig#transformers.AutoConfig) ~~Dict[str, Any]~~                                                                   |
| `mixed_precision`    | Replace whitelisted ops by half-precision counterparts. Speeds up training and prediction on GPUs with [Tensor Cores](https://developer.nvidia.com/tensor-cores) and reduces GPU memory use. ~~bool~~                                                 |
| `grad_scaler_config` | Configuration to pass to `thinc.api.PyTorchGradScaler` during training when `mixed_precision` is enabled. ~~Dict[str, Any]~~                                                                                                                          |
| **CREATES**          | The model using the architecture. ~~Model[List[Doc], FullTransformerBatch]~~                                                                                                                                                                          |
|                      |                                                                                                                                                                                                                                                       |

<Infobox title="Mixed precision support" variant="warning">
Mixed-precision support is currently an experimental feature.
</Infobox>

<Accordion title="Previous versions of spacy-transformers.TransformerModel" spaced>

- The `transformer_config` argument was added in
  `spacy-transformers.TransformerModel.v2`.
- The `mixed_precision` and `grad_scaler_config` arguments were added in
  `spacy-transformers.TransformerModel.v3`.

The other arguments are shared between all versions.

</Accordion>

### spacy-transformers.TransformerListener.v1 {#TransformerListener}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy-transformers.TransformerListener.v1"
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

| Name          | Description                                                                                                                                                                                                                                                                                                                                      |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `pooling`     | A reduction layer used to calculate the token vectors based on zero or more wordpiece vectors. If in doubt, mean pooling (see [`reduce_mean`](https://thinc.ai/docs/api-layers#reduce_mean)) is usually a good choice. ~~Model[Ragged, Floats2d]~~                                                                                               |
| `grad_factor` | Reweight gradients from the component before passing them upstream. You can set this to `0` to "freeze" the transformer weights with respect to the component, or use it to make some components more significant than others. Leaving it at `1.0` is usually fine. ~~float~~                                                                    |
| `upstream`    | A string to identify the "upstream" `Transformer` component to communicate with. By default, the upstream name is the wildcard string `"*"`, but you could also specify the name of the `Transformer` component. You'll almost never have multiple upstream `Transformer` components, so the wildcard string will almost always be fine. ~~str~~ |
| **CREATES**   | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                                                                                                                                           |

### spacy-transformers.Tok2VecTransformer.v3 {#Tok2VecTransformer}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy-transformers.Tok2VecTransformer.v3"
> name = "albert-base-v2"
> tokenizer_config = {"use_fast": false}
> transformer_config = {}
> grad_factor = 1.0
> mixed_precision = true
> grad_scaler_config = {"init_scale": 32768}
> ```

Use a transformer as a [`Tok2Vec`](/api/tok2vec) layer directly. This does
**not** allow multiple components to share the transformer weights and does
**not** allow the transformer to set annotations into the [`Doc`](/api/doc)
object, but it's a **simpler solution** if you only need the transformer within
one component.

| Name                 | Description                                                                                                                                                                                                                                                                   |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_spans`          | Function that takes a batch of [`Doc`](/api/doc) object and returns lists of [`Span`](/api) objects to process by the transformer. [See here](/api/transformer#span_getters) for built-in options and examples. ~~Callable[[List[Doc]], List[Span]]~~                         |
| `tokenizer_config`   | Tokenizer settings passed to [`transformers.AutoTokenizer`](https://huggingface.co/transformers/model_doc/auto.html#transformers.AutoTokenizer). ~~Dict[str, Any]~~                                                                                                           |
| `transformer_config` | Settings to pass to the transformers forward pass. ~~Dict[str, Any]~~                                                                                                                                                                                                         |
| `pooling`            | A reduction layer used to calculate the token vectors based on zero or more wordpiece vectors. If in doubt, mean pooling (see [`reduce_mean`](https://thinc.ai/docs/api-layers#reduce_mean)) is usually a good choice. ~~Model[Ragged, Floats2d]~~                            |
| `grad_factor`        | Reweight gradients from the component before passing them upstream. You can set this to `0` to "freeze" the transformer weights with respect to the component, or use it to make some components more significant than others. Leaving it at `1.0` is usually fine. ~~float~~ |
| `mixed_precision`    | Replace whitelisted ops by half-precision counterparts. Speeds up training and prediction on GPUs with [Tensor Cores](https://developer.nvidia.com/tensor-cores) and reduces GPU memory use. ~~bool~~                                                                         |
| `grad_scaler_config` | Configuration to pass to `thinc.api.PyTorchGradScaler` during training when `mixed_precision` is enabled. ~~Dict[str, Any]~~                                                                                                                                                  |
| **CREATES**          | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                                                                        |

<Infobox title="Mixed precision support" variant="warning">
Mixed-precision support is currently an experimental feature.
</Infobox>

<Accordion title="Previous versions of spacy-transformers.Tok2VecTransformer" spaced>

- The `transformer_config` argument was added in
  `spacy-transformers.Tok2VecTransformer.v2`.
- The `mixed_precision` and `grad_scaler_config` arguments were added in
  `spacy-transformers.Tok2VecTransformer.v3`.

The other arguments are shared between all versions.

</Accordion>

## Pretraining architectures {#pretrain source="spacy/ml/models/multi_task.py"}

The spacy `pretrain` command lets you initialize a `Tok2Vec` layer in your
pipeline with information from raw text. To this end, additional layers are
added to build a network for a temporary task that forces the `Tok2Vec` layer to
learn something about sentence structure and word cooccurrence statistics. Two
pretraining objectives are available, both of which are variants of the cloze
task [Devlin et al. (2018)](https://arxiv.org/abs/1810.04805) introduced for
BERT.

For more information, see the section on
[pretraining](/usage/embeddings-transformers#pretraining).

### spacy.PretrainVectors.v1 {#pretrain_vectors}

> #### Example config
>
> ```ini
> [pretraining]
> component = "tok2vec"
>
> [initialize]
> vectors = "en_core_web_lg"
> ...
>
> [pretraining.objective]
> @architectures = "spacy.PretrainVectors.v1"
> maxout_pieces = 3
> hidden_size = 300
> loss = "cosine"
> ```

Predict the word's vector from a static embeddings table as pretraining
objective for a Tok2Vec layer. To use this objective, make sure that the
`initialize.vectors` section in the config refers to a model with static
vectors.

| Name            | Description                                                                                                                                               |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `maxout_pieces` | The number of maxout pieces to use. Recommended values are `2` or `3`. ~~int~~                                                                            |
| `hidden_size`   | Size of the hidden layer of the model. ~~int~~                                                                                                            |
| `loss`          | The loss function can be either "cosine" or "L2". We typically recommend to use "cosine". ~~~str~~                                                        |
| **CREATES**     | A callable function that can create the Model, given the `vocab` of the pipeline and the `tok2vec` layer to pretrain. ~~Callable[[Vocab, Model], Model]~~ |

### spacy.PretrainCharacters.v1 {#pretrain_chars}

> #### Example config
>
> ```ini
> [pretraining]
> component = "tok2vec"
> ...
>
> [pretraining.objective]
> @architectures = "spacy.PretrainCharacters.v1"
> maxout_pieces = 3
> hidden_size = 300
> n_characters = 4
> ```

Predict some number of leading and trailing UTF-8 bytes as pretraining objective
for a Tok2Vec layer.

| Name            | Description                                                                                                                                               |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `maxout_pieces` | The number of maxout pieces to use. Recommended values are `2` or `3`. ~~int~~                                                                            |
| `hidden_size`   | Size of the hidden layer of the model. ~~int~~                                                                                                            |
| `n_characters`  | The window of characters - e.g. if `n_characters = 2`, the model will try to predict the first two and last two characters of the word. ~~int~~           |
| **CREATES**     | A callable function that can create the Model, given the `vocab` of the pipeline and the `tok2vec` layer to pretrain. ~~Callable[[Vocab, Model], Model]~~ |

## Parser & NER architectures {#parser}

### spacy.TransitionBasedParser.v2 {#TransitionBasedParser source="spacy/ml/models/parser.py"}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.TransitionBasedParser.v2"
> state_type = "ner"
> extra_state_tokens = false
> hidden_width = 64
> maxout_pieces = 2
> use_upper = true
>
> [model.tok2vec]
> @architectures = "spacy.HashEmbedCNN.v2"
> pretrained_vectors = null
> width = 96
> depth = 4
> embed_size = 2000
> window_size = 1
> maxout_pieces = 3
> subword_features = true
> ```

Build a transition-based parser model. Can apply to NER or dependency parsing.
Transition-based parsing is an approach to structured prediction where the task
of predicting the structure is mapped to a series of state transitions. You
might find [this tutorial](https://explosion.ai/blog/parsing-english-in-python)
helpful for background information. The neural network state prediction model
consists of either two or three subnetworks:

- **tok2vec**: Map each token into a vector representation. This subnetwork is
  run once for each batch.
- **lower**: Construct a feature-specific vector for each `(token, feature)`
  pair. This is also run once for each batch. Constructing the state
  representation is then a matter of summing the component features and
  applying the non-linearity.
- **upper** (optional): A feed-forward network that predicts scores from the
  state representation. If not present, the output from the lower model is used
  as action scores directly.

| Name                 | Description                                                                                                                                                                                                                                                                                                                                                             |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tok2vec`            | Subnetwork to map tokens into vector representations. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                                                                                                                                              |
| `state_type`         | Which task to extract features for. Possible values are "ner" and "parser". ~~str~~                                                                                                                                                                                                                                                                                     |
| `extra_state_tokens` | Whether to use an expanded feature set when extracting the state tokens. Slightly slower, but sometimes improves accuracy slightly. Defaults to `False`. ~~bool~~                                                                                                                                                                                                       |
| `hidden_width`       | The width of the hidden layer. ~~int~~                                                                                                                                                                                                                                                                                                                                  |
| `maxout_pieces`      | How many pieces to use in the state prediction layer. Recommended values are `1`, `2` or `3`. If `1`, the maxout non-linearity is replaced with a [`Relu`](https://thinc.ai/docs/api-layers#relu) non-linearity if `use_upper` is `True`, and no non-linearity if `False`. ~~int~~                                                                                      |
| `use_upper`          | Whether to use an additional hidden layer after the state vector in order to predict the action scores. It is recommended to set this to `False` for large pretrained models such as transformers, and `True` for smaller networks. The upper layer is computed on CPU, which becomes a bottleneck on larger GPU-based models, where it's also less necessary. ~~bool~~ |
| `nO`                 | The number of actions the model will predict between. Usually inferred from data at the beginning of training, or loaded from disk. ~~int~~                                                                                                                                                                                                                             |
| **CREATES**          | The model using the architecture. ~~Model[List[Docs], List[List[Floats2d]]]~~                                                                                                                                                                                                                                                                                           |

<Accordion title="spacy.TransitionBasedParser.v1 definition" spaced>

[TransitionBasedParser.v1](/api/legacy#TransitionBasedParser_v1) had the exact
same signature, but the `use_upper` argument was `True` by default.

</Accordion>

## Tagging architectures {#tagger source="spacy/ml/models/tagger.py"}

### spacy.Tagger.v2 {#Tagger}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.Tagger.v2"
> nO = null
> normalize = false
>
> [model.tok2vec]
> # ...
> ```

Build a tagger model, using a provided token-to-vector component. The tagger
model adds a linear layer with softmax activation to predict scores given
the token vectors.

| Name        | Description                                                                                |
| ----------- | ------------------------------------------------------------------------------------------ |
| `tok2vec`   | Subnetwork to map tokens into vector representations. ~~Model[List[Doc], List[Floats2d]]~~ |
| `nO`        | The number of tags to output. Inferred from the data if `None`. ~~Optional[int]~~          |
| `normalize` | Normalize probabilities during inference. Defaults to `False`. ~~bool~~                    |
| **CREATES** | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                     |

<Accordion title="Previous versions of spacy.Tagger" spaced>

- The `normalize` argument was added in `spacy.Tagger.v2`. `spacy.Tagger.v1`
  always normalizes probabilities during inference.

The other arguments are shared between all versions.

</Accordion>

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

<Infobox title="Single-label vs. multi-label classification" variant="warning">

When the architecture for a text classification challenge contains a setting for
`exclusive_classes`, it is important to use the correct value for the correct
pipeline component. The `textcat` component should always be used for
single-label use-cases where `exclusive_classes = true`, while the
`textcat_multilabel` should be used for multi-label settings with
`exclusive_classes = false`.

</Infobox>

### spacy.TextCatEnsemble.v2 {#TextCatEnsemble}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.TextCatEnsemble.v2"
> nO = null
>
> [model.linear_model]
> @architectures = "spacy.TextCatBOW.v2"
> exclusive_classes = true
> ngram_size = 1
> no_output_layer = false
>
> [model.tok2vec]
> @architectures = "spacy.Tok2Vec.v2"
>
> [model.tok2vec.embed]
> @architectures = "spacy.MultiHashEmbed.v2"
> width = 64
> rows = [2000, 2000, 1000, 1000, 1000, 1000]
> attrs = ["ORTH", "LOWER", "PREFIX", "SUFFIX", "SHAPE", "ID"]
> include_static_vectors = false
>
> [model.tok2vec.encode]
> @architectures = "spacy.MaxoutWindowEncoder.v2"
> width = ${model.tok2vec.embed.width}
> window_size = 1
> maxout_pieces = 3
> depth = 2
> ```

Stacked ensemble of a linear bag-of-words model and a neural network model. The
neural network is built upon a Tok2Vec layer and uses attention. The setting for
whether or not this model should cater for multi-label classification, is taken
from the linear model, where it is stored in `model.attrs["multi_label"]`.

| Name           | Description                                                                                                                                                                                    |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `linear_model` | The linear bag-of-words model. ~~Model[List[Doc], Floats2d]~~                                                                                                                                  |
| `tok2vec`      | The `tok2vec` layer to build the neural network upon. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                     |
| `nO`           | Output dimension, determined by the number of different labels. If not set, the [`TextCategorizer`](/api/textcategorizer) component will set it when `initialize` is called. ~~Optional[int]~~ |
| **CREATES**    | The model using the architecture. ~~Model[List[Doc], Floats2d]~~                                                                                                                               |

<Accordion title="spacy.TextCatEnsemble.v1 definition" spaced>

[TextCatEnsemble.v1](/api/legacy#TextCatEnsemble_v1) was functionally similar,
but used an internal `tok2vec` instead of taking it as argument:

| Name                 | Description                                                                                                                                                                                    |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exclusive_classes`  | Whether or not categories are mutually exclusive. ~~bool~~                                                                                                                                     |
| `pretrained_vectors` | Whether or not pretrained vectors will be used in addition to the feature vectors. ~~bool~~                                                                                                    |
| `width`              | Output dimension of the feature encoding step. ~~int~~                                                                                                                                         |
| `embed_size`         | Input dimension of the feature encoding step. ~~int~~                                                                                                                                          |
| `conv_depth`         | Depth of the tok2vec layer. ~~int~~                                                                                                                                                            |
| `window_size`        | The number of contextual vectors to [concatenate](https://thinc.ai/docs/api-layers#expand_window) from the left and from the right. ~~int~~                                                    |
| `ngram_size`         | Determines the maximum length of the n-grams in the BOW model. For instance, `ngram_size=3`would give unigram, trigram and bigram features. ~~int~~                                            |
| `dropout`            | The dropout rate. ~~float~~                                                                                                                                                                    |
| `nO`                 | Output dimension, determined by the number of different labels. If not set, the [`TextCategorizer`](/api/textcategorizer) component will set it when `initialize` is called. ~~Optional[int]~~ |
| **CREATES**          | The model using the architecture. ~~Model[List[Doc], Floats2d]~~                                                                                                                               |

</Accordion>

### spacy.TextCatCNN.v2 {#TextCatCNN}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.TextCatCNN.v2"
> exclusive_classes = false
> nO = null
>
> [model.tok2vec]
> @architectures = "spacy.HashEmbedCNN.v2"
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

| Name                | Description                                                                                                                                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exclusive_classes` | Whether or not categories are mutually exclusive. ~~bool~~                                                                                                                                     |
| `tok2vec`           | The [`tok2vec`](#tok2vec) layer of the model. ~~Model~~                                                                                                                                        |
| `nO`                | Output dimension, determined by the number of different labels. If not set, the [`TextCategorizer`](/api/textcategorizer) component will set it when `initialize` is called. ~~Optional[int]~~ |
| **CREATES**         | The model using the architecture. ~~Model[List[Doc], Floats2d]~~                                                                                                                               |

<Accordion title="spacy.TextCatCNN.v1 definition" spaced>

[TextCatCNN.v1](/api/legacy#TextCatCNN_v1) had the exact same signature, but was
not yet resizable. Since v2, new labels can be added to this component, even
after training.

</Accordion>

### spacy.TextCatBOW.v2 {#TextCatBOW}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.TextCatBOW.v2"
> exclusive_classes = false
> ngram_size = 1
> no_output_layer = false
> nO = null
> ```

An n-gram "bag-of-words" model. This architecture should run much faster than
the others, but may not be as accurate, especially if texts are short.

| Name                | Description                                                                                                                                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exclusive_classes` | Whether or not categories are mutually exclusive. ~~bool~~                                                                                                                                     |
| `ngram_size`        | Determines the maximum length of the n-grams in the BOW model. For instance, `ngram_size=3` would give unigram, trigram and bigram features. ~~int~~                                           |
| `no_output_layer`   | Whether or not to add an output layer to the model (`Softmax` activation if `exclusive_classes` is `True`, else `Logistic`). ~~bool~~                                                          |
| `nO`                | Output dimension, determined by the number of different labels. If not set, the [`TextCategorizer`](/api/textcategorizer) component will set it when `initialize` is called. ~~Optional[int]~~ |
| **CREATES**         | The model using the architecture. ~~Model[List[Doc], Floats2d]~~                                                                                                                               |

<Accordion title="spacy.TextCatBOW.v1 definition" spaced>

[TextCatBOW.v1](/api/legacy#TextCatBOW_v1) had the exact same signature, but was
not yet resizable. Since v2, new labels can be added to this component, even
after training.

</Accordion>

## Span classification architectures {#spancat source="spacy/ml/models/spancat.py"}

### spacy.SpanCategorizer.v1 {#SpanCategorizer}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.SpanCategorizer.v1"
> scorer = {"@layers": "spacy.LinearLogistic.v1"}
>
> [model.reducer]
> @layers = spacy.mean_max_reducer.v1"
> hidden_size = 128
>
> [model.tok2vec]
> @architectures = "spacy.Tok2Vec.v1"
>
> [model.tok2vec.embed]
> @architectures = "spacy.MultiHashEmbed.v1"
> # ...
>
> [model.tok2vec.encode]
> @architectures = "spacy.MaxoutWindowEncoder.v1"
> # ...
> ```

Build a span categorizer model to power a
[`SpanCategorizer`](/api/spancategorizer) component, given a token-to-vector
model, a reducer model to map the sequence of vectors for each span down to a
single vector, and a scorer model to map the vectors to probabilities.

| Name        | Description                                                                     |
| ----------- | ------------------------------------------------------------------------------- |
| `tok2vec`   | The token-to-vector model. ~~Model[List[Doc], List[Floats2d]]~~                 |
| `reducer`   | The reducer model. ~~Model[Ragged, Floats2d]~~                                  |
| `scorer`    | The scorer model. ~~Model[Floats2d, Floats2d]~~                                 |
| **CREATES** | The model using the architecture. ~~Model[Tuple[List[Doc], Ragged], Floats2d]~~ |

### spacy.mean_max_reducer.v1 {#mean_max_reducer}

Reduce sequences by concatenating their mean and max pooled vectors, and then
combine the concatenated vectors with a hidden layer.

| Name          | Description                           |
| ------------- | ------------------------------------- |
| `hidden_size` | The size of the hidden layer. ~~int~~ |

## Entity linking architectures {#entitylinker source="spacy/ml/models/entity_linker.py"}

An [`EntityLinker`](/api/entitylinker) component disambiguates textual mentions
(tagged as named entities) to unique identifiers, grounding the named entities
into the "real world". This requires 3 main components:

- A [`KnowledgeBase`](/api/kb) (KB) holding the unique identifiers, potential
  synonyms and prior probabilities.
- A candidate generation step to produce a set of likely identifiers, given a
  certain textual mention.
- A machine learning [`Model`](https://thinc.ai/docs/api-model) that picks the
  most plausible ID from the set of candidates.

### spacy.EntityLinker.v2 {#EntityLinker}

> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.EntityLinker.v2"
> nO = null
>
> [model.tok2vec]
> @architectures = "spacy.HashEmbedCNN.v2"
> pretrained_vectors = null
> width = 96
> depth = 2
> embed_size = 2000
> window_size = 1
> maxout_pieces = 3
> subword_features = true
> ```

The `EntityLinker` model architecture is a Thinc `Model` with a
[`Linear`](https://thinc.ai/api-layers#linear) output layer.

| Name        | Description                                                                                                                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tok2vec`   | The [`tok2vec`](#tok2vec) layer of the model. ~~Model~~                                                                                                                                                             |
| `nO`        | Output dimension, determined by the length of the vectors encoding each entity in the KB. If the `nO` dimension is not set, the entity linking component will set it when `initialize` is called. ~~Optional[int]~~ |
| **CREATES** | The model using the architecture. ~~Model[List[Doc], Floats2d]~~                                                                                                                                                    |

### spacy.EmptyKB.v1 {#EmptyKB}

A function that creates an empty `KnowledgeBase` from a [`Vocab`](/api/vocab)
instance. This is the default when a new entity linker component is created.

| Name                   | Description                                                                         |
| ---------------------- | ----------------------------------------------------------------------------------- |
| `entity_vector_length` | The length of the vectors encoding each entity in the KB. Defaults to `64`. ~~int~~ |

### spacy.KBFromFile.v1 {#KBFromFile}

A function that reads an existing `KnowledgeBase` from file.

| Name      | Description                                              |
| --------- | -------------------------------------------------------- |
| `kb_path` | The location of the KB that was stored to file. ~~Path~~ |

### spacy.CandidateGenerator.v1 {#CandidateGenerator}

A function that takes as input a [`KnowledgeBase`](/api/kb) and a
[`Span`](/api/span) object denoting a named entity, and returns a list of
plausible [`Candidate`](/api/kb/#candidate) objects. The default
`CandidateGenerator` uses the text of a mention to find its potential
aliases in the `KnowledgeBase`. Note that this function is case-dependent.
