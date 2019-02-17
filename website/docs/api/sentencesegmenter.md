---
title: SentenceSegmenter
tag: class
source: spacy/pipeline.pyx
---

A simple spaCy hook, to allow custom sentence boundary detection logic that
doesn't require the dependency parse. By default, sentence segmentation is
performed by the [`DependencyParser`](/api/dependencyparser), so the
`SentenceSegmenter` lets you implement a simpler, rule-based strategy that
doesn't require a statistical model to be loaded. The component is also
available via the string name `"sentencizer"`. After initialization, it is
typically added to the processing pipeline using
[`nlp.add_pipe`](/api/language#add_pipe).

## SentenceSegmenter.\_\_init\_\_ {#init tag="method"}

Initialize the sentence segmenter. To change the sentence boundary detection
strategy, pass a generator function `strategy` on initialization, or assign a
new strategy to the `.strategy` attribute. Sentence detection strategies should
be generators that take `Doc` objects and yield `Span` objects for each
sentence.

> #### Example
>
> ```python
> # Construction via create_pipe
> sentencizer = nlp.create_pipe("sentencizer")
>
> # Construction from class
> from spacy.pipeline import SentenceSegmenter
> sentencizer = SentenceSegmenter(nlp.vocab)
> ```

| Name        | Type                | Description                                                 |
| ----------- | ------------------- | ----------------------------------------------------------- |
| `vocab`     | `Vocab`             | The shared vocabulary.                                      |
| `strategy`  | unicode / callable  | The segmentation strategy to use. Defaults to `"on_punct"`. |
| **RETURNS** | `SentenceSegmenter` | The newly constructed object.                               |

## SentenceSegmenter.\_\_call\_\_ {#call tag="method"}

Apply the sentence segmenter on a `Doc`. Typically, this happens automatically
after the component has been added to the pipeline using
[`nlp.add_pipe`](/api/language#add_pipe).

> #### Example
>
> ```python
> from spacy.lang.en import English
>
> nlp = English()
> sentencizer = nlp.create_pipe("sentencizer")
> nlp.add_pipe(sentencizer)
> doc = nlp(u"This is a sentence. This is another sentence.")
> assert list(doc.sents) == 2
> ```

| Name        | Type  | Description                                                  |
| ----------- | ----- | ------------------------------------------------------------ |
| `doc`       | `Doc` | The `Doc` object to process, e.g. the `Doc` in the pipeline. |
| **RETURNS** | `Doc` | The modified `Doc` with added sentence boundaries.           |

## SentenceSegmenter.split_on_punct {#split_on_punct tag="staticmethod"}

Split the `Doc` on punctuation characters `.`, `!` and `?`. This is the default
strategy used by the `SentenceSegmenter.`

| Name       | Type   | Description                    |
| ---------- | ------ | ------------------------------ |
| `doc`      | `Doc`  | The `Doc` object to process.   |
| **YIELDS** | `Span` | The sentences in the document. |

## Attributes {#attributes}

| Name       | Type     | Description                                                         |
| ---------- | -------- | ------------------------------------------------------------------- |
| `strategy` | callable | The segmentation strategy. Can be overwritten after initialization. |
