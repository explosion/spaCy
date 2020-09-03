---
title: Layers and Model Architectures
teaser: Power spaCy components with custom neural networks
menu:
  - ['Type Signatures', 'type-sigs']
  - ['Swapping Architectures', 'swap-architectures']
  - ['PyTorch & TensorFlow', 'frameworks']
  - ['Thinc Models', 'thinc']
  - ['Trainable Components', 'components']
next: /usage/projects
---

> #### Example
>
> ```python
> from thinc.api import Model, chain
>
> @spacy.registry.architectures.register("model.v1")
> def build_model(width: int, classes: int) -> Model:
>     tok2vec = build_tok2vec(width)
>     output_layer = build_output_layer(width, classes)
>     model = chain(tok2vec, output_layer)
>     return model
> ```

A **model architecture** is a function that wires up a
[Thinc `Model`](https://thinc.ai/docs/api-model) instance. It describes the
neural network that is run internally as part of a component in a spaCy
pipeline. To define the actual architecture, you can implement your logic in
Thinc directly, or you can use Thinc as a thin wrapper around frameworks such as
PyTorch, TensorFlow and MXNet. Each Model can also be used as a sublayer of a
larger network, allowing you to freely combine implementations from different
frameworks into one `Thinc` Model.

spaCy's built-in components require a `Model` instance to be passed to them via
the config system. To change the model architecture of an existing component,
you just need to [**update the config**](#swap-architectures) so that it refers
to a different registered function. Once the component has been created from
this config, you won't be able to change it anymore. The architecture is like a
recipe for the network, and you can't change the recipe once the dish has
already been prepared. You have to make a new one.

```ini
### config.cfg (excerpt)
[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "model.v1"
width = 512
classes = 16
```

## Type signatures {#type-sigs}

> #### Example
>
> ```python
> from typing import List
> from thinc.api import Model, chain
> from thinc.types import Floats2d
> def chain_model(
>     tok2vec: Model[List[Doc], List[Floats2d]],
>     layer1: Model[List[Floats2d], Floats2d],
>     layer2: Model[Floats2d, Floats2d]
> ) -> Model[List[Doc], Floats2d]:
>     model = chain(tok2vec, layer1, layer2)
>     return model
> ```

The Thinc `Model` class is a **generic type** that can specify its input and
output types. Python uses a square-bracket notation for this, so the type
~~Model[List, Dict]~~ says that each batch of inputs to the model will be a
list, and the outputs will be a dictionary. You can be even more specific and
write for instance~~Model[List[Doc], Dict[str, float]]~~ to specify that the
model expects a list of [`Doc`](/api/doc) objects as input, and returns a
dictionary mapping of strings to floats. Some of the most common types you'll
see are: ​

| Type               | Description                                                                                          |
| ------------------ | ---------------------------------------------------------------------------------------------------- |
| ~~List[Doc]~~      | A batch of [`Doc`](/api/doc) objects. Most components expect their models to take this as input.     |
| ~~Floats2d~~       | A two-dimensional `numpy` or `cupy` array of floats. Usually 32-bit.                                 |
| ~~Ints2d~~         | A two-dimensional `numpy` or `cupy` array of integers. Common dtypes include uint64, int32 and int8. |
| ~~List[Floats2d]~~ | A list of two-dimensional arrays, generally with one array per `Doc` and one row per token.          |
| ~~Ragged~~         | A container to handle variable-length sequence data in an unpadded contiguous array.                 |
| ~~Padded~~         | A container to handle variable-length sequence data in a padded contiguous array.                    |

The model type signatures help you figure out which model architectures and
components can **fit together**. For instance, the
[`TextCategorizer`](/api/textcategorizer) class expects a model typed
~~Model[List[Doc], Floats2d]~~, because the model will predict one row of
category probabilities per [`Doc`](/api/doc). In contrast, the
[`Tagger`](/api/tagger) class expects a model typed ~~Model[List[Doc],
List[Floats2d]]~~, because it needs to predict one row of probabilities per
token.

There's no guarantee that two models with the same type signature can be used
interchangeably. There are many other ways they could be incompatible. However,
if the types don't match, they almost surely _won't_ be compatible. This little
bit of validation goes a long way, especially if you
[configure your editor](https://thinc.ai/docs/usage-type-checking) or other
tools to highlight these errors early. The config file is also validated at the
beginning of training, to verify that all the types match correctly.

<Accordion title="Tip: Static type checking in your editor">

If you're using a modern editor like Visual Studio Code, you can
[set up `mypy`](https://thinc.ai/docs/usage-type-checking#install) with the
custom Thinc plugin and get live feedback about mismatched types as you write
code.

[![](../images/thinc_mypy.jpg)](https://thinc.ai/docs/usage-type-checking#linting)

</Accordion>

## Swapping model architectures {#swap-architectures}

If no model is specified for the [`TextCategorizer`](/api/textcategorizer), the
[TextCatEnsemble](/api/architectures#TextCatEnsemble) architecture is used by
default. This architecture combines a simpel bag-of-words model with a neural
network, usually resulting in the most accurate results, but at the cost of
speed. The config file for this model would look something like this:

```ini
### config.cfg (excerpt)
[components.textcat]
factory = "textcat"
labels = []

[components.textcat.model]
@architectures = "spacy.TextCatEnsemble.v1"
exclusive_classes = false
pretrained_vectors = null
width = 64
conv_depth = 2
embed_size = 2000
window_size = 1
ngram_size = 1
dropout = 0
nO = null
```

spaCy has two additional built-in `textcat` architectures, and you can easily
use those by swapping out the definition of the textcat's model. For instance,
to use the simple and fast bag-of-words model
[TextCatBOW](/api/architectures#TextCatBOW), you can change the config to:

```ini
### config.cfg (excerpt) {highlight="6-10"}
[components.textcat]
factory = "textcat"
labels = []

[components.textcat.model]
@architectures = "spacy.TextCatBOW.v1"
exclusive_classes = false
ngram_size = 1
no_output_layer = false
nO = null
```

For details on all pre-defined architectures shipped with spaCy and how to
configure them, check out the [model architectures](/api/architectures)
documentation.

### Defining sublayers {#sublayers}

Model architecture functions often accept **sublayers as arguments**, so that
you can try **substituting a different layer** into the network. Depending on
how the architecture function is structured, you might be able to define your
network structure entirely through the [config system](/usage/training#config),
using layers that have already been defined. ​

In most neural network models for NLP, the most important parts of the network
are what we refer to as the
[embed and encode](https://explosion.ai/blog/deep-learning-formula-nlp) steps.
These steps together compute dense, context-sensitive representations of the
tokens, and their combination forms a typical
[`Tok2Vec`](/api/architectures#Tok2Vec) layer:

```ini
### config.cfg (excerpt)
[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v1"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v1"
# ...

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
# ...
```

By defining these sublayers specifically, it becomes straightforward to swap out
a sublayer for another one, for instance changing the first sublayer to a
character embedding with the [CharacterEmbed](/api/architectures#CharacterEmbed)
architecture:

```ini
### config.cfg (excerpt)
[components.tok2vec.model.embed]
@architectures = "spacy.CharacterEmbed.v1"
# ...

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
# ...
```

Most of spaCy's default architectures accept a `tok2vec` layer as a sublayer
within the larger task-specific neural network. This makes it easy to **switch
between** transformer, CNN, BiLSTM or other feature extraction approaches. The
[transformers documentation](/usage/embeddings-transformers#training-custom-model)
section shows an example of swapping out a model's standard `tok2vec` layer with
a transformer. And if you want to define your own solution, all you need to do
is register a ~~Model[List[Doc], List[Floats2d]]~~ architecture function, and
you'll be able to try it out in any of the spaCy components. ​

## Wrapping PyTorch, TensorFlow and other frameworks {#frameworks}

Thinc allows you to [wrap models](https://thinc.ai/docs/usage-frameworks)
written in other machine learning frameworks like PyTorch, TensorFlow and MXNet
using a unified [`Model`](https://thinc.ai/docs/api-model) API. As well as
**wrapping whole models**, Thinc lets you call into an external framework for
just **part of your model**: you can have a model where you use PyTorch just for
the transformer layers, using "native" Thinc layers to do fiddly input and
output transformations and add on task-specific "heads", as efficiency is less
of a consideration for those parts of the network.

<!-- TODO: custom tagger implemented in PyTorch, wrapped as Thinc model, link off to project (with notebook?) -->

## Implementing models in Thinc {#thinc}

<!-- TODO: use same example as above, custom tagger, but implemented in Thinc, link off to Thinc docs where appropriate -->

## Models for trainable components {#components}

<!-- TODO:

- Interaction with `predict`, `get_loss` and `set_annotations`
- Initialization life-cycle with `begin_training`.

Example: relation extraction component (implemented as project template)

-->

![Diagram of a pipeline component with its model](../images/layers-architectures.svg)

```python
def update(self, examples):
    docs = [ex.predicted for ex in examples]
    refs = [ex.reference for ex in examples]
    predictions, backprop = self.model.begin_update(docs)
    gradient = self.get_loss(predictions, refs)
    backprop(gradient)

def __call__(self, doc):
    predictions = self.model([doc])
    self.set_annotations(predictions)
```
