---
title: Layers and Model Architectures
teaser: Power spaCy components with custom neural networks
menu:
  - ['Type Signatures', 'type-sigs']
  - ['Defining Sublayers', 'sublayers']
  - ['PyTorch & TensorFlow', 'frameworks']
  - ['Trainable Components', 'components']
next: /usage/projects
---

​A **model architecture** is a function that wires up a
[Thinc `Model`](https://thinc.ai/docs/api-model) instance, which you can then
use in a component or as a layer of a larger network. You can use Thinc as a
thin wrapper around frameworks such as PyTorch, TensorFlow or MXNet, or you can
implement your logic in Thinc directly. ​ spaCy's built-in components will never
construct their `Model` instances themselves, so you won't have to subclass the
component to change its model architecture. You can just **update the config**
so that it refers to a different registered function. Once the component has
been created, its model instance has already been assigned, so you cannot change
its model architecture. The architecture is like a recipe for the network, and
you can't change the recipe once the dish has already been prepared. You have to
make a new one.

![Diagram of a pipeline component with its model](../images/layers-architectures.svg)

## Type signatures {#type-sigs}

<!-- TODO: update example, maybe simplify definition? -->

> #### Example
>
> ```python
> @spacy.registry.architectures.register("spacy.Tagger.v1")
> def build_tagger_model(
>     tok2vec: Model[List[Doc], List[Floats2d]], nO: Optional[int] = None
> ) -> Model[List[Doc], List[Floats2d]]:
>     t2v_width = tok2vec.get_dim("nO") if tok2vec.has_dim("nO") else None
>     output_layer = Softmax(nO, t2v_width, init_W=zero_init)
>     softmax = with_array(output_layer)
>     model = chain(tok2vec, softmax)
>     model.set_ref("tok2vec", tok2vec)
>     model.set_ref("softmax", output_layer)
>     model.set_ref("output_layer", output_layer)
>     return model
> ```

​ The Thinc `Model` class is a **generic type** that can specify its input and
output types. Python uses a square-bracket notation for this, so the type
~~Model[List, Dict]~~ says that each batch of inputs to the model will be a
list, and the outputs will be a dictionary. Both `typing.List` and `typing.Dict`
are also generics, allowing you to be more specific about the data. For
instance, you can write ~~Model[List[Doc], Dict[str, float]]~~ to specify that
the model expects a list of [`Doc`](/api/doc) objects as input, and returns a
dictionary mapping strings to floats. Some of the most common types you'll see
are: ​

| Type               | Description                                                                                          |
| ------------------ | ---------------------------------------------------------------------------------------------------- |
| ~~List[Doc]~~      | A batch of [`Doc`](/api/doc) objects. Most components expect their models to take this as input.     |
| ~~Floats2d~~       | A two-dimensional `numpy` or `cupy` array of floats. Usually 32-bit.                                 |
| ~~Ints2d~~         | A two-dimensional `numpy` or `cupy` array of integers. Common dtypes include uint64, int32 and int8. |
| ~~List[Floats2d]~~ | A list of two-dimensional arrays, generally with one array per `Doc` and one row per token.          |
| ~~Ragged~~         | A container to handle variable-length sequence data in an unpadded contiguous array.                 |
| ~~Padded~~         | A container to handle variable-length sequence data in a passed contiguous array.                    |

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
tools to highlight these errors early. Thinc will also verify that your types
match correctly when your config file is processed at the beginning of training.

<Infobox title="Tip: Static type checking in your editor" emoji="💡">

If you're using a modern editor like Visual Studio Code, you can
[set up `mypy`](https://thinc.ai/docs/usage-type-checking#install) with the
custom Thinc plugin and get live feedback about mismatched types as you write
code.

[![](../images/thinc_mypy.jpg)](https://thinc.ai/docs/usage-type-checking#linting)

</Infobox>

## Defining sublayers {#sublayers}

​ Model architecture functions often accept **sublayers as arguments**, so that
you can try **substituting a different layer** into the network. Depending on
how the architecture function is structured, you might be able to define your
network structure entirely through the [config system](/usage/training#config),
using layers that have already been defined. ​The
[transformers documentation](/usage/embeddings-transformers#transformers)
section shows a common example of swapping in a different sublayer.

In most neural network models for NLP, the most important parts of the network
are what we refer to as the
[embed and encode](https://explosion.ai/blog/embed-encode-attend-predict) steps.
These steps together compute dense, context-sensitive representations of the
tokens. Most of spaCy's default architectures accept a
[`tok2vec` embedding layer](/api/architectures#tok2vec-arch) as an argument, so
you can control this important part of the network separately. This makes it
easy to **switch between** transformer, CNN, BiLSTM or other feature extraction
approaches. And if you want to define your own solution, all you need to do is
register a ~~Model[List[Doc], List[Floats2d]]~~ architecture function, and
you'll be able to try it out in any of spaCy components. ​

<!-- TODO: example of switching sublayers -->

### Registering new architectures

- Recap concept, link to config docs. ​

## Wrapping PyTorch, TensorFlow and other frameworks {#frameworks}

<!-- TODO: this is copied over from the Thinc docs and we probably want to shorten it and make it more spaCy-specific -->

Thinc allows you to wrap models written in other machine learning frameworks
like PyTorch, TensorFlow and MXNet using a unified
[`Model`](https://thinc.ai/docs/api-model) API. As well as **wrapping whole
models**, Thinc lets you call into an external framework for just **part of your
model**: you can have a model where you use PyTorch just for the transformer
layers, using "native" Thinc layers to do fiddly input and output
transformations and add on task-specific "heads", as efficiency is less of a
consideration for those parts of the network.

Thinc uses a special class, [`Shim`](https://thinc.ai/docs/api-model#shim), to
hold references to external objects. This allows each wrapper space to define a
custom type, with whatever attributes and methods are helpful, to assist in
managing the communication between Thinc and the external library. The
[`Model`](https://thinc.ai/docs/api-model#model) class holds `shim` instances in
a separate list, and communicates with the shims about updates, serialization,
changes of device, etc.

The wrapper will receive each batch of inputs, convert them into a suitable form
for the underlying model instance, and pass them over to the shim, which will
**manage the actual communication** with the model. The output is then passed
back into the wrapper, and converted for use in the rest of the network. The
equivalent procedure happens during backpropagation. Array conversion is handled
via the [DLPack](https://github.com/dmlc/dlpack) standard wherever possible, so
that data can be passed between the frameworks **without copying the data back**
to the host device unnecessarily.

| Framework      | Wrapper layer                                                             | Shim                                                      | DLPack          |
| -------------- | ------------------------------------------------------------------------- | --------------------------------------------------------- | --------------- |
| **PyTorch**    | [`PyTorchWrapper`](https://thinc.ai/docs/api-layers#pytorchwrapper)       | [`PyTorchShim`](https://thinc.ai/docs/api-model#shims)    | ✅              |
| **TensorFlow** | [`TensorFlowWrapper`](https://thinc.ai/docs/api-layers#tensorflowwrapper) | [`TensorFlowShim`](https://thinc.ai/docs/api-model#shims) | ❌ <sup>1</sup> |
| **MXNet**      | [`MXNetWrapper`](https://thinc.ai/docs/api-layers#mxnetwrapper)           | [`MXNetShim`](https://thinc.ai/docs/api-model#shims)      | ✅              |

1. DLPack support in TensorFlow is now
   [available](<(https://github.com/tensorflow/tensorflow/issues/24453)>) but
   still experimental.

<!-- TODO:
- Explain concept
- Link off to notebook ​
-->

## Models for trainable components {#components}

- Interaction with `predict`, `get_loss` and `set_annotations`
- Initialization life-cycle with `begin_training`.
- Link to relation extraction notebook.

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
