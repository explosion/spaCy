---
title: Sentencizer
tag: class
source: spacy/pipeline/sentencizer.pyx
teaser: 'Pipeline component for rule-based sentence boundary detection'
api_base_class: /api/pipe
api_string_name: sentencizer
api_trainable: false
---

A simple pipeline component, to allow custom sentence boundary detection logic
that doesn't require the dependency parse. By default, sentence segmentation is
performed by the [`DependencyParser`](/api/dependencyparser), so the
`Sentencizer` lets you implement a simpler, rule-based strategy that doesn't
require a statistical model to be loaded.

## Config and implementation {#config}

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config).

> #### Example
>
> ```python
> config = {"punct_chars": None}
> nlp.add_pipe("entity_ruler", config=config)
> ```

| Setting       | Type        | Description                                                                                                | Default |
| ------------- | ----------- | ---------------------------------------------------------------------------------------------------------- | ------- |
| `punct_chars` | `List[str]` | Optional custom list of punctuation characters that mark sentence ends. See below for defaults if not set. | `None`  |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/sentencizer.pyx
```

## Sentencizer.\_\_init\_\_ {#init tag="method"}

Initialize the sentencizer.

> #### Example
>
> ```python
> # Construction via add_pipe
> sentencizer = nlp.add_pipe("sentencizer")
>
> # Construction from class
> from spacy.pipeline import Sentencizer
> sentencizer = Sentencizer()
> ```

| Name           | Type        | Description                                                                                     |
| -------------- | ----------- | ----------------------------------------------------------------------------------------------- |
| _keyword-only_ |             |                                                                                                 |
| `punct_chars`  | `List[str]` | Optional custom list of punctuation characters that mark sentence ends. See below for defaults. |

```python
### punct_chars defaults
['!', '.', '?', '։', '؟', '۔', '܀', '܁', '܂', '߹', '।', '॥', '၊', '။', '።',
 '፧', '፨', '᙮', '᜵', '᜶', '᠃', '᠉', '᥄', '᥅', '᪨', '᪩', '᪪', '᪫',
 '᭚', '᭛', '᭞', '᭟', '᰻', '᰼', '᱾', '᱿', '‼', '‽', '⁇', '⁈', '⁉',
 '⸮', '⸼', '꓿', '꘎', '꘏', '꛳', '꛷', '꡶', '꡷', '꣎', '꣏', '꤯', '꧈',
 '꧉', '꩝', '꩞', '꩟', '꫰', '꫱', '꯫', '﹒', '﹖', '﹗', '！', '．', '？',
 '𐩖', '𐩗', '𑁇', '𑁈', '𑂾', '𑂿', '𑃀', '𑃁', '𑅁', '𑅂', '𑅃', '𑇅',
 '𑇆', '𑇍', '𑇞', '𑇟', '𑈸', '𑈹', '𑈻', '𑈼', '𑊩', '𑑋', '𑑌', '𑗂',
 '𑗃', '𑗉', '𑗊', '𑗋', '𑗌', '𑗍', '𑗎', '𑗏', '𑗐', '𑗑', '𑗒', '𑗓',
 '𑗔', '𑗕', '𑗖', '𑗗', '𑙁', '𑙂', '𑜼', '𑜽', '𑜾', '𑩂', '𑩃', '𑪛',
 '𑪜', '𑱁', '𑱂', '𖩮', '𖩯', '𖫵', '𖬷', '𖬸', '𖭄', '𛲟', '𝪈', '｡', '。']
```

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
> nlp.add_pipe("sentencizer")
> doc = nlp("This is a sentence. This is another sentence.")
> assert len(list(doc.sents)) == 2
> ```

| Name        | Type  | Description                                                  |
| ----------- | ----- | ------------------------------------------------------------ |
| `doc`       | `Doc` | The `Doc` object to process, e.g. the `Doc` in the pipeline. |
| **RETURNS** | `Doc` | The modified `Doc` with added sentence boundaries.           |

## Sentencizer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order.

> #### Example
>
> ```python
> sentencizer = nlp.add_pipe("sentencizer")
> for doc in sentencizer.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                           |
| -------------- | --------------- | ----------------------------------------------------- |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                |
| _keyword-only_ |                 |                                                       |
| `batch_size`   | int             | The number of documents to buffer. Defaults to `128`. |
| **YIELDS**     | `Doc`           | The processed documents in order.                     |

## Sentencizer.score {#score tag="method" new="3"}

Score a batch of examples.

> #### Example
>
> ```python
> scores = sentencizer.score(examples)
> ```

| Name        | Type                | Description                                                              |
| ----------- | ------------------- | ------------------------------------------------------------------------ |
| `examples`  | `Iterable[Example]` | The examples to score.                                                   |
| **RETURNS** | `Dict[str, Any]`    | The scores, produced by [`Scorer.score_spans`](/api/scorer#score_spans). |

## Sentencizer.to_disk {#to_disk tag="method"}

Save the sentencizer settings (punctuation characters) a directory. Will create
a file `sentencizer.json`. This also happens automatically when you save an
`nlp` object with a sentencizer added to its pipeline.

> #### Example
>
> ```python
> config = {"punct_chars": [".", "?", "!", "。"]}
> sentencizer = nlp.add_pipe("sentencizer", config=config)
> sentencizer.to_disk("/path/to/sentencizer.json")
> ```

| Name   | Type         | Description                                                                                                           |
| ------ | ------------ | --------------------------------------------------------------------------------------------------------------------- |
| `path` | str / `Path` | A path to a JSON file, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |

## Sentencizer.from_disk {#from_disk tag="method"}

Load the sentencizer settings from a file. Expects a JSON file. This also
happens automatically when you load an `nlp` object or model with a sentencizer
added to its pipeline.

> #### Example
>
> ```python
> sentencizer = nlp.add_pipe("sentencizer")
> sentencizer.from_disk("/path/to/sentencizer.json")
> ```

| Name        | Type          | Description                                                                |
| ----------- | ------------- | -------------------------------------------------------------------------- |
| `path`      | str / `Path`  | A path to a JSON file. Paths may be either strings or `Path`-like objects. |
| **RETURNS** | `Sentencizer` | The modified `Sentencizer` object.                                         |

## Sentencizer.to_bytes {#to_bytes tag="method"}

Serialize the sentencizer settings to a bytestring.

> #### Example
>
> ```python
> config = {"punct_chars": [".", "?", "!", "。"]}
> sentencizer = nlp.add_pipe("sentencizer", config=config)
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
> sentencizer = nlp.add_pipe("sentencizer")
> sentencizer.from_bytes(sentencizer_bytes)
> ```

| Name         | Type          | Description                        |
| ------------ | ------------- | ---------------------------------- |
| `bytes_data` | bytes         | The bytestring to load.            |
| **RETURNS**  | `Sentencizer` | The modified `Sentencizer` object. |
