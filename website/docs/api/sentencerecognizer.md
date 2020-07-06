---
title: SentenceRecognizer
tag: class
source: spacy/pipeline/pipes.pyx
new: 3
---

A trainable pipeline component for sentence segmentation. For a simpler,
ruse-based strategy, see the [`Sentencizer`](/api/sentencizer). This class is a
subclass of `Pipe` and follows the same API. The component is also available via
the string name `"senter"`. After initialization, it is typically added to the
processing pipeline using [`nlp.add_pipe`](/api/language#add_pipe).

## SentenceRecognizer.\_\_init\_\_ {#init tag="method"}

Initialize the sentence recognizer.

> #### Example
>
> ```python
> # Construction via create_pipe
> senter = nlp.create_pipe("senter")
>
> # Construction from class
> from spacy.pipeline import SentenceRecognizer
> senter = SentenceRecognizer()
> ```

<!-- TODO: document, similar to other trainable pipeline components -->
