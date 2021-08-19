# Listeners

1. [Overview](#1-overview)
   - [A. Initialization](#1a-initialization)
   - [B. Internal communication](#1b-internal-communication)

## 1. Overview

Trainable spaCy components typically use some sort of `tok2vec` layer as part of the `model` definition.
This `tok2vec` layer produces embeddings and is either a standard `Tok2Vec` layer, or a Transformer-based one.
Both versions can be used either inline/standalone, which means that they are defined and used
by only one specific component (e.g. NER), or [shared](https://spacy.io/usage/embeddings-transformers#embedding-layers),
in which case the `Tok2Vec` becomes a separate component that can
feed embeddings to multiple components downstream, using a listener-pattern.

| Type        | Usage      | Architecture                                                                                       |
| ----------- | ---------- | -------------------------------------------------------------------------------------------------- |
| Tok2Vec     | standalone | [`spacy.Tok2Vec`](https://spacy.io/api/architectures#Tok2Vec)                                      |
| Tok2Vec     | listener   | [`spacy.Tok2VecListener`](https://spacy.io/api/architectures#Tok2VecListener)                      |
| Transformer | standalone | [`spacy-transformers.Tok2VecTransformer`](https://spacy.io/api/architectures#Tok2VecTransformer)   |
| Transformer | listener   | [`spacy-transformers.TransformerListener`](https://spacy.io/api/architectures#TransformerListener) |

Here we discuss the listener pattern and its implementation in code in more detail.

### 1A. Initialization

To allow sharing a `tok2vec` layer, a separate `tok2vec` component needs to be defined in the config:

```
[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"
```

A listener can then be set up by making sure the correct `upstream` name is defined, referring to the
name of the Tok2Vec component (or `*` as a wildcard):

```
[components.ner.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
upstream = "tok2vec"
```

When an [`nlp`](https://github.com/explosion/spaCy/blob/master/extra/DEVELOPER_DOCS/Language.md) object is
initialized or deserialized, it will make sure to link each `tok2vec` component to its listeners. This is
implemented in the method `nlp._link_components` which loops over each
component in the pipeline and call `find_listeners` on a component if it's defined.
The [`tok2vec` component](https://github.com/explosion/spaCy/blob/master/spacy/pipeline/tok2vec.py)'s implementation
of this `find_listener` method will
specifically identify sublayers of a model definition that are of type `Tok2VecListener` with a matching
upstream name and will then add that listener to the internal `self.listener_map`.

If it's a Transformer-based pipeline, a
[`transformer` component](https://github.com/explosion/spacy-transformers/blob/master/spacy_transformers/pipeline_component.py)
has a similar implementation but will specifically look for `TransformerListener` sublayers of downstream components.

Typically, the output dimension `nO` of a listener's model equals the `nO` (or `width`) of the upstream embedding layer.
For a standard `Tok2Vec`-based components, this is typically known up-front and defined as such in the config:

```
[components.ner.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode.width}
```

A `transformer` component however typically only knows its `nO` dimension after the HuggingFace transformer
is set with the function `model.attrs["set_transformer"]`, implemented by `set_pytorch_transformer`.
This is why, upon linking of the transformer listeners, the `transformer` component also makes sure to set
the listener's output dimension correctly.

This dimension inference needs to also happen with resumed/frozen components, which means that for some CLI
commands (`assemble` and `train`), we need to call `nlp._link_components` even before initializing the `nlp`
object. To cover all use-cases and avoid negative side effects, the code base ensures that performing the
linking twice is not harmful.

[comment]: <> (TODO: empty initialization )

[comment]: <> ("The Tok2Vec listener did not receive any valid input from an upstream component.")

### 1B. Internal communication

The internal communication between a listener and its downstream components is organized by sending and 
receiving information across the components. 

#### During training

[comment]: <> (`nlp.update` batches the data and sends each batch)

The `tok2vec` or `transformer` component runs first and calculates 
the embeddings for a given batch of input documents, either in the `predict` or the `update` method. These 
embeddings are then sent to the listeners by calling their `receive` function and uniquely identifying the 
batch of documents with a `batch_id`. Only one such batch is kept in memory for each listener. Then, when the 
downstream component runs and the listener should produce results, it verifies whether the given batch of documents 
matches the `batch_id` it has in memory. If not, one of two errors is raised: `E953` if a different batch is in 
memory, or the dreaded `E954` if no batch is in memory at all. If the batch ID does match, the results from 
memory are produced.


