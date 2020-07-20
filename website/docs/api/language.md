---
title: Language
teaser: A text-processing pipeline
tag: class
source: spacy/language.py
---

Usually you'll load this once per process as `nlp` and pass the instance around
your application. The `Language` class is created when you call
[`spacy.load()`](/api/top-level#spacy.load) and contains the shared vocabulary
and [language data](/usage/adding-languages), optional model data loaded from a
[model package](/models) or a path, and a
[processing pipeline](/usage/processing-pipelines) containing components like
the tagger or parser that are called on a document in order. You can also add
your own processing pipeline components that take a `Doc` object, modify it and
return it.

## Language.\_\_init\_\_ {#init tag="method"}

Initialize a `Language` object.

> #### Example
>
> ```python
> from spacy.vocab import Vocab
> from spacy.language import Language
> nlp = Language(Vocab())
>
> from spacy.lang.en import English
> nlp = English()
> ```

| Name        | Type       | Description                                                                                |
| ----------- | ---------- | ------------------------------------------------------------------------------------------ |
| `vocab`     | `Vocab`    | A `Vocab` object. If `True`, a vocab is created via `Language.Defaults.create_vocab`.      |
| `make_doc`  | callable   | A function that takes text and returns a `Doc` object. Usually a `Tokenizer`.              |
| `meta`      | dict       | Custom meta data for the `Language` class. Is written to by models to add model meta data. |
| **RETURNS** | `Language` | The newly constructed object.                                                              |

## Language.\_\_call\_\_ {#call tag="method"}

Apply the pipeline to some text. The text can span multiple sentences, and can
contain arbitrary whitespace. Alignment into the original string is preserved.

> #### Example
>
> ```python
> doc = nlp("An example sentence. Another sentence.")
> assert (doc[0].text, doc[0].head.tag_) == ("An", "NN")
> ```

| Name        | Type  | Description                                                                       |
| ----------- | ----- | --------------------------------------------------------------------------------- |
| `text`      | str   | The text to be processed.                                                         |
| `disable`   | `List[str]`  | Names of pipeline components to [disable](/usage/processing-pipelines#disabling). |
| **RETURNS** | `Doc` | A container for accessing the annotations.                                        |

## Language.pipe {#pipe tag="method"}

Process texts as a stream, and yield `Doc` objects in order. This is usually
more efficient than processing texts one-by-one.

> #### Example
>
> ```python
> texts = ["One document.", "...", "Lots of documents"]
> for doc in nlp.pipe(texts, batch_size=50):
>     assert doc.is_parsed
> ```

| Name                                         | Type              | Description                                                                                                                                                |
| -------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `texts`                                      | `Iterable[str]`   | A sequence of strings.                                                                                                                                     |
| `as_tuples`                                  | bool              | If set to `True`, inputs should be a sequence of `(text, context)` tuples. Output will then be a sequence of `(doc, context)` tuples. Defaults to `False`. |
| `batch_size`                                 | int               | The number of texts to buffer.                                                                                                                             |
| `disable`                                    | `List[str]`       | Names of pipeline components to [disable](/usage/processing-pipelines#disabling).                                                                          |
| `component_cfg` <Tag variant="new">2.1</Tag> | `Dict[str, Dict]` | Config parameters for specific pipeline components, keyed by component name.                                                                               |
| `n_process` <Tag variant="new">2.2.2</Tag>   | int               | Number of processors to use, only supported in Python 3. Defaults to `1`.                                                                                  |
| **YIELDS**                                   | `Doc`             | Documents in the order of the original text.                                                                                                               |

## Language.update {#update tag="method"}

Update the models in the pipeline.

> #### Example
>
> ```python
> for raw_text, entity_offsets in train_data:
>     doc = nlp.make_doc(raw_text)
>     example = Example.from_dict(doc, {"entities": entity_offsets})
>     nlp.update([example], sgd=optimizer)
> ```

| Name                                         | Type                | Description                                                                  |
| -------------------------------------------- | ------------------- | ---------------------------------------------------------------------------- |
| `examples`                                   | `Iterable[Example]` | A batch of `Example` objects to learn from.                                  |
| _keyword-only_                               |                     |                                                                              |
| `drop`                                       | float               | The dropout rate.                                                            |
| `sgd`                                        | `Optimizer`         | An [`Optimizer`](https://thinc.ai/docs/api-optimizers) object.               |
| `losses`                                     | `Dict[str, float]`  | Dictionary to update with the loss, keyed by pipeline component.             |
| `component_cfg` <Tag variant="new">2.1</Tag> | `Dict[str, Dict]`   | Config parameters for specific pipeline components, keyed by component name. |
| **RETURNS**                                  | `Dict[str, float]`  | The updated `losses` dictionary.                                             |

## Language.evaluate {#evaluate tag="method"}

Evaluate a model's pipeline components.

> #### Example
>
> ```python
> scorer = nlp.evaluate(examples, verbose=True)
> print(scorer.scores)
> ```

| Name                                         | Type                | Description                                                                           |
| -------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------- |
| `examples`                                   | `Iterable[Example]` | A batch of [`Example`](/api/example) objects to learn from.                           |
| `verbose`                                    | bool                | Print debugging information.                                                          |
| `batch_size`                                 | int                 | The batch size to use.                                                                |
| `scorer`                                     | `Scorer`            | Optional [`Scorer`](/api/scorer) to use. If not passed in, a new one will be created. |
| `component_cfg` <Tag variant="new">2.1</Tag> | `Dict[str, Dict]`   | Config parameters for specific pipeline components, keyed by component name.          |
| **RETURNS**                                  | Scorer              | The scorer containing the evaluation scores.                                          |

## Language.begin_training {#begin_training tag="method"}

Allocate models, pre-process training data and acquire an
[`Optimizer`](https://thinc.ai/docs/api-optimizers).

> #### Example
>
> ```python
> optimizer = nlp.begin_training(get_examples)
> ```

| Name                                         | Type                | Description                                                                                                        |
| -------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `get_examples`                               | `Iterable[Example]` | Optional gold-standard annotations in the form of [`Example`](/api/example) objects.                               |
| `sgd`                                        | `Optimizer`         | An optional [`Optimizer`](https://thinc.ai/docs/api-optimizers) object. If not set, a default one will be created. |
| `component_cfg` <Tag variant="new">2.1</Tag> | `Dict[str, Dict]`   | Config parameters for specific pipeline components, keyed by component name.                                       |
| `**cfg`                                      | -                   | Config parameters (sent to all components).                                                                        |
| **RETURNS**                                  | `Optimizer`         | An optimizer.                                                                                                      |

## Language.use_params {#use_params tag="contextmanager, method"}

Replace weights of models in the pipeline with those provided in the params
dictionary. Can be used as a context manager, in which case, models go back to
their original weights after the block.

> #### Example
>
> ```python
> with nlp.use_params(optimizer.averages):
>     nlp.to_disk("/tmp/checkpoint")
> ```

| Name     | Type | Description                                   |
| -------- | ---- | --------------------------------------------- |
| `params` | dict | A dictionary of parameters keyed by model ID. |
| `**cfg`  | -    | Config parameters.                            |

## Language.create_pipe {#create_pipe tag="method" new="2"}

Create a pipeline component from a factory.

> #### Example
>
> ```python
> parser = nlp.create_pipe("parser")
> nlp.add_pipe(parser)
> ```

| Name        | Type     | Description                                                                        |
| ----------- | -------- | ---------------------------------------------------------------------------------- |
| `name`      | str      | Factory name to look up in [`Language.factories`](/api/language#class-attributes). |
| `config`    | dict     | Configuration parameters to initialize component.                                  |
| **RETURNS** | callable | The pipeline component.                                                            |

## Language.add_pipe {#add_pipe tag="method" new="2"}

Add a component to the processing pipeline. Valid components are callables that
take a `Doc` object, modify it and return it. Only one of `before`, `after`,
`first` or `last` can be set. Default behavior is `last=True`.

> #### Example
>
> ```python
> def component(doc):
>     # modify Doc and return it return doc
>
> nlp.add_pipe(component, before="ner")
> nlp.add_pipe(component, name="custom_name", last=True)
> ```

| Name        | Type     | Description                                                                                                                                                                                                                                            |
| ----------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `component` | callable | The pipeline component.                                                                                                                                                                                                                                |
| `name`      | str      | Name of pipeline component. Overwrites existing `component.name` attribute if available. If no `name` is set and the component exposes no name attribute, `component.__name__` is used. An error is raised if the name already exists in the pipeline. |
| `before`    | str      | Component name to insert component directly before.                                                                                                                                                                                                    |
| `after`     | str      | Component name to insert component directly after:                                                                                                                                                                                                     |
| `first`     | bool     | Insert component first / not first in the pipeline.                                                                                                                                                                                                    |
| `last`      | bool     | Insert component last / not last in the pipeline.                                                                                                                                                                                                      |

## Language.has_pipe {#has_pipe tag="method" new="2"}

Check whether a component is present in the pipeline. Equivalent to
`name in nlp.pipe_names`.

> #### Example
>
> ```python
> nlp.add_pipe(lambda doc: doc, name="component")
> assert "component" in nlp.pipe_names
> assert nlp.has_pipe("component")
> ```

| Name        | Type | Description                                              |
| ----------- | ---- | -------------------------------------------------------- |
| `name`      | str  | Name of the pipeline component to check.                 |
| **RETURNS** | bool | Whether a component of that name exists in the pipeline. |

## Language.get_pipe {#get_pipe tag="method" new="2"}

Get a pipeline component for a given component name.

> #### Example
>
> ```python
> parser = nlp.get_pipe("parser")
> custom_component = nlp.get_pipe("custom_component")
> ```

| Name        | Type     | Description                            |
| ----------- | -------- | -------------------------------------- |
| `name`      | str      | Name of the pipeline component to get. |
| **RETURNS** | callable | The pipeline component.                |

## Language.replace_pipe {#replace_pipe tag="method" new="2"}

Replace a component in the pipeline.

> #### Example
>
> ```python
> nlp.replace_pipe("parser", my_custom_parser)
> ```

| Name        | Type     | Description                       |
| ----------- | -------- | --------------------------------- |
| `name`      | str      | Name of the component to replace. |
| `component` | callable | The pipeline component to insert. |

## Language.rename_pipe {#rename_pipe tag="method" new="2"}

Rename a component in the pipeline. Useful to create custom names for
pre-defined and pre-loaded components. To change the default name of a component
added to the pipeline, you can also use the `name` argument on
[`add_pipe`](/api/language#add_pipe).

> #### Example
>
> ```python
> nlp.rename_pipe("parser", "spacy_parser")
> ```

| Name       | Type | Description                      |
| ---------- | ---- | -------------------------------- |
| `old_name` | str  | Name of the component to rename. |
| `new_name` | str  | New name of the component.       |

## Language.remove_pipe {#remove_pipe tag="method" new="2"}

Remove a component from the pipeline. Returns the removed component name and
component function.

> #### Example
>
> ```python
> name, component = nlp.remove_pipe("parser")
> assert name == "parser"
> ```

| Name        | Type  | Description                                           |
| ----------- | ----- | ----------------------------------------------------- |
| `name`      | str   | Name of the component to remove.                      |
| **RETURNS** | tuple | A `(name, component)` tuple of the removed component. |

## Language.select_pipes {#select_pipes tag="contextmanager, method" new="3"}

Disable one or more pipeline components. If used as a context manager, the
pipeline will be restored to the initial state at the end of the block.
Otherwise, a `DisabledPipes` object is returned, that has a `.restore()` method
you can use to undo your changes. You can specify either `disable` (as a list or
string), or `enable`. In the latter case, all components not in the `enable`
list, will be disabled.

> #### Example
>
> ```python
> with nlp.select_pipes(disable=["tagger", "parser"]):
>    nlp.begin_training()
>
> with nlp.select_pipes(enable="ner"):
>     nlp.begin_training()
>
> disabled = nlp.select_pipes(disable=["tagger", "parser"])
> nlp.begin_training()
> disabled.restore()
> ```

<Infobox title="Changed in v3.0" variant="warning" id="disable_pipes">

As of spaCy v3.0, the `disable_pipes` method has been renamed to `select_pipes`:

```diff
- nlp.disable_pipes(["tagger", "parser"])
+ nlp.select_pipes(disable=["tagger", "parser"])
```

</Infobox>

| Name        | Type            | Description                                                                          |
| ----------- | --------------- | ------------------------------------------------------------------------------------ |
| `disable`   | str / list      | Name(s) of pipeline components to disable.                                           |
| `enable`    | str / list      | Names(s) of pipeline components that will not be disabled.                           |
| **RETURNS** | `DisabledPipes` | The disabled pipes that can be restored by calling the object's `.restore()` method. |

## Language.to_disk {#to_disk tag="method" new="2"}

Save the current state to a directory. If a model is loaded, this will **include
the model**.

> #### Example
>
> ```python
> nlp.to_disk("/path/to/models")
> ```

| Name      | Type         | Description                                                                                                           |
| --------- | ------------ | --------------------------------------------------------------------------------------------------------------------- |
| `path`    | str / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| `exclude` | list         | Names of pipeline components or [serialization fields](#serialization-fields) to exclude.                             |

## Language.from_disk {#from_disk tag="method" new="2"}

Loads state from a directory. Modifies the object in place and returns it. If
the saved `Language` object contains a model, the model will be loaded. Note
that this method is commonly used via the subclasses like `English` or `German`
to make language-specific functionality like the
[lexical attribute getters](/usage/adding-languages#lex-attrs) available to the
loaded object.

> #### Example
>
> ```python
> from spacy.language import Language
> nlp = Language().from_disk("/path/to/model")
>
> # using language-specific subclass
> from spacy.lang.en import English
> nlp = English().from_disk("/path/to/en_model")
> ```

| Name        | Type         | Description                                                                               |
| ----------- | ------------ | ----------------------------------------------------------------------------------------- |
| `path`      | str / `Path` | A path to a directory. Paths may be either strings or `Path`-like objects.                |
| `exclude`   | list         | Names of pipeline components or [serialization fields](#serialization-fields) to exclude. |
| **RETURNS** | `Language`   | The modified `Language` object.                                                           |

## Language.to_bytes {#to_bytes tag="method"}

Serialize the current state to a binary string.

> #### Example
>
> ```python
> nlp_bytes = nlp.to_bytes()
> ```

| Name        | Type  | Description                                                                               |
| ----------- | ----- | ----------------------------------------------------------------------------------------- |
| `exclude`   | list  | Names of pipeline components or [serialization fields](#serialization-fields) to exclude. |
| **RETURNS** | bytes | The serialized form of the `Language` object.                                             |

## Language.from_bytes {#from_bytes tag="method"}

Load state from a binary string. Note that this method is commonly used via the
subclasses like `English` or `German` to make language-specific functionality
like the [lexical attribute getters](/usage/adding-languages#lex-attrs)
available to the loaded object.

> #### Example
>
> ```python
> from spacy.lang.en import English
> nlp_bytes = nlp.to_bytes()
> nlp2 = English()
> nlp2.from_bytes(nlp_bytes)
> ```

| Name         | Type       | Description                                                                               |
| ------------ | ---------- | ----------------------------------------------------------------------------------------- |
| `bytes_data` | bytes      | The data to load from.                                                                    |
| `exclude`    | list       | Names of pipeline components or [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**  | `Language` | The `Language` object.                                                                    |

## Attributes {#attributes}

| Name                                       | Type        | Description                                                                                     |
| ------------------------------------------ | ----------- | ----------------------------------------------------------------------------------------------- |
| `vocab`                                    | `Vocab`     | A container for the lexical types.                                                              |
| `tokenizer`                                | `Tokenizer` | The tokenizer.                                                                                  |
| `make_doc`                                 | `callable`  | Callable that takes a string and returns a `Doc`.                                               |
| `pipeline`                                 | list        | List of `(name, component)` tuples describing the current processing pipeline, in order.        |
| `pipe_names` <Tag variant="new">2</Tag>    | list        | List of pipeline component names, in order.                                                     |
| `pipe_labels` <Tag variant="new">2.2</Tag> | dict        | List of labels set by the pipeline components, if available, keyed by component name.           |
| `meta`                                     | dict        | Custom meta data for the Language class. If a model is loaded, contains meta data of the model. |
| `path` <Tag variant="new">2</Tag>          | `Path`      | Path to the model data directory, if a model is loaded. Otherwise `None`.                       |

## Class attributes {#class-attributes}

| Name                                   | Type  | Description                                                                                                                         |
| -------------------------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `Defaults`                             | class | Settings, data and factory methods for creating the `nlp` object and processing pipeline.                                           |
| `lang`                                 | str   | Two-letter language ID, i.e. [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).                                     |
| `factories` <Tag variant="new">2</Tag> | dict  | Factories that create pre-defined pipeline components, e.g. the tagger, parser or entity recognizer, keyed by their component name. |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = nlp.to_bytes(exclude=["tokenizer", "vocab"])
> nlp.from_disk("./model-data", exclude=["ner"])
> ```

| Name        | Description                                        |
| ----------- | -------------------------------------------------- |
| `vocab`     | The shared [`Vocab`](/api/vocab).                  |
| `tokenizer` | Tokenization rules and exceptions.                 |
| `meta`      | The meta data, available as `Language.meta`.       |
| ...         | String names of pipeline components, e.g. `"ner"`. |
