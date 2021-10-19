---
title: Sentencizer
tag: class
source: spacy/pipeline/sentencizer.pyx
teaser: 'Pipeline component for rule-based sentence boundary detection'
api_string_name: sentencizer
api_trainable: false
---

A simple pipeline component to allow custom sentence boundary detection logic
that doesn't require the dependency parse. By default, sentence segmentation is
performed by the [`DependencyParser`](/api/dependencyparser), so the
`Sentencizer` lets you implement a simpler, rule-based strategy that doesn't
require a statistical model to be loaded.

## Assigned Attributes {#assigned-attributes}

Calculated values will be assigned to `Token.is_sent_start`. The resulting
sentences can be accessed using `Doc.sents`.

| Location              | Value                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `Token.is_sent_start` | A boolean value indicating whether the token starts a sentence. This will be either `True` or `False` for all tokens. ~~bool~~ |
| `Doc.sents`           | An iterator over sentences in the `Doc`, determined by `Token.is_sent_start` values. ~~Iterator[Span]~~                        |

## Config and implementation {#config}

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config).

> #### Example
>
> ```python
> config = {"punct_chars": None}
> nlp.add_pipe("sentencizer", config=config)
> ```

| Setting                                  | Description                                                                                                                                            |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `punct_chars`                            | Optional custom list of punctuation characters that mark sentence ends. See below for defaults if not set. Defaults to `None`. ~~Optional[List[str]]~~ | `None` |
| `overwrite` <Tag variant="new">3.2</Tag> | Whether existing annotation is overwritten. Defaults to `False`. ~~bool~~                                                                              |
| `scorer` <Tag variant="new">3.2</Tag>    | The scoring method. Defaults to [`Scorer.score_spans`](/api/scorer#score_spans) for the attribute `"sents"` ~~Optional[Callable]~~                     |

```python
%%GITHUB_SPACY/spacy/pipeline/sentencizer.pyx
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

| Name                                     | Description                                                                                                                        |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| _keyword-only_                           |                                                                                                                                    |
| `punct_chars`                            | Optional custom list of punctuation characters that mark sentence ends. See below for defaults. ~~Optional[List[str]]~~            |
| `overwrite` <Tag variant="new">3.2</Tag> | Whether existing annotation is overwritten. Defaults to `False`. ~~bool~~                                                          |
| `scorer` <Tag variant="new">3.2</Tag>    | The scoring method. Defaults to [`Scorer.score_spans`](/api/scorer#score_spans) for the attribute `"sents"` ~~Optional[Callable]~~ |

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

| Name        | Description                                                          |
| ----------- | -------------------------------------------------------------------- |
| `doc`       | The `Doc` object to process, e.g. the `Doc` in the pipeline. ~~Doc~~ |
| **RETURNS** | The modified `Doc` with added sentence boundaries. ~~Doc~~           |

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

| Name           | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `stream`       | A stream of documents. ~~Iterable[Doc]~~                      |
| _keyword-only_ |                                                               |
| `batch_size`   | The number of documents to buffer. Defaults to `128`. ~~int~~ |
| **YIELDS**     | The processed documents in order. ~~Doc~~                     |

## Sentencizer.to_disk {#to_disk tag="method"}

Save the sentencizer settings (punctuation characters) to a directory. Will
create a file `sentencizer.json`. This also happens automatically when you save
an `nlp` object with a sentencizer added to its pipeline.

> #### Example
>
> ```python
> config = {"punct_chars": [".", "?", "!", "。"]}
> sentencizer = nlp.add_pipe("sentencizer", config=config)
> sentencizer.to_disk("/path/to/sentencizer.json")
> ```

| Name   | Description                                                                                                                                |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path` | A path to a JSON file, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |

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

| Name        | Description                                                                                     |
| ----------- | ----------------------------------------------------------------------------------------------- |
| `path`      | A path to a JSON file. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| **RETURNS** | The modified `Sentencizer` object. ~~Sentencizer~~                                              |

## Sentencizer.to_bytes {#to_bytes tag="method"}

Serialize the sentencizer settings to a bytestring.

> #### Example
>
> ```python
> config = {"punct_chars": [".", "?", "!", "。"]}
> sentencizer = nlp.add_pipe("sentencizer", config=config)
> sentencizer_bytes = sentencizer.to_bytes()
> ```

| Name        | Description                    |
| ----------- | ------------------------------ |
| **RETURNS** | The serialized data. ~~bytes~~ |

## Sentencizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> sentencizer_bytes = sentencizer.to_bytes()
> sentencizer = nlp.add_pipe("sentencizer")
> sentencizer.from_bytes(sentencizer_bytes)
> ```

| Name         | Description                                        |
| ------------ | -------------------------------------------------- |
| `bytes_data` | The bytestring to load. ~~bytes~~                  |
| **RETURNS**  | The modified `Sentencizer` object. ~~Sentencizer~~ |
