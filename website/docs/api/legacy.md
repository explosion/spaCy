---
title: Legacy functions and architectures
teaser: Archived implementations available through spacy-legacy
source: spacy/legacy
---

The [`spacy-legacy`](https://github.com/explosion/spacy-legacy) package includes
outdated registered functions and architectures. It is installed automatically
as a dependency of spaCy, and provides backwards compatibility for archived
functions that may still be used in projects.

You can find the detailed documentation of each such legacy function on this
page.

## Architectures {#architectures}

These functions are available from `@spacy.registry.architectures`.

### spacy.Tok2Vec.v1 {#Tok2Vec_v1}

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
| `encode`    | Encode context into the embeddings, using an architecture such as a CNN, BiLSTM or transformer. For example, [MaxoutWindowEncoder.v1](/api/legacy#MaxoutWindowEncoder_v1). ~~Model[Floats2d, Floats2d]~~                         |
| **CREATES** | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                           |

### spacy.MaxoutWindowEncoder.v1 {#MaxoutWindowEncoder_v1}

The `spacy.MaxoutWindowEncoder.v1` architecture was producing a model of type
`Model[Floats2D, Floats2D]`. Since `spacy.MaxoutWindowEncoder.v2`, this has been
changed to output type `Model[List[Floats2d], List[Floats2d]]`.

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

### spacy.MishWindowEncoder.v1 {#MishWindowEncoder_v1}

The `spacy.MishWindowEncoder.v1` architecture was producing a model of type
`Model[Floats2D, Floats2D]`. Since `spacy.MishWindowEncoder.v2`, this has been
changed to output type `Model[List[Floats2d], List[Floats2d]]`.

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

### spacy.HashEmbedCNN.v1 {#HashEmbedCNN_v1}

Identical to [`spacy.HashEmbedCNN.v2`](/api/architectures#HashEmbedCNN) except
using [`spacy.StaticVectors.v1`](#StaticVectors_v1) if vectors are included.

### spacy.MultiHashEmbed.v1 {#MultiHashEmbed_v1}

Identical to [`spacy.MultiHashEmbed.v2`](/api/architectures#MultiHashEmbed)
except with [`spacy.StaticVectors.v1`](#StaticVectors_v1) if vectors are
included.

### spacy.CharacterEmbed.v1 {#CharacterEmbed_v1}

Identical to [`spacy.CharacterEmbed.v2`](/api/architectures#CharacterEmbed)
except using [`spacy.StaticVectors.v1`](#StaticVectors_v1) if vectors are
included.

### spacy.TextCatEnsemble.v1 {#TextCatEnsemble_v1}

The `spacy.TextCatEnsemble.v1` architecture built an internal `tok2vec` and
`linear_model`. Since `spacy.TextCatEnsemble.v2`, this has been refactored so
that the `TextCatEnsemble` takes these two sublayers as input.

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

Stacked ensemble of a bag-of-words model and a neural network model. The neural
network has an internal CNN Tok2Vec layer and uses attention.

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

### spacy.TextCatCNN.v1 {#TextCatCNN_v1}

Since `spacy.TextCatCNN.v2`, this architecture has become resizable, which means
that you can add labels to a previously trained textcat. `TextCatCNN` v1 did not
yet support that.

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

| Name                | Description                                                                                                                                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exclusive_classes` | Whether or not categories are mutually exclusive. ~~bool~~                                                                                                                                     |
| `tok2vec`           | The [`tok2vec`](#tok2vec) layer of the model. ~~Model~~                                                                                                                                        |
| `nO`                | Output dimension, determined by the number of different labels. If not set, the [`TextCategorizer`](/api/textcategorizer) component will set it when `initialize` is called. ~~Optional[int]~~ |
| **CREATES**         | The model using the architecture. ~~Model[List[Doc], Floats2d]~~                                                                                                                               |

### spacy.TextCatBOW.v1 {#TextCatBOW_v1}

Since `spacy.TextCatBOW.v2`, this architecture has become resizable, which means
that you can add labels to a previously trained textcat. `TextCatBOW` v1 did not
yet support that.

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

An n-gram "bag-of-words" model. This architecture should run much faster than
the others, but may not be as accurate, especially if texts are short.

| Name                | Description                                                                                                                                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exclusive_classes` | Whether or not categories are mutually exclusive. ~~bool~~                                                                                                                                     |
| `ngram_size`        | Determines the maximum length of the n-grams in the BOW model. For instance, `ngram_size=3` would give unigram, trigram and bigram features. ~~int~~                                           |
| `no_output_layer`   | Whether or not to add an output layer to the model (`Softmax` activation if `exclusive_classes` is `True`, else `Logistic`). ~~bool~~                                                          |
| `nO`                | Output dimension, determined by the number of different labels. If not set, the [`TextCategorizer`](/api/textcategorizer) component will set it when `initialize` is called. ~~Optional[int]~~ |
| **CREATES**         | The model using the architecture. ~~Model[List[Doc], Floats2d]~~                                                                                                                               |

### spacy.TransitionBasedParser.v1 {#TransitionBasedParser_v1}

Identical to
[`spacy.TransitionBasedParser.v2`](/api/architectures#TransitionBasedParser)
except the `use_upper` was set to `True` by default.

## Layers {#layers}

These functions are available from `@spacy.registry.layers`.

### spacy.StaticVectors.v1 {#StaticVectors_v1}

Identical to [`spacy.StaticVectors.v2`](/api/architectures#StaticVectors) except
for the handling of tokens without vectors.

<Infobox title="Bugs for tokens without vectors" variant="warning">

`spacy.StaticVectors.v1` maps tokens without vectors to the final row in the
vectors table, which causes the model predictions to change if new vectors are
added to an existing vectors table. See more details in
[issue #7662](https://github.com/explosion/spaCy/issues/7662#issuecomment-813925655).

</Infobox>

## Loggers {#loggers}

These functions are available from `@spacy.registry.loggers`.

### spacy.ConsoleLogger.v1 {#ConsoleLogger_v1}

> #### Example config
>
> ```ini
> [training.logger]
> @loggers = "spacy.ConsoleLogger.v1"
> progress_bar = true
> ```

Writes the results of a training step to the console in a tabular format.

<Accordion title="Example console output" spaced>

```cli
$ python -m spacy train config.cfg
```

```
ℹ Using CPU
ℹ Loading config and nlp from: config.cfg
ℹ Pipeline: ['tok2vec', 'tagger']
ℹ Start training
ℹ Training. Initial learn rate: 0.0

E     #        LOSS TOK2VEC   LOSS TAGGER   TAG_ACC   SCORE
---   ------   ------------   -----------   -------   ------
  0        0           0.00         86.20      0.22     0.00
  0      200           3.08      18968.78     34.00     0.34
  0      400          31.81      22539.06     33.64     0.34
  0      600          92.13      22794.91     43.80     0.44
  0      800         183.62      21541.39     56.05     0.56
  0     1000         352.49      25461.82     65.15     0.65
  0     1200         422.87      23708.82     71.84     0.72
  0     1400         601.92      24994.79     76.57     0.77
  0     1600         662.57      22268.02     80.20     0.80
  0     1800        1101.50      28413.77     82.56     0.83
  0     2000        1253.43      28736.36     85.00     0.85
  0     2200        1411.02      28237.53     87.42     0.87
  0     2400        1605.35      28439.95     88.70     0.89
```

Note that the cumulative loss keeps increasing within one epoch, but should
start decreasing across epochs.

 </Accordion>

| Name           | Description                                               |
| -------------- | --------------------------------------------------------- |
| `progress_bar` | Whether the logger should print the progress bar ~~bool~~ |

Logging utilities for spaCy are implemented in the
[`spacy-loggers`](https://github.com/explosion/spacy-loggers) repo, and the
functions are typically available from `@spacy.registry.loggers`.

More documentation can be found in that repo's
[readme](https://github.com/explosion/spacy-loggers/blob/main/README.md) file.
