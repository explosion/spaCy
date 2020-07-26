---
title: SentenceRecognizer
tag: class
source: spacy/pipeline/senter.pyx
new: 3
---

A trainable pipeline component for sentence segmentation. For a simpler,
ruse-based strategy, see the [`Sentencizer`](/api/sentencizer). This class is a
subclass of `Pipe` and follows the same API. The component is also available via
the string name `"senter"`.

## Implementation and defaults {#implementation}

See the [model architectures](/api/architectures) documentation for details on
the architectures and their arguments and hyperparameters. To learn more about
how to customize the config and train custom models, check out the
[training config](/usage/training#config) docs.

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/senter.pyx
```

## SentenceRecognizer.\_\_init\_\_ {#init tag="method"}

Initialize the sentence recognizer.

> #### Example
>
> ```python
> # Construction via add_pipe
> senter = nlp.add_pipe("senter")
> ```

<!-- TODO: document, similar to other trainable pipeline components -->
