---
title: Morphologizer
tag: class
source: spacy/pipeline/morphologizer.pyx
new: 3
---

A trainable pipeline component to predict morphological features. This class is
a subclass of `Pipe` and follows the same API. The component is also available
via the string name `"morphologizer"`. After initialization, it is typically
added to the processing pipeline using [`nlp.add_pipe`](/api/language#add_pipe).

## Default config {#config}

This is the default configuration used to initialize the model powering the
pipeline component. See the [model architectures](/api/architectures)
documentation for details on the architectures and their arguments and
hyperparameters. To learn more about how to customize the config and train
custom models, check out the [training config](/usage/training#config) docs.

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/defaults/morphologizer_defaults.cfg
```
