---
title: Layers and Model Architectures
teaser: Power spaCy components with custom neural networks
menu:
  - ['Type Signatures', 'type-sigs']
  - ['Swapping Architectures', 'swap-architectures']
  - ['PyTorch & TensorFlow', 'frameworks']
  - ['Custom Thinc Models', 'thinc']
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
PyTorch, TensorFlow and MXNet. Each `Model` can also be used as a sublayer of a
larger network, allowing you to freely combine implementations from different
frameworks into a single model.

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
default. This architecture combines a simple bag-of-words model with a neural
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
using a unified [`Model`](https://thinc.ai/docs/api-model) API. This makes it
easy to use a model implemented in a different framework to power a component in
your spaCy pipeline. For example, to wrap a PyTorch model as a Thinc `Model`,
you can use Thinc's
[`PyTorchWrapper`](https://thinc.ai/docs/api-layers#pytorchwrapper):

```python
from thinc.api import PyTorchWrapper

wrapped_pt_model = PyTorchWrapper(torch_model)
```

Let's use PyTorch to define a very simple neural network consisting of two
hidden `Linear` layers with `ReLU` activation and dropout, and a
softmax-activated output layer:

```python
### PyTorch model
from torch import nn

torch_model = nn.Sequential(
    nn.Linear(width, hidden_width),
    nn.ReLU(),
    nn.Dropout2d(dropout),
    nn.Linear(hidden_width, nO),
    nn.ReLU(),
    nn.Dropout2d(dropout),
    nn.Softmax(dim=1)
)
```

The resulting wrapped `Model` can be used as a **custom architecture** as such,
or can be a **subcomponent of a larger model**. For instance, we can use Thinc's
[`chain`](https://thinc.ai/docs/api-layers#chain) combinator, which works like
`Sequential` in PyTorch, to combine the wrapped model with other components in a
larger network. This effectively means that you can easily wrap different
components from different frameworks, and "glue" them together with Thinc:

```python
from thinc.api import chain, with_array, PyTorchWrapper
from spacy.ml import CharacterEmbed

wrapped_pt_model = PyTorchWrapper(torch_model)
char_embed = CharacterEmbed(width, embed_size, nM, nC)
model = chain(char_embed, with_array(wrapped_pt_model))
```

In the above example, we have combined our custom PyTorch model with a character
embedding layer defined by spaCy.
[CharacterEmbed](/api/architectures#CharacterEmbed) returns a `Model` that takes
a ~~List[Doc]~~ as input, and outputs a ~~List[Floats2d]~~. To make sure that
the wrapped PyTorch model receives valid inputs, we use Thinc's
[`with_array`](https://thinc.ai/docs/api-layers#with_array) helper.

You could also implement a model that only uses PyTorch for the transformer
layers, and "native" Thinc layers to do fiddly input and output transformations
and add on task-specific "heads", as efficiency is less of a consideration for
those parts of the network.

### Using wrapped models {#frameworks-usage}

To use our custom model including the PyTorch subnetwork, all we need to do is
register the architecture using the
[`architectures` registry](/api/top-level#registry). This will assign the
architecture a name so spaCy knows how to find it, and allows passing in
arguments like hyperparameters via the [config](/usage/training#config). The
full example then becomes:

```python
### Registering the architecture {highlight="9"}
from typing import List
from thinc.types import Floats2d
from thinc.api import Model, PyTorchWrapper, chain, with_array
import spacy
from spacy.tokens.doc import Doc
from spacy.ml import CharacterEmbed
from torch import nn

@spacy.registry.architectures("CustomTorchModel.v1")
def create_torch_model(
    nO: int,
    width: int,
    hidden_width: int,
    embed_size: int,
    nM: int,
    nC: int,
    dropout: float,
) -> Model[List[Doc], List[Floats2d]]:
    char_embed = CharacterEmbed(width, embed_size, nM, nC)
    torch_model = nn.Sequential(
        nn.Linear(width, hidden_width),
        nn.ReLU(),
        nn.Dropout2d(dropout),
        nn.Linear(hidden_width, nO),
        nn.ReLU(),
        nn.Dropout2d(dropout),
        nn.Softmax(dim=1)
    )
    wrapped_pt_model = PyTorchWrapper(torch_model)
    model = chain(char_embed, with_array(wrapped_pt_model))
    return model
```

The model definition can now be used in any existing trainable spaCy component,
by specifying it in the config file. In this configuration, all required
parameters for the various subcomponents of the custom architecture are passed
in as settings via the config.

```ini
### config.cfg (excerpt) {highlight="5-5"}
[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "CustomTorchModel.v1"
nO = 50
width = 96
hidden_width = 48
embed_size = 2000
nM = 64
nC = 8
dropout = 0.2
```

<Infobox variant="warning">

Remember that it is best not to rely on any (hidden) default values, to ensure
that training configs are complete and experiments fully reproducible.

</Infobox>

Note that when using a PyTorch or Tensorflow model, it is recommended to set the
GPU memory allocator accordingly. When `gpu_allocator` is set to "pytorch" or
"tensorflow" in the training config, cupy will allocate memory via those
respective libraries, preventing OOM errors when there's available memory
sitting in the other library's pool.

```ini
### config.cfg (excerpt)
[training]
gpu_allocator = "pytorch"
```

## Custom models with Thinc {#thinc}

Of course it's also possible to define the `Model` from the previous section
entirely in Thinc. The Thinc documentation provides details on the
[various layers](https://thinc.ai/docs/api-layers) and helper functions
available. Combinators can also be used to
[overload operators](https://thinc.ai/docs/usage-models#operators) and a common
usage pattern is to bind `chain` to `>>`. The "native" Thinc version of our
simple neural network would then become:

```python
from thinc.api import chain, with_array, Model, Relu, Dropout, Softmax
from spacy.ml import CharacterEmbed

char_embed = CharacterEmbed(width, embed_size, nM, nC)
with Model.define_operators({">>": chain}):
    layers = (
        Relu(hidden_width, width)
        >> Dropout(dropout)
        >> Relu(hidden_width, hidden_width)
        >> Dropout(dropout)
        >> Softmax(nO, hidden_width)
    )
    model = char_embed >> with_array(layers)
```

<Infobox variant="warning" title="Important note on inputs and outputs">

Note that Thinc layers define the output dimension (`nO`) as the first argument,
followed (optionally) by the input dimension (`nI`). This is in contrast to how
the PyTorch layers are defined, where `in_features` precedes `out_features`.

</Infobox>

### Shape inference in Thinc {#thinc-shape-inference}

It is **not** strictly necessary to define all the input and output dimensions
for each layer, as Thinc can perform
[shape inference](https://thinc.ai/docs/usage-models#validation) between
sequential layers by matching up the output dimensionality of one layer to the
input dimensionality of the next. This means that we can simplify the `layers`
definition:

> #### Diff
>
> ```diff
> layers = (
>     Relu(hidden_width, width)
>     >> Dropout(dropout)
> -   >> Relu(hidden_width, hidden_width)
> +    >> Relu(hidden_width)
>     >> Dropout(dropout)
> -   >> Softmax(nO, hidden_width)
> +   >> Softmax(nO)
> )
> ```

```python
with Model.define_operators({">>": chain}):
    layers = (
        Relu(hidden_width, width)
        >> Dropout(dropout)
        >> Relu(hidden_width)
        >> Dropout(dropout)
        >> Softmax(nO)
    )
```

Thinc can even go one step further and **deduce the correct input dimension** of
the first layer, and output dimension of the last. To enable this functionality,
you have to call
[`Model.initialize`](https://thinc.ai/docs/api-model#initialize) with an **input
sample** `X` and an **output sample** `Y` with the correct dimensions:

```python
### Shape inference with initialization {highlight="3,7,10"}
with Model.define_operators({">>": chain}):
    layers = (
        Relu(hidden_width)
        >> Dropout(dropout)
        >> Relu(hidden_width)
        >> Dropout(dropout)
        >> Softmax()
    )
    model = char_embed >> with_array(layers)
    model.initialize(X=input_sample, Y=output_sample)
```

The built-in [pipeline components](/usage/processing-pipelines) in spaCy ensure
that their internal models are **always initialized** with appropriate sample
data. In this case, `X` is typically a ~~List[Doc]~~, while `Y` is typically a
~~List[Array1d]~~ or ~~List[Array2d]~~, depending on the specific task. This
functionality is triggered when
[`nlp.begin_training`](/api/language#begin_training) is called.

### Dropout and normalization in Thinc {#thinc-dropout-norm}

Many of the available Thinc [layers](https://thinc.ai/docs/api-layers) allow you
to define a `dropout` argument that will result in "chaining" an additional
[`Dropout`](https://thinc.ai/docs/api-layers#dropout) layer. Optionally, you can
often specify whether or not you want to add layer normalization, which would
result in an additional
[`LayerNorm`](https://thinc.ai/docs/api-layers#layernorm) layer. That means that
the following `layers` definition is equivalent to the previous:

```python
with Model.define_operators({">>": chain}):
    layers = (
        Relu(hidden_width, dropout=dropout, normalize=False)
        >> Relu(hidden_width, dropout=dropout, normalize=False)
        >> Softmax()
    )
    model = char_embed >> with_array(layers)
    model.initialize(X=input_sample, Y=output_sample)
```

## Create new trainable components {#components}

<Infobox title="This section is still under construction" emoji="🚧" variant="warning">
</Infobox>

<!-- TODO: write trainable component section
- Interaction with `predict`, `get_loss` and `set_annotations`
- Initialization life-cycle with `begin_training`, correlation with add_label
Example: relation extraction component (implemented as project template)
Avoid duplication with usage/processing-pipelines#trainable-components ?
-->

<!-- ![Diagram of a pipeline component with its model](../images/layers-architectures.svg)

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
-->
