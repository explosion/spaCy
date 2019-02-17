---
title: Models
teaser: Downloadable statistical models for spaCy to predict linguistic features
menu:
  - ['Quickstart', 'quickstart']
  - ['Model Architecture', 'architecture']
  - ['Conventions', 'conventions']
---

spaCy v2.0 features new neural models for **tagging**, **parsing** and **entity
recognition**. The models have been designed and implemented from scratch
specifically for spaCy, to give you an unmatched balance of speed, size and
accuracy. A novel bloom embedding strategy with subword features is used to
support huge vocabularies in tiny tables. Convolutional layers with residual
connections, layer normalization and maxout non-linearity are used, giving much
better efficiency than the standard BiLSTM solution. For more details, see the
notes on the [model architecture](#architecture).

The parser and NER use an imitation learning objective to deliver **accuracy
in-line with the latest research systems**, even when evaluated from raw text.
With these innovations, spaCy v2.0's models are **10× smaller**, **20% more
accurate**, and **even cheaper to run** than the previous generation.

### Quickstart {hidden="true"}

import QuickstartModels from 'widgets/quickstart-models.js'

<QuickstartModels title="Quickstart" id="quickstart" description="Install a default model, get the code to load it from within spaCy and an example to test it. For more options, see the section on available models below." />

<Infobox title="📖 Installation and usage">

For more details on how to use models with spaCy, see the
[usage guide on models](/usage/models).

</Infobox>

## Model architecture {#architecture}

spaCy's statistical models have been custom-designed to give a high-performance
mix of speed and accuracy. The current architecture hasn't been published yet,
but in the meantime we prepared a video that explains how the models work, with
particular focus on NER.

<YouTube id="sqDHBH9IjRU" />

The parsing model is a blend of recent results. The two recent inspirations have
been the work of Eli Klipperwasser and Yoav Goldberg at Bar Ilan[^1], and the
SyntaxNet team from Google. The foundation of the parser is still based on the
work of Joakim Nivre[^2], who introduced the transition-based framework[^3], the
arc-eager transition system, and the imitation learning objective. The model is
implemented using [Thinc](https://github.com/explosion/thinc), spaCy's machine
learning library. We first predict context-sensitive vectors for each word in
the input:

```python
(embed_lower | embed_prefix | embed_suffix | embed_shape)
    >> Maxout(token_width)
    >> convolution ** 4
```

This convolutional layer is shared between the tagger, parser and NER, and will
also be shared by the future neural lemmatizer. Because the parser shares these
layers with the tagger, the parser does not require tag features. I got this
trick from David Weiss's "Stack Combination" paper[^4].

To boost the representation, the tagger actually predicts a "super tag" with
POS, morphology and dependency label[^5]. The tagger predicts these supertags by
adding a softmax layer onto the convolutional layer – so, we're teaching the
convolutional layer to give us a representation that's one affine transform from
this informative lexical information. This is obviously good for the parser
(which backprops to the convolutions, too). The parser model makes a state
vector by concatenating the vector representations for its context tokens. The
current context tokens:

| Context tokens                                                                     | Description                                                                 |
| ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `S0`, `S1`, `S2`                                                                   | Top three words on the stack.                                               |
| `B0`, `B1`                                                                         | First two words of the buffer.                                              |
| `S0L1`, `S1L1`, `S2L1`, `B0L1`, `B1L1`<br />`S0L2`, `S1L2`, `S2L2`, `B0L2`, `B1L2` | Leftmost and second leftmost children of `S0`, `S1`, `S2`, `B0` and `B1`.   |
| `S0R1`, `S1R1`, `S2R1`, `B0R1`, `B1R1`<br />`S0R2`, `S1R2`, `S2R2`, `B0R2`, `B1R2` | Rightmost and second rightmost children of `S0`, `S1`, `S2`, `B0` and `B1`. |

This makes the state vector quite long: `13*T`, where `T` is the token vector
width (128 is working well). Fortunately, there's a way to structure the
computation to save some expense (and make it more GPU-friendly).

The parser typically visits `2*N` states for a sentence of length `N` (although
it may visit more, if it back-tracks with a non-monotonic transition[^4]). A
naive implementation would require `2*N (B, 13*T) @ (13*T, H)` matrix
multiplications for a batch of size `B`. We can instead perform one
`(B*N, T) @ (T, 13*H)` multiplication, to pre-compute the hidden weights for
each positional feature with respect to the words in the batch. (Note that our
token vectors come from the CNN — so we can't play this trick over the
vocabulary. That's how Stanford's NN parser[^3] works — and why its model is so
big.)

This pre-computation strategy allows a nice compromise between GPU-friendliness
and implementation simplicity. The CNN and the wide lower layer are computed on
the GPU, and then the precomputed hidden weights are moved to the CPU, before we
start the transition-based parsing process. This makes a lot of things much
easier. We don't have to worry about variable-length batch sizes, and we don't
have to implement the dynamic oracle in CUDA to train.

Currently the parser's loss function is multi-label log loss[^6], as the dynamic
oracle allows multiple states to be 0 cost. This is defined as follows, where
`gZ` is the sum of the scores assigned to gold classes:

```python
(exp(score) / Z) - (exp(score) / gZ)
```

<Infobox title="Bibliography">

1. [Simple and Accurate Dependency Parsing Using Bidirectional LSTM Feature Representations {#fn-1}](https://www.semanticscholar.org/paper/Simple-and-Accurate-Dependency-Parsing-Using-Bidir-Kiperwasser-Goldberg/3cf31ecb2724b5088783d7c96a5fc0d5604cbf41).
   Eliyahu Kiperwasser, Yoav Goldberg. (2016)
2. [A Dynamic Oracle for Arc-Eager Dependency Parsing {#fn-2}](https://www.semanticscholar.org/paper/A-Dynamic-Oracle-for-Arc-Eager-Dependency-Parsing-Goldberg-Nivre/22697256ec19ecc3e14fcfc63624a44cf9c22df4).
   Yoav Goldberg, Joakim Nivre (2012)
3. [Parsing English in 500 Lines of Python {#fn-3}](https://explosion.ai/blog/parsing-english-in-python).
   Matthew Honnibal (2013)
4. [Stack-propagation: Improved Representation Learning for Syntax {#fn-4}](https://www.semanticscholar.org/paper/Stack-propagation-Improved-Representation-Learning-Zhang-Weiss/0c133f79b23e8c680891d2e49a66f0e3d37f1466).
   Yuan Zhang, David Weiss (2016)
5. [Deep multi-task learning with low level tasks supervised at lower layers {#fn-5}](https://www.semanticscholar.org/paper/Deep-multi-task-learning-with-low-level-tasks-supe-S%C3%B8gaard-Goldberg/03ad06583c9721855ccd82c3d969a01360218d86).
   Anders Søgaard, Yoav Goldberg (2016)
6. [An Improved Non-monotonic Transition System for Dependency Parsing {#fn-6}](https://www.semanticscholar.org/paper/An-Improved-Non-monotonic-Transition-System-for-De-Honnibal-Johnson/4094cee47ade13b77b5ab4d2e6cb9dd2b8a2917c).
   Matthew Honnibal, Mark Johnson (2015)
7. [A Fast and Accurate Dependency Parser using Neural Networks {#fn-7}](http://cs.stanford.edu/people/danqi/papers/emnlp2014.pdf).
   Danqi Cheng, Christopher D. Manning (2014)
8. [Parsing the Wall Street Journal using a Lexical-Functional Grammar and Discriminative Estimation Techniques {#fn-8}](https://www.semanticscholar.org/paper/Parsing-the-Wall-Street-Journal-using-a-Lexical-Fu-Riezler-King/0ad07862a91cd59b7eb5de38267e47725a62b8b2).
   Stefan Riezler et al. (2002)

</Infobox>

## Model naming conventions {#conventions}

In general, spaCy expects all model packages to follow the naming convention of
`[lang`\_[name]]. For spaCy's models, we also chose to divide the name into
three components:

1. **Type:** Model capabilities (e.g. `core` for general-purpose model with
   vocabulary, syntax, entities and word vectors, or `depent` for only vocab,
   syntax and entities).
2. **Genre:** Type of text the model is trained on, e.g. `web` or `news`.
3. **Size:** Model size indicator, `sm`, `md` or `lg`.

For example, `en_core_web_sm` is a small English model trained on written web
text (blogs, news, comments), that includes vocabulary, vectors, syntax and
entities.

### Model versioning {#model-versioning}

Additionally, the model versioning reflects both the compatibility with spaCy,
as well as the major and minor model version. A model version `a.b.c` translates
to:

- `a`: **spaCy major version**. For example, `2` for spaCy v2.x.
- `b`: **Model major version**. Models with a different major version can't be
  loaded by the same code. For example, changing the width of the model, adding
  hidden layers or changing the activation changes the model major version.
- `c`: **Model minor version**. Same model structure, but different parameter
  values, e.g. from being trained on different data, for different numbers of
  iterations, etc.

For a detailed compatibility overview, see the
[`compatibility.json`](https://github.com/explosion/spacy-models/tree/master/compatibility.json)
in the models repository. This is also the source of spaCy's internal
compatibility check, performed when you run the [`download`](/api/cli#download)
command.
