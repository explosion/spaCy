---
title: Legacy functions and architectures
teaser: Archived implementations available through spacy-legacy
source: spacy/legacy
---

The [`spacy-legacy`](https://github.com/explosion/spacy-legacy) package includes 
outdated registered functions and architectures. It is installed automatically as 
a dependency of spaCy, and provides backwards compatibility for archived functions 
that may still be used in projects.

You can find the detailed documentation of each such legacy function on this page.

## Architectures {#architectures}

These functions are available from `@spacy.registry.architectures`.

### spacy.Tok2Vec.v1 {#Tok2Vec}

The `spacy.Tok2Vec.v1` architecture was expecting an `encode` model of type 
`Model[Floats2D, Floats2D]` such as `spacy.MaxoutWindowEncoder.v1` or 
`spacy.MishWindowEncoder.v1`.

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

Construct a tok2vec model out of two subnetworks: one for embedding and one for
encoding. See the
["Embed, Encode, Attend, Predict"](https://explosion.ai/blog/deep-learning-formula-nlp)
blog post for background.

| Name        | Description                                                                                                                                                                                                                      |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `embed`     | Embed tokens into context-independent word vector representations. For example, [CharacterEmbed](/api/architectures#CharacterEmbed) or [MultiHashEmbed](/api/architectures#MultiHashEmbed). ~~Model[List[Doc], List[Floats2d]]~~ |
| `encode`    | Encode context into the embeddings, using an architecture such as a CNN, BiLSTM or transformer. For example, [MaxoutWindowEncoder.v1](/api/legacy#MaxoutWindowEncoder). ~~Model[Floats2d, Floats2d]~~                            |
| **CREATES** | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                           |

### spacy.MaxoutWindowEncoder.v1 {#MaxoutWindowEncoder}

The `spacy.MaxoutWindowEncoder.v1` architecture was producing a model of type 
`Model[Floats2D, Floats2D]`. Since `spacy.MaxoutWindowEncoder.v2`, this has been changed to output 
type `Model[List[Floats2d], List[Floats2d]]`.


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

| Name            | Description                                                                                                                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`         | The input and output width. These are required to be the same, to allow residual connections. This value will be determined by the width of the inputs. Recommended values are between `64` and `300`. ~~int~~ |
| `window_size`   | The number of words to concatenate around each token to construct the convolution. Recommended value is `1`. ~~int~~                                                                                           |
| `maxout_pieces` | The number of maxout pieces to use. Recommended values are `2` or `3`. ~~int~~                                                                                                                                 |
| `depth`         | The number of convolutional layers. Recommended value is `4`. ~~int~~                                                                                                                                          |
| **CREATES**     | The model using the architecture. ~~Model[Floats2d, Floats2d]~~                                                                                                                                                |

### spacy.MishWindowEncoder.v1 {#MishWindowEncoder}

The `spacy.MishWindowEncoder.v1` architecture was producing a model of type 
`Model[Floats2D, Floats2D]`. Since `spacy.MishWindowEncoder.v2`, this has been changed to output 
type `Model[List[Floats2d], List[Floats2d]]`.

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

| Name          | Description                                                                                                                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `width`       | The input and output width. These are required to be the same, to allow residual connections. This value will be determined by the width of the inputs. Recommended values are between `64` and `300`. ~~int~~ |
| `window_size` | The number of words to concatenate around each token to construct the convolution. Recommended value is `1`. ~~int~~                                                                                           |
| `depth`       | The number of convolutional layers. Recommended value is `4`. ~~int~~                                                                                                                                          |
| **CREATES**   | The model using the architecture. ~~Model[Floats2d, Floats2d]~~                                                                                                                                                |
