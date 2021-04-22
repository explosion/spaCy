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
| `encode`    | Encode context into the embeddings, using an architecture such as a CNN, BiLSTM or transformer. For example, [MaxoutWindowEncoder.v1](/api/legacy#MaxoutWindowEncoder_v1). ~~Model[Floats2d, Floats2d]~~                            |
| **CREATES** | The model using the architecture. ~~Model[List[Doc], List[Floats2d]]~~                                                                                                                                                           |

### spacy.MaxoutWindowEncoder.v1 {#MaxoutWindowEncoder_v1}

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

### spacy.MishWindowEncoder.v1 {#MishWindowEncoder_v1}

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


### spacy.TextCatEnsemble.v1 {#TextCatEnsemble_v1}

The `spacy.TextCatEnsemble.v1` architecture built an internal `tok2vec` and `linear_model`. 
Since `spacy.TextCatEnsemble.v2`, this has been refactored so that the `TextCatEnsemble` takes these 
two sublayers as input.

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


### spacy.TextCatEnsemble.v2 {#TextCatEnsemble_v2}

Since `spacy.TextCatEnsemble.v3`, this architecture has become resizable, which means that you can add 
labels to a previously trained textcat. `TextCatEnsemble` v1 and v2 did not yet support that.


> #### Example Config
>
> ```ini
> [model]
> @architectures = "spacy.TextCatEnsemble.v2"
> nO = null
>
> [model.linear_model]
> @architectures = "spacy.TextCatBOW.v1"
> exclusive_classes = true
> ngram_size = 1
> no_output_layer = false
>
> [model.tok2vec]
> @architectures = "spacy.Tok2Vec.v2"
>
> [model.tok2vec.embed]
> @architectures = "spacy.MultiHashEmbed.v1"
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

[TextCatEnsemble.v1](/api/legacy#TextCatEnsemble_v1) was functionally similar, but used an internal `tok2vec` instead of
taking it as argument:

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

### spacy.TextCatCNN.v1 {#TextCatCNN_v1}

Since `spacy.TextCatCNN.v2`, this architecture has become resizable, which means that you can add 
labels to a previously trained textcat. `TextCatCNN` v1 did not yet support that.

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

Since `spacy.TextCatBOW.v2`, this architecture has become resizable, which means that you can add 
labels to a previously trained textcat. `TextCatBOW` v1 did not yet support that.

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

## Loggers {#loggers}

These functions are available from `@spacy.registry.loggers`.

### spacy.WandbLogger.v1 {#WandbLogger_v1}

The first version of the [`WandbLogger`](/api/top-level#WandbLogger) did not yet 
support the `log_dataset_dir` and `model_log_interval` arguments.

> #### Example config
>
> ```ini
> [training.logger]
> @loggers = "spacy.WandbLogger.v1"
> project_name = "monitor_spacy_training"
> remove_config_values = ["paths.train", "paths.dev", "corpora.train.path", "corpora.dev.path"]
> ```
| Name                   | Description                                                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `project_name`         | The name of the project in the Weights & Biases interface. The project will be created automatically if it doesn't exist yet. ~~str~~ |
| `remove_config_values` | A list of values to include from the config before it is uploaded to W&B (default: empty). ~~List[str]~~                              |
