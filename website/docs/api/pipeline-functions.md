---
title: Pipeline Functions
teaser: Other built-in pipeline components and helpers
source: spacy/pipeline/functions.py
menu:
  - ['merge_noun_chunks', 'merge_noun_chunks']
  - ['merge_entities', 'merge_entities']
  - ['merge_subtokens', 'merge_subtokens']
  - ['token_splitter', 'token_splitter']
---

## merge_noun_chunks {#merge_noun_chunks tag="function"}

Merge noun chunks into a single token. Also available via the string name
`"merge_noun_chunks"`.

> #### Example
>
> ```python
> texts = [t.text for t in nlp("I have a blue car")]
> assert texts == ["I", "have", "a", "blue", "car"]
>
> nlp.add_pipe("merge_noun_chunks")
> texts = [t.text for t in nlp("I have a blue car")]
> assert texts == ["I", "have", "a blue car"]
> ```

<Infobox variant="warning">

Since noun chunks require part-of-speech tags and the dependency parse, make
sure to add this component _after_ the `"tagger"` and `"parser"` components. By
default, `nlp.add_pipe` will add components to the end of the pipeline and after
all other components.

</Infobox>

| Name        | Description                                                          |
| ----------- | -------------------------------------------------------------------- |
| `doc`       | The `Doc` object to process, e.g. the `Doc` in the pipeline. ~~Doc~~ |
| **RETURNS** | The modified `Doc` with merged noun chunks. ~~Doc~~                  |

## merge_entities {#merge_entities tag="function"}

Merge named entities into a single token. Also available via the string name
`"merge_entities"`.

> #### Example
>
> ```python
> texts = [t.text for t in nlp("I like David Bowie")]
> assert texts == ["I", "like", "David", "Bowie"]
>
> nlp.add_pipe("merge_entities")
>
> texts = [t.text for t in nlp("I like David Bowie")]
> assert texts == ["I", "like", "David Bowie"]
> ```

<Infobox variant="warning">

Since named entities are set by the entity recognizer, make sure to add this
component _after_ the `"ner"` component. By default, `nlp.add_pipe` will add
components to the end of the pipeline and after all other components.

</Infobox>

| Name        | Description                                                          |
| ----------- | -------------------------------------------------------------------- |
| `doc`       | The `Doc` object to process, e.g. the `Doc` in the pipeline. ~~Doc~~ |
| **RETURNS** | The modified `Doc` with merged entities. ~~Doc~~                     |

## merge_subtokens {#merge_subtokens tag="function" new="2.1"}

Merge subtokens into a single token. Also available via the string name
`"merge_subtokens"`. As of v2.1, the parser is able to predict "subtokens" that
should be merged into one single token later on. This is especially relevant for
languages like Chinese, Japanese or Korean, where a "word" isn't defined as a
whitespace-delimited sequence of characters. Under the hood, this component uses
the [`Matcher`](/api/matcher) to find sequences of tokens with the dependency
label `"subtok"` and then merges them into a single token.

> #### Example
>
> Note that this example assumes a custom Chinese model that oversegments and
> was trained to predict subtokens.
>
> ```python
> doc = nlp("拜托")
> print([(token.text, token.dep_) for token in doc])
> # [('拜', 'subtok'), ('托', 'subtok')]
>
> nlp.add_pipe("merge_subtokens")
> doc = nlp("拜托")
> print([token.text for token in doc])
> # ['拜托']
> ```

<Infobox variant="warning">

Since subtokens are set by the parser, make sure to add this component _after_
the `"parser"` component. By default, `nlp.add_pipe` will add components to the
end of the pipeline and after all other components.

</Infobox>

| Name        | Description                                                          |
| ----------- | -------------------------------------------------------------------- |
| `doc`       | The `Doc` object to process, e.g. the `Doc` in the pipeline. ~~Doc~~ |
| `label`     | The subtoken dependency label. Defaults to `"subtok"`. ~~str~~       |
| **RETURNS** | The modified `Doc` with merged subtokens. ~~Doc~~                    |

## token_splitter {#token_splitter tag="function" new="3.0"}

Split tokens longer than a minimum length into shorter tokens. Intended for use
with transformer pipelines where long spaCy tokens lead to input text that
exceed the transformer model max length.

> #### Example
>
> ```python
> config = {"min_length": 20, "split_length": 5}
> nlp.add_pipe("token_splitter", config=config, first=True)
> doc = nlp("aaaaabbbbbcccccdddddee")
> print([token.text for token in doc])
> # ['aaaaa', 'bbbbb', 'ccccc', 'ddddd', 'ee']
> ```

| Setting        | Description                                                           |
| -------------- | --------------------------------------------------------------------- |
| `min_length`   | The minimum length for a token to be split. Defaults to `25`. ~~int~~ |
| `split_length` | The length of the split tokens. Defaults to `5`. ~~int~~              |
| **RETURNS**    | The modified `Doc` with the split tokens. ~~Doc~~                     |

## doc_cleaner {#doc_cleaner tag="function" new="3.2.1"}

Clean up `Doc` attributes. Intended for use at the end of pipelines with
`tok2vec` or `transformer` pipeline components that store tensors and other
values that can require a lot of memory and frequently aren't needed after the
whole pipeline has run.

> #### Example
>
> ```python
> config = {"attrs": {"tensor": None}}
> nlp.add_pipe("doc_cleaner", config=config)
> doc = nlp("text")
> assert doc.tensor is None
> ```

| Setting     | Description                                                                                                                                                                         |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `attrs`     | A dict of the `Doc` attributes and the values to set them to. Defaults to `{"tensor": None, "_.trf_data": None}` to clean up after `tok2vec` and `transformer` components. ~~dict~~ |
| `silent`    | If `False`, show warnings if attributes aren't found or can't be set. Defaults to `True`. ~~bool~~                                                                                  |
| **RETURNS** | The modified `Doc` with the modified attributes. ~~Doc~~                                                                                                                            |
