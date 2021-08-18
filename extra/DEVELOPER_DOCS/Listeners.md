# Listeners

Trainable spaCy components typically use some sort of `tok2vec` layer as part of the `model` definition.
This `tok2vec` layer produces embeddings and is either a standard `Tok2Vec` layer, or a Transformer-based one.
Both versions can be used either inline/standalone, which means that they are defined and used
by only one specific component (e.g. NER), or [shared](https://spacy.io/usage/embeddings-transformers#embedding-layers), in which case the `Tok2Vec` becomes a separate component that can
feed embeddings to multiple components downstream, using a listener-pattern.

| Type        | Usage      | Architecture                                                                                         |
| ----------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| Tok2Vec     | standalone | [`spacy.Tok2Vec`](https://spacy.io/api/architectures#Tok2Vec)                                        |
| Tok2Vec     | listener   | [`spacy.Tok2VecListener`](https://spacy.io/api/architectures#Tok2VecListener)                        |
| Transformer | standalone | [`spacy-transformers.Tok2VecTransformer`](https://spacy.io/api/architectures#Tok2VecTransformer)     |
| Transformer | listener   | [`spacy-transformers.TransformerListener`](https://spacy.io/api/architectures#TransformerListener) |

Here we discuss the listener pattern and its implementation in code in more detail.

1. [Overview](#1-overview)
   - [A. Pipeline component](#1a-pipeline-component)
   - [B. Model architectures](#1b-model-architectures)

## 1. Overview

### 1A. Pipeline component

class Tok2Vec(TrainablePipe)

> Reference: `spacy/pipeline/tok2vec.py`

### 1B. Model architectures

class Tok2VecListener

> Reference: `spacy/ml/models/tok2vec.py`
>
> Reference: `spacy_transformers/architectures.py`
