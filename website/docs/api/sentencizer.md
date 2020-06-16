---
title: Sentencizer
tag: class
source: spacy/pipeline/pipes.pyx
---

A simple pipeline component, to allow custom sentence boundary detection logic
that doesn't require the dependency parse. By default, sentence segmentation is
performed by the [`DependencyParser`](/api/dependencyparser), so the
`Sentencizer` lets you implement a simpler, rule-based strategy that doesn't
require a statistical model to be loaded. The component is also available via
the string name `"sentencizer"`. After initialization, it is typically added to
the processing pipeline using [`nlp.add_pipe`](/api/language#add_pipe).

<Infobox title="Important note" variant="warning">

Compared to the previous `SentenceSegmenter` class, the `Sentencizer` component
doesn't add a hook to `doc.user_hooks["sents"]`. Instead, it iterates over the
tokens in the `Doc` and sets the `Token.is_sent_start` property. The
`SentenceSegmenter` is still available if you import it directly:

```python
from spacy.pipeline import SentenceSegmenter
```

</Infobox>

## Sentencizer.\_\_init\_\_ {#init tag="method"}

Initialize the sentencizer.

> #### Example
>
> ```python
> # Construction via create_pipe
> sentencizer = nlp.create_pipe("sentencizer")
>
> # Construction from class
> from spacy.pipeline import Sentencizer
> sentencizer = Sentencizer()
> ```

| Name          | Type          | Description                                                                                            |
| ------------- | ------------- | ------------------------------------------------------------------------------------------------------ |
| `punct_chars` | list          | Optional custom list of punctuation characters that mark sentence ends. Defaults to `['!', '.', '?', '։', '؟', '۔', '܀', '܁', '܂', '߹', '।', '॥', '၊', '။', '።', '፧', '፨', '᙮', '᜵', '᜶', '᠃', '᠉', '᥄', '᥅', '᪨', '᪩', '᪪', '᪫', '᭚', '᭛', '᭞', '᭟', '᰻', '᰼', '᱾', '᱿', '‼', '‽', '⁇', '⁈', '⁉', '⸮', '⸼', '꓿', '꘎', '꘏', '꛳', '꛷', '꡶', '꡷', '꣎', '꣏', '꤯', '꧈', '꧉', '꩝', '꩞', '꩟', '꫰', '꫱', '꯫', '﹒', '﹖', '﹗', '！', '．', '？', '𐩖', '𐩗', '𑁇', '𑁈', '𑂾', '𑂿', '𑃀', '𑃁', '𑅁', '𑅂', '𑅃', '𑇅', '𑇆', '𑇍', '𑇞', '𑇟', '𑈸', '𑈹', '𑈻', '𑈼', '𑊩', '𑑋', '𑑌', '𑗂', '𑗃', '𑗉', '𑗊', '𑗋', '𑗌', '𑗍', '𑗎', '𑗏', '𑗐', '𑗑', '𑗒', '𑗓', '𑗔', '𑗕', '𑗖', '𑗗', '𑙁', '𑙂', '𑜼', '𑜽', '𑜾', '𑩂', '𑩃', '𑪛', '𑪜', '𑱁', '𑱂', '𖩮', '𖩯', '𖫵', '𖬷', '𖬸', '𖭄', '𛲟', '𝪈', '｡', '。']`. |
| **RETURNS**   | `Sentencizer` | The newly constructed object.                                                                          |

## Sentencizer.\_\_call\_\_ {#call tag="method"}

Apply the sentencizer on a `Doc`. Typically, this happens automatically after
the component has been added to the pipeline using
[`nlp.add_pipe`](/api/language#add_pipe).

> #### Example
>
> ```python
> from spacy.lang.en import English
>
> nlp = English()
> sentencizer = nlp.create_pipe("sentencizer")
> nlp.add_pipe(sentencizer)
> doc = nlp("This is a sentence. This is another sentence.")
> assert len(list(doc.sents)) == 2
> ```

| Name        | Type  | Description                                                  |
| ----------- | ----- | ------------------------------------------------------------ |
| `doc`       | `Doc` | The `Doc` object to process, e.g. the `Doc` in the pipeline. |
| **RETURNS** | `Doc` | The modified `Doc` with added sentence boundaries.           |

## Sentencizer.to_disk {#to_disk tag="method"}

Save the sentencizer settings (punctuation characters) a directory. Will create
a file `sentencizer.json`. This also happens automatically when you save an
`nlp` object with a sentencizer added to its pipeline.

> #### Example
>
> ```python
> sentencizer = Sentencizer(punct_chars=[".", "?", "!", "。"])
> sentencizer.to_disk("/path/to/sentencizer.jsonl")
> ```

| Name   | Type             | Description                                                                                                      |
| ------ | ---------------- | ---------------------------------------------------------------------------------------------------------------- |
| `path` | unicode / `Path` | A path to a file, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |

## Sentencizer.from_disk {#from_disk tag="method"}

Load the sentencizer settings from a file. Expects a JSON file. This also
happens automatically when you load an `nlp` object or model with a sentencizer
added to its pipeline.

> #### Example
>
> ```python
> sentencizer = Sentencizer()
> sentencizer.from_disk("/path/to/sentencizer.json")
> ```

| Name        | Type             | Description                                                                |
| ----------- | ---------------- | -------------------------------------------------------------------------- |
| `path`      | unicode / `Path` | A path to a JSON file. Paths may be either strings or `Path`-like objects. |
| **RETURNS** | `Sentencizer`    | The modified `Sentencizer` object.                                         |

## Sentencizer.to_bytes {#to_bytes tag="method"}

Serialize the sentencizer settings to a bytestring.

> #### Example
>
> ```python
> sentencizer = Sentencizer(punct_chars=[".", "?", "!", "。"])
> sentencizer_bytes = sentencizer.to_bytes()
> ```

| Name        | Type  | Description          |
| ----------- | ----- | -------------------- |
| **RETURNS** | bytes | The serialized data. |

## Sentencizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> sentencizer_bytes = sentencizer.to_bytes()
> sentencizer = Sentencizer()
> sentencizer.from_bytes(sentencizer_bytes)
> ```

| Name         | Type          | Description                        |
| ------------ | ------------- | ---------------------------------- |
| `bytes_data` | bytes         | The bytestring to load.            |
| **RETURNS**  | `Sentencizer` | The modified `Sentencizer` object. |
