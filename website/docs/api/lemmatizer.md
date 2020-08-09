---
title: Lemmatizer
tag: class
source: spacy/pipeline/lemmatizer.py
new: 3
teaser: 'Pipeline component for lemmatization'
api_base_class: /api/pipe
api_string_name: lemmatizer
api_trainable: false
---

Component for assigning base forms to tokens using rules based on part-of-speech
tags, or lookup tables. Functionality to train the component is coming soon.
Different [`Language`](/api/language) subclasses can implement their own
lemmatizer components via
[language-specific factories](/usage/processing-pipelines#factories-language).
The default data used is provided by the
[`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data)
extension package.

<Infobox variant="warning" title="New in v3.0">

As of v3.0, the `Lemmatizer` is a **standalone pipeline component** that can be
added to your pipeline, and not a hidden part of the vocab that runs behind the
scenes. This makes it easier to customize how lemmas should be assigned in your
pipeline.

If the lemmatization mode is set to `"rule"` and requires part-of-speech tags to
be assigned, make sure a [`Tagger`](/api/tagger) or another component assigning
tags is available in the pipeline and runs _before_ the lemmatizer.

</Infobox>

## Config and implementation

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config).

For examples of the lookups data formats used by the lookup and rule-based
lemmatizers, see the
[`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data) repo.

> #### Example
>
> ```python
> config = {"mode": "rule"}
> nlp.add_pipe("lemmatizer", config=config)
> ```

| Setting     | Type                                       | Description                                                                                                                                                                            | Default    |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `mode`      | str                                        | The lemmatizer mode, e.g. `"lookup"` or `"rule"`.                                                                                                                                      | `"lookup"` |
| `lookups`   | [`Lookups`](/api/lookups)                  | The lookups object containing the tables such as `"lemma_rules"`, `"lemma_index"`, `"lemma_exc"` and `"lemma_lookup"`. If `None`, default tables are loaded from `spacy-lookups-data`. | `None`     |
| `overwrite` | bool                                       | Whether to overwrite existing lemmas.                                                                                                                                                  | `False`    |
| `model`     | [`Model`](https://thinc.ai/docs/api-model) | **Not yet implemented:** the model to use.                                                                                                                                             | `None`     |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/lemmatizer.py
```

## Lemmatizer.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> lemmatizer = nlp.add_pipe("lemmatizer")
>
> # Construction via add_pipe with custom settings
> config = {"mode": "rule", overwrite=True}
> lemmatizer = nlp.add_pipe("lemmatizer", config=config)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

| Name           | Type                                       | Description                                                                                                                              |
| -------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`        | [`Vocab`](/api/vocab)                      | The vocab.                                                                                                                               |
| `model`        | [`Model`](https://thinc.ai/docs/api-model) | A model (not yet implemented).                                                                                                           |
| `name`         | str                                        | String name of the component instance. Used to add entries to the `losses` during training.                                              |
| _keyword-only_ |                                            |                                                                                                                                          |
| mode           | str                                        | The lemmatizer mode, e.g. `"lookup"` or `"rule"`. Defaults to `"lookup"`.                                                                |
| lookups        | [`Lookups`](/api/lookups)                  | A lookups object containing the tables such as `"lemma_rules"`, `"lemma_index"`, `"lemma_exc"` and `"lemma_lookup"`. Defaults to `None`. |
| overwrite      | bool                                       | Whether to overwrite existing lemmas.                                                                                                    |

## Lemmatizer.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> lemmatizer = nlp.add_pipe("lemmatizer")
> # This usually happens under the hood
> processed = lemmatizer(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## Lemmatizer.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("lemmatizer")
> for doc in lemmatizer.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                            |
| -------------- | --------------- | ------------------------------------------------------ |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                 |
| _keyword-only_ |                 |                                                        |
| `batch_size`   | int             | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**     | `Doc`           | Processed documents in the order of the original text. |

## Lemmatizer.lookup_lemmatize {#lookup_lemmatize tag="method"}

Lemmatize a token using a lookup-based approach. If no lemma is found, the
original string is returned. Languages can provide a
[lookup table](/usage/adding-languages#lemmatizer) via the `Lookups`.

| Name        | Type                  | Description                           |
| ----------- | --------------------- | ------------------------------------- |
| `token`     | [`Token`](/api/token) | The token to lemmatize.               |
| **RETURNS** | `List[str]`           | A list containing one or more lemmas. |

## Lemmatizer.rule_lemmatize {#rule_lemmatize tag="method"}

Lemmatize a token using a rule-based approach. Typically relies on POS tags.

| Name        | Type                  | Description                           |
| ----------- | --------------------- | ------------------------------------- |
| `token`     | [`Token`](/api/token) | The token to lemmatize.               |
| **RETURNS** | `List[str]`           | A list containing one or more lemmas. |

## Lemmatizer.is_base_form {#is_base_form tag="method"}

Check whether we're dealing with an uninflected paradigm, so we can avoid
lemmatization entirely.

| Name        | Type                  | Description                                                                                             |
| ----------- | --------------------- | ------------------------------------------------------------------------------------------------------- |
| `token`     | [`Token`](/api/token) | The token to analyze.                                                                                   |
| **RETURNS** | bool                  | Whether the token's attributes (e.g., part-of-speech tag, morphological features) describe a base form. |

## Lemmatizer.get_lookups_config {#get_lookups_config tag="classmethod"}

Returns the lookups configuration settings for a given mode for use in
[`Lemmatizer.load_lookups`](#load_lookups).

| Name        | Type | Description                                       |
| ----------- | ---- | ------------------------------------------------- |
| `mode`      | str  | The lemmatizer mode.                              |
| **RETURNS** | dict | The lookups configuration settings for this mode. |

## Lemmatizer.load_lookups {#load_lookups tag="classmethod"}

Load and validate lookups tables. If the provided lookups is `None`, load the
default lookups tables according to the language and mode settings. Confirm that
all required tables for the language and mode are present.

| Name        | Type                      | Description                                                                  |
| ----------- | ------------------------- | ---------------------------------------------------------------------------- |
| `lang`      | str                       | The language.                                                                |
| `mode`      | str                       | The lemmatizer mode.                                                         |
| `lookups`   | [`Lookups`](/api/lookups) | The provided lookups, may be `None` if the default lookups should be loaded. |
| **RETURNS** | [`Lookups`](/api/lookups) | The lookups object.                                                          |

## Lemmatizer.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("lemmatizer")
> lemmatizer.to_disk("/path/to/lemmatizer")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## Lemmatizer.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("lemmatizer")
> lemmatizer.from_disk("/path/to/lemmatizer")
> ```

| Name           | Type            | Description                                                                |
| -------------- | --------------- | -------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                            |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `Lemmatizer`    | The modified `Lemmatizer` object.                                          |

## Lemmatizer.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> lemmatizer = nlp.add_pipe("lemmatizer")
> lemmatizer_bytes = lemmatizer.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the `Lemmatizer` object.                           |

## Lemmatizer.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> lemmatizer_bytes = lemmatizer.to_bytes()
> lemmatizer = nlp.add_pipe("lemmatizer")
> lemmatizer.from_bytes(lemmatizer_bytes)
> ```

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| `bytes_data`   | bytes           | The data to load from.                                                    |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | `Lemmatizer`    | The `Lemmatizer` object.                                                  |

## Lemmatizer.mode {#mode tag="property"}

The lemmatizer mode.

| Name        | Type  | Description          |
| ----------- | ----- | -------------------- |
| **RETURNS** | `str` | The lemmatizer mode. |

## Attributes {#attributes}

| Name      | Type                              | Description         |
| --------- | --------------------------------- | ------------------- |
| `vocab`   | The shared [`Vocab`](/api/vocab). |
| `lookups` | [`Lookups`](/api/lookups)         | The lookups object. |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = lemmatizer.to_disk("/path", exclude=["vocab"])
> ```

| Name      | Description                                          |
| --------- | ---------------------------------------------------- |
| `vocab`   | The shared [`Vocab`](/api/vocab).                    |
| `lookups` | The lookups. You usually don't want to exclude this. |
