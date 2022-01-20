---
title: Language
teaser: A text-processing pipeline
tag: class
source: spacy/language.py
---

Usually you'll load this once per process as `nlp` and pass the instance around
your application. The `Language` class is created when you call
[`spacy.load`](/api/top-level#spacy.load) and contains the shared vocabulary and
[language data](/usage/linguistic-features#language-data), optional binary
weights, e.g. provided by a [trained pipeline](/models), and the
[processing pipeline](/usage/processing-pipelines) containing components like
the tagger or parser that are called on a document in order. You can also add
your own processing pipeline components that take a `Doc` object, modify it and
return it.

## Language.\_\_init\_\_ {#init tag="method"}

Initialize a `Language` object. Note that the `meta` is only used for meta
information in [`Language.meta`](/api/language#meta) and not to configure the
`nlp` object or to override the config. To initialize from a config, use
[`Language.from_config`](/api/language#from_config) instead.

> #### Example
>
> ```python
> # Construction from subclass
> from spacy.lang.en import English
> nlp = English()
>
> # Construction from scratch
> from spacy.vocab import Vocab
> from spacy.language import Language
> nlp = Language(Vocab())
> ```

| Name               | Description                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `vocab`            | A `Vocab` object. If `True`, a vocab is created using the default language data settings. ~~Vocab~~                      |
| _keyword-only_     |                                                                                                                          |
| `max_length`       | Maximum number of characters allowed in a single text. Defaults to `10 ** 6`. ~~int~~                                    |
| `meta`             | [Meta data](/api/data-formats#meta) overrides. ~~Dict[str, Any]~~                                                        |
| `create_tokenizer` | Optional function that receives the `nlp` object and returns a tokenizer. ~~Callable[[Language], Callable[[str], Doc]]~~ |
| `batch_size`       | Default batch size for [`pipe`](#pipe) and [`evaluate`](#evaluate). Defaults to `1000`. ~~int~~                          |

## Language.from_config {#from_config tag="classmethod" new="3"}

Create a `Language` object from a loaded config. Will set up the tokenizer and
language data, add pipeline components based on the pipeline and add pipeline
components based on the definitions specified in the config. If no config is
provided, the default config of the given language is used. This is also how
spaCy loads a model under the hood based on its
[`config.cfg`](/api/data-formats#config).

> #### Example
>
> ```python
> from thinc.api import Config
> from spacy.language import Language
>
> config = Config().from_disk("./config.cfg")
> nlp = Language.from_config(config)
> ```

| Name           | Description                                                                                                                                                                                                                                      |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `config`       | The loaded config. ~~Union[Dict[str, Any], Config]~~                                                                                                                                                                                             |
| _keyword-only_ |                                                                                                                                                                                                                                                  |
| `vocab`        | A `Vocab` object. If `True`, a vocab is created using the default language data settings. ~~Vocab~~                                                                                                                                              |
| `disable`      | Names of pipeline components to [disable](/usage/processing-pipelines#disabling). Disabled pipes will be loaded but they won't be run unless you explicitly enable them by calling [`nlp.enable_pipe`](/api/language#enable_pipe). ~~List[str]~~ |
| `exclude`      | Names of pipeline components to [exclude](/usage/processing-pipelines#disabling). Excluded components won't be loaded. ~~List[str]~~                                                                                                             |
| `meta`         | [Meta data](/api/data-formats#meta) overrides. ~~Dict[str, Any]~~                                                                                                                                                                                |
| `auto_fill`    | Whether to automatically fill in missing values in the config, based on defaults and function argument annotations. Defaults to `True`. ~~bool~~                                                                                                 |
| `validate`     | Whether to validate the component config and arguments against the types expected by the factory. Defaults to `True`. ~~bool~~                                                                                                                   |
| **RETURNS**    | The initialized object. ~~Language~~                                                                                                                                                                                                             |

## Language.component {#component tag="classmethod" new="3"}

Register a custom pipeline component under a given name. This allows
initializing the component by name using
[`Language.add_pipe`](/api/language#add_pipe) and referring to it in
[config files](/usage/training#config). This classmethod and decorator is
intended for **simple stateless functions** that take a `Doc` and return it. For
more complex stateful components that allow settings and need access to the
shared `nlp` object, use the [`Language.factory`](/api/language#factory)
decorator. For more details and examples, see the
[usage documentation](/usage/processing-pipelines#custom-components).

> #### Example
>
> ```python
> from spacy.language import Language
>
> # Usage as a decorator
> @Language.component("my_component")
> def my_component(doc):
>    # Do something to the doc
>    return doc
>
> # Usage as a function
> Language.component("my_component2", func=my_component)
> ```

| Name           | Description                                                                                                                                                        |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`         | The name of the component factory. ~~str~~                                                                                                                         |
| _keyword-only_ |                                                                                                                                                                    |
| `assigns`      | `Doc` or `Token` attributes assigned by this component, e.g. `["token.ent_id"]`. Used for [pipe analysis](/usage/processing-pipelines#analysis). ~~Iterable[str]~~ |
| `requires`     | `Doc` or `Token` attributes required by this component, e.g. `["token.ent_id"]`. Used for [pipe analysis](/usage/processing-pipelines#analysis). ~~Iterable[str]~~ |
| `retokenizes`  | Whether the component changes tokenization. Used for [pipe analysis](/usage/processing-pipelines#analysis). ~~bool~~                                               |
| `func`         | Optional function if not used as a decorator. ~~Optional[Callable[[Doc], Doc]]~~                                                                                   |

## Language.factory {#factory tag="classmethod"}

Register a custom pipeline component factory under a given name. This allows
initializing the component by name using
[`Language.add_pipe`](/api/language#add_pipe) and referring to it in
[config files](/usage/training#config). The registered factory function needs to
take at least two **named arguments** which spaCy fills in automatically: `nlp`
for the current `nlp` object and `name` for the component instance name. This
can be useful to distinguish multiple instances of the same component and allows
trainable components to add custom losses using the component instance name. The
`default_config` defines the default values of the remaining factory arguments.
It's merged into the [`nlp.config`](/api/language#config). For more details and
examples, see the
[usage documentation](/usage/processing-pipelines#custom-components).

> #### Example
>
> ```python
> from spacy.language import Language
>
> # Usage as a decorator
> @Language.factory(
>    "my_component",
>    default_config={"some_setting": True},
> )
> def create_my_component(nlp, name, some_setting):
>      return MyComponent(some_setting)
>
> # Usage as function
> Language.factory(
>     "my_component",
>     default_config={"some_setting": True},
>     func=create_my_component
> )
> ```

| Name                    | Description                                                                                                                                                                                                                                                                                                                        |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                  | The name of the component factory. ~~str~~                                                                                                                                                                                                                                                                                         |
| _keyword-only_          |                                                                                                                                                                                                                                                                                                                                    |
| `default_config`        | The default config, describing the default values of the factory arguments. ~~Dict[str, Any]~~                                                                                                                                                                                                                                     |
| `assigns`               | `Doc` or `Token` attributes assigned by this component, e.g. `["token.ent_id"]`. Used for [pipe analysis](/usage/processing-pipelines#analysis). ~~Iterable[str]~~                                                                                                                                                                 |
| `requires`              | `Doc` or `Token` attributes required by this component, e.g. `["token.ent_id"]`. Used for [pipe analysis](/usage/processing-pipelines#analysis). ~~Iterable[str]~~                                                                                                                                                                 |
| `retokenizes`           | Whether the component changes tokenization. Used for [pipe analysis](/usage/processing-pipelines#analysis). ~~bool~~                                                                                                                                                                                                               |
| `default_score_weights` | The scores to report during training, and their default weight towards the final score used to select the best model. Weights should sum to `1.0` per component and will be combined and normalized for the whole pipeline. If a weight is set to `None`, the score will not be logged or weighted. ~~Dict[str, Optional[float]]~~ |
| `func`                  | Optional function if not used as a decorator. ~~Optional[Callable[[...], Callable[[Doc], Doc]]]~~                                                                                                                                                                                                                                  |

## Language.\_\_call\_\_ {#call tag="method"}

Apply the pipeline to some text. The text can span multiple sentences, and can
contain arbitrary whitespace. Alignment into the original string is preserved.

> #### Example
>
> ```python
> doc = nlp("An example sentence. Another sentence.")
> assert (doc[0].text, doc[0].head.tag_) == ("An", "NN")
> ```

| Name            | Description                                                                                                                                    |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `text`          | The text to be processed. ~~str~~                                                                                                              |
| _keyword-only_  |                                                                                                                                                |
| `disable`       | Names of pipeline components to [disable](/usage/processing-pipelines#disabling). ~~List[str]~~                                                |
| `component_cfg` | Optional dictionary of keyword arguments for components, keyed by component names. Defaults to `None`. ~~Optional[Dict[str, Dict[str, Any]]]~~ |
| **RETURNS**     | A container for accessing the annotations. ~~Doc~~                                                                                             |

## Language.pipe {#pipe tag="method"}

Process texts as a stream, and yield `Doc` objects in order. This is usually
more efficient than processing texts one-by-one.

> #### Example
>
> ```python
> texts = ["One document.", "...", "Lots of documents"]
> for doc in nlp.pipe(texts, batch_size=50):
>     assert doc.has_annotation("DEP")
> ```

| Name                                       | Description                                                                                                                                                         |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `texts`                                    | A sequence of strings. ~~Iterable[str]~~                                                                                                                            |
| _keyword-only_                             |                                                                                                                                                                     |
| `as_tuples`                                | If set to `True`, inputs should be a sequence of `(text, context)` tuples. Output will then be a sequence of `(doc, context)` tuples. Defaults to `False`. ~~bool~~ |
| `batch_size`                               | The number of texts to buffer. ~~Optional[int]~~                                                                                                                    |
| `disable`                                  | Names of pipeline components to [disable](/usage/processing-pipelines#disabling). ~~List[str]~~                                                                     |
| `component_cfg`                            | Optional dictionary of keyword arguments for components, keyed by component names. Defaults to `None`. ~~Optional[Dict[str, Dict[str, Any]]]~~                      |
| `n_process` <Tag variant="new">2.2.2</Tag> | Number of processors to use. Defaults to `1`. ~~int~~                                                                                                               |
| **YIELDS**                                 | Documents in the order of the original text. ~~Doc~~                                                                                                                |

## Language.set_error_handler {#set_error_handler tag="method" new="3"}

Define a callback that will be invoked when an error is thrown during processing
of one or more documents. Specifically, this function will call
[`set_error_handler`](/api/pipe#set_error_handler) on all the pipeline
components that define that function. The error handler will be invoked with the
original component's name, the component itself, the list of documents that was
being processed, and the original error.

> #### Example
>
> ```python
> def warn_error(proc_name, proc, docs, e):
>     print(f"An error occurred when applying component {proc_name}.")
>
> nlp.set_error_handler(warn_error)
> ```

| Name            | Description                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------- |
| `error_handler` | A function that performs custom error handling. ~~Callable[[str, Callable[[Doc], Doc], List[Doc], Exception]~~ |

## Language.initialize {#initialize tag="method" new="3"}

Initialize the pipeline for training and return an
[`Optimizer`](https://thinc.ai/docs/api-optimizers). Under the hood, it uses the
settings defined in the [`[initialize]`](/api/data-formats#config-initialize)
config block to set up the vocabulary, load in vectors and tok2vec weights and
pass optional arguments to the `initialize` methods implemented by pipeline
components or the tokenizer. This method is typically called automatically when
you run [`spacy train`](/api/cli#train). See the usage guide on the
[config lifecycle](/usage/training#config-lifecycle) and
[initialization](/usage/training#initialization) for details.

`get_examples` should be a function that returns an iterable of
[`Example`](/api/example) objects. The data examples can either be the full
training data or a representative sample. They are used to **initialize the
models** of trainable pipeline components and are passed each component's
[`initialize`](/api/pipe#initialize) method, if available. Initialization
includes validating the network,
[inferring missing shapes](/usage/layers-architectures#thinc-shape-inference)
and setting up the label scheme based on the data.

If no `get_examples` function is provided when calling `nlp.initialize`, the
pipeline components will be initialized with generic data. In this case, it is
crucial that the output dimension of each component has already been defined
either in the [config](/usage/training#config), or by calling
[`pipe.add_label`](/api/pipe#add_label) for each possible output label (e.g. for
the tagger or textcat).

<Infobox variant="warning" title="Changed in v3.0" id="begin_training">

This method was previously called `begin_training`. It now also takes a
**function** that is called with no arguments and returns a sequence of
[`Example`](/api/example) objects instead of tuples of `Doc` and `GoldParse`
objects.

</Infobox>

> #### Example
>
> ```python
> get_examples = lambda: examples
> optimizer = nlp.initialize(get_examples)
> ```

| Name           | Description                                                                                                                                              |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. ~~Optional[Callable[[], Iterable[Example]]]~~ |
| _keyword-only_ |                                                                                                                                                          |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~                                            |
| **RETURNS**    | The optimizer. ~~Optimizer~~                                                                                                                             |

## Language.resume_training {#resume_training tag="method,experimental" new="3"}

Continue training a trained pipeline. Create and return an optimizer, and
initialize "rehearsal" for any pipeline component that has a `rehearse` method.
Rehearsal is used to prevent models from "forgetting" their initialized
"knowledge". To perform rehearsal, collect samples of text you want the models
to retain performance on, and call [`nlp.rehearse`](/api/language#rehearse) with
a batch of [Example](/api/example) objects.

> #### Example
>
> ```python
> optimizer = nlp.resume_training()
> nlp.rehearse(examples, sgd=optimizer)
> ```

| Name           | Description                                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                                               |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~ |
| **RETURNS**    | The optimizer. ~~Optimizer~~                                                                                  |

## Language.update {#update tag="method"}

Update the models in the pipeline.

<Infobox variant="warning" title="Changed in v3.0">

The `Language.update` method now takes a batch of [`Example`](/api/example)
objects instead of the raw texts and annotations or `Doc` and `GoldParse`
objects. An [`Example`](/api/example) streamlines how data is passed around. It
stores two `Doc` objects: one for holding the gold-standard reference data, and
one for holding the predictions of the pipeline.

For most use cases, you shouldn't have to write your own training scripts
anymore. Instead, you can use [`spacy train`](/api/cli#train) with a config file
and custom registered functions if needed. See the
[training documentation](/usage/training) for details.

</Infobox>

> #### Example
>
> ```python
> for raw_text, entity_offsets in train_data:
>     doc = nlp.make_doc(raw_text)
>     example = Example.from_dict(doc, {"entities": entity_offsets})
>     nlp.update([example], sgd=optimizer)
> ```

| Name            | Description                                                                                                                                    |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`      | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                                              |
| _keyword-only_  |                                                                                                                                                |
| `drop`          | The dropout rate. ~~float~~                                                                                                                    |
| `sgd`           | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~                                  |
| `losses`        | Dictionary to update with the loss, keyed by pipeline component. ~~Optional[Dict[str, float]]~~                                                |
| `component_cfg` | Optional dictionary of keyword arguments for components, keyed by component names. Defaults to `None`. ~~Optional[Dict[str, Dict[str, Any]]]~~ |
| **RETURNS**     | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                                          |

## Language.rehearse {#rehearse tag="method,experimental" new="3"}

Perform a "rehearsal" update from a batch of data. Rehearsal updates teach the
current model to make predictions similar to an initial model, to try to address
the "catastrophic forgetting" problem. This feature is experimental.

> #### Example
>
> ```python
> optimizer = nlp.resume_training()
> losses = nlp.rehearse(examples, sgd=optimizer)
> ```

| Name           | Description                                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------------------- |
| `examples`     | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                             |
| _keyword-only_ |                                                                                                               |
| `drop`         | The dropout rate. ~~float~~                                                                                   |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~ |
| `losses`       | Dictionary to update with the loss, keyed by pipeline component. ~~Optional[Dict[str, float]]~~               |
| **RETURNS**    | The updated `losses` dictionary. ~~Dict[str, float]~~                                                         |

## Language.evaluate {#evaluate tag="method"}

Evaluate a pipeline's components.

<Infobox variant="warning" title="Changed in v3.0">

The `Language.evaluate` method now takes a batch of [`Example`](/api/example)
objects instead of tuples of `Doc` and `GoldParse` objects.

</Infobox>

> #### Example
>
> ```python
> scores = nlp.evaluate(examples)
> print(scores)
> ```

| Name            | Description                                                                                                                                    |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`      | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                                              |
| _keyword-only_  |                                                                                                                                                |
| `batch_size`    | The batch size to use. ~~Optional[int]~~                                                                                                       |
| `scorer`        | Optional [`Scorer`](/api/scorer) to use. If not passed in, a new one will be created. ~~Optional[Scorer]~~                                     |
| `component_cfg` | Optional dictionary of keyword arguments for components, keyed by component names. Defaults to `None`. ~~Optional[Dict[str, Dict[str, Any]]]~~ |
| `scorer_cfg`    | Optional dictionary of keyword arguments for the `Scorer`. Defaults to `None`. ~~Optional[Dict[str, Any]]~~                                    |
| **RETURNS**     | A dictionary of evaluation scores. ~~Dict[str, Union[float, Dict[str, float]]]~~                                                               |

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

| Name     | Description                                            |
| -------- | ------------------------------------------------------ |
| `params` | A dictionary of parameters keyed by model ID. ~~dict~~ |

## Language.add_pipe {#add_pipe tag="method" new="2"}

Add a component to the processing pipeline. Expects a name that maps to a
component factory registered using
[`@Language.component`](/api/language#component) or
[`@Language.factory`](/api/language#factory). Components should be callables
that take a `Doc` object, modify it and return it. Only one of `before`,
`after`, `first` or `last` can be set. Default behavior is `last=True`.

<Infobox title="Changed in v3.0" variant="warning">

As of v3.0, the [`Language.add_pipe`](/api/language#add_pipe) method doesn't
take callables anymore and instead expects the **name of a component factory**
registered using [`@Language.component`](/api/language#component) or
[`@Language.factory`](/api/language#factory). It now takes care of creating the
component, adds it to the pipeline and returns it.

</Infobox>

> #### Example
>
> ```python
> @Language.component("component")
> def component_func(doc):
>     # modify Doc and return it
>     return doc
>
> nlp.add_pipe("component", before="ner")
> component = nlp.add_pipe("component", name="custom_name", last=True)
>
> # Add component from source pipeline
> source_nlp = spacy.load("en_core_web_sm")
> nlp.add_pipe("ner", source=source_nlp)
> ```

| Name                                  | Description                                                                                                                                                                                                                                                                              |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `factory_name`                        | Name of the registered component factory. ~~str~~                                                                                                                                                                                                                                        |
| `name`                                | Optional unique name of pipeline component instance. If not set, the factory name is used. An error is raised if the name already exists in the pipeline. ~~Optional[str]~~                                                                                                              |
| _keyword-only_                        |                                                                                                                                                                                                                                                                                          |
| `before`                              | Component name or index to insert component directly before. ~~Optional[Union[str, int]]~~                                                                                                                                                                                               |
| `after`                               | Component name or index to insert component directly after. ~~Optional[Union[str, int]]~~                                                                                                                                                                                                |
| `first`                               | Insert component first / not first in the pipeline. ~~Optional[bool]~~                                                                                                                                                                                                                   |
| `last`                                | Insert component last / not last in the pipeline. ~~Optional[bool]~~                                                                                                                                                                                                                     |
| `config` <Tag variant="new">3</Tag>   | Optional config parameters to use for this component. Will be merged with the `default_config` specified by the component factory. ~~Dict[str, Any]~~                                                                                                                                    |
| `source` <Tag variant="new">3</Tag>   | Optional source pipeline to copy component from. If a source is provided, the `factory_name` is interpreted as the name of the component in the source pipeline. Make sure that the vocab, vectors and settings of the source pipeline match the target pipeline. ~~Optional[Language]~~ |
| `validate` <Tag variant="new">3</Tag> | Whether to validate the component config and arguments against the types expected by the factory. Defaults to `True`. ~~bool~~                                                                                                                                                           |
| **RETURNS**                           | The pipeline component. ~~Callable[[Doc], Doc]~~                                                                                                                                                                                                                                         |

## Language.create_pipe {#create_pipe tag="method" new="2"}

Create a pipeline component from a factory.

<Infobox title="Changed in v3.0" variant="warning">

As of v3.0, the [`Language.add_pipe`](/api/language#add_pipe) method also takes
the string name of the factory, creates the component, adds it to the pipeline
and returns it. The `Language.create_pipe` method is now mostly used internally.
To create a component and add it to the pipeline, you should always use
`Language.add_pipe`.

</Infobox>

> #### Example
>
> ```python
> parser = nlp.create_pipe("parser")
> ```

| Name                                  | Description                                                                                                                                                                 |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `factory_name`                        | Name of the registered component factory. ~~str~~                                                                                                                           |
| `name`                                | Optional unique name of pipeline component instance. If not set, the factory name is used. An error is raised if the name already exists in the pipeline. ~~Optional[str]~~ |
| _keyword-only_                        |                                                                                                                                                                             |
| `config` <Tag variant="new">3</Tag>   | Optional config parameters to use for this component. Will be merged with the `default_config` specified by the component factory. ~~Dict[str, Any]~~                       |
| `validate` <Tag variant="new">3</Tag> | Whether to validate the component config and arguments against the types expected by the factory. Defaults to `True`. ~~bool~~                                              |
| **RETURNS**                           | The pipeline component. ~~Callable[[Doc], Doc]~~                                                                                                                            |

## Language.has_factory {#has_factory tag="classmethod" new="3"}

Check whether a factory name is registered on the `Language` class or subclass.
Will check for
[language-specific factories](/usage/processing-pipelines#factories-language)
registered on the subclass, as well as general-purpose factories registered on
the `Language` base class, available to all subclasses.

> #### Example
>
> ```python
> from spacy.language import Language
> from spacy.lang.en import English
>
> @English.component("component")
> def component(doc):
>     return doc
>
> assert English.has_factory("component")
> assert not Language.has_factory("component")
> ```

| Name        | Description                                                         |
| ----------- | ------------------------------------------------------------------- |
| `name`      | Name of the pipeline factory to check. ~~str~~                      |
| **RETURNS** | Whether a factory of that name is registered on the class. ~~bool~~ |

## Language.has_pipe {#has_pipe tag="method" new="2"}

Check whether a component is present in the pipeline. Equivalent to
`name in nlp.pipe_names`.

> #### Example
>
> ```python
> @Language.component("component")
> def component(doc):
>     return doc
>
> nlp.add_pipe("component", name="my_component")
> assert "my_component" in nlp.pipe_names
> assert nlp.has_pipe("my_component")
> ```

| Name        | Description                                                       |
| ----------- | ----------------------------------------------------------------- |
| `name`      | Name of the pipeline component to check. ~~str~~                  |
| **RETURNS** | Whether a component of that name exists in the pipeline. ~~bool~~ |

## Language.get_pipe {#get_pipe tag="method" new="2"}

Get a pipeline component for a given component name.

> #### Example
>
> ```python
> parser = nlp.get_pipe("parser")
> custom_component = nlp.get_pipe("custom_component")
> ```

| Name        | Description                                      |
| ----------- | ------------------------------------------------ |
| `name`      | Name of the pipeline component to get. ~~str~~   |
| **RETURNS** | The pipeline component. ~~Callable[[Doc], Doc]~~ |

## Language.replace_pipe {#replace_pipe tag="method" new="2"}

Replace a component in the pipeline and return the new component.

<Infobox title="Changed in v3.0" variant="warning">

As of v3.0, the `Language.replace_pipe` method doesn't take callables anymore
and instead expects the **name of a component factory** registered using
[`@Language.component`](/api/language#component) or
[`@Language.factory`](/api/language#factory).

</Infobox>

> #### Example
>
> ```python
> new_parser = nlp.replace_pipe("parser", "my_custom_parser")
> ```

| Name                                  | Description                                                                                                                                                        |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`                                | Name of the component to replace. ~~str~~                                                                                                                          |
| `component`                           | The factory name of the component to insert. ~~str~~                                                                                                               |
| _keyword-only_                        |                                                                                                                                                                    |
| `config` <Tag variant="new">3</Tag>   | Optional config parameters to use for the new component. Will be merged with the `default_config` specified by the component factory. ~~Optional[Dict[str, Any]]~~ |
| `validate` <Tag variant="new">3</Tag> | Whether to validate the component config and arguments against the types expected by the factory. Defaults to `True`. ~~bool~~                                     |
| **RETURNS**                           | The new pipeline component. ~~Callable[[Doc], Doc]~~                                                                                                               |

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

| Name       | Description                              |
| ---------- | ---------------------------------------- |
| `old_name` | Name of the component to rename. ~~str~~ |
| `new_name` | New name of the component. ~~str~~       |

## Language.remove_pipe {#remove_pipe tag="method" new="2"}

Remove a component from the pipeline. Returns the removed component name and
component function.

> #### Example
>
> ```python
> name, component = nlp.remove_pipe("parser")
> assert name == "parser"
> ```

| Name        | Description                                                                                |
| ----------- | ------------------------------------------------------------------------------------------ |
| `name`      | Name of the component to remove. ~~str~~                                                   |
| **RETURNS** | A `(name, component)` tuple of the removed component. ~~Tuple[str, Callable[[Doc], Doc]]~~ |

## Language.disable_pipe {#disable_pipe tag="method" new="3"}

Temporarily disable a pipeline component so it's not run as part of the
pipeline. Disabled components are listed in
[`nlp.disabled`](/api/language#attributes) and included in
[`nlp.components`](/api/language#attributes), but not in
[`nlp.pipeline`](/api/language#pipeline), so they're not run when you process a
`Doc` with the `nlp` object. If the component is already disabled, this method
does nothing.

> #### Example
>
> ```python
> nlp.add_pipe("ner")
> nlp.add_pipe("textcat")
> assert nlp.pipe_names == ["ner", "textcat"]
> nlp.disable_pipe("ner")
> assert nlp.pipe_names == ["textcat"]
> assert nlp.component_names == ["ner", "textcat"]
> assert nlp.disabled == ["ner"]
> ```

| Name   | Description                               |
| ------ | ----------------------------------------- |
| `name` | Name of the component to disable. ~~str~~ |

## Language.enable_pipe {#enable_pipe tag="method" new="3"}

Enable a previously disabled component (e.g. via
[`Language.disable_pipes`](/api/language#disable_pipes)) so it's run as part of
the pipeline, [`nlp.pipeline`](/api/language#pipeline). If the component is
already enabled, this method does nothing.

> #### Example
>
> ```python
> nlp.disable_pipe("ner")
> assert "ner" in nlp.disabled
> assert not "ner" in nlp.pipe_names
> nlp.enable_pipe("ner")
> assert not "ner" in nlp.disabled
> assert "ner" in nlp.pipe_names
> ```

| Name   | Description                              |
| ------ | ---------------------------------------- |
| `name` | Name of the component to enable. ~~str~~ |

## Language.select_pipes {#select_pipes tag="contextmanager, method" new="3"}

Disable one or more pipeline components. If used as a context manager, the
pipeline will be restored to the initial state at the end of the block.
Otherwise, a `DisabledPipes` object is returned, that has a `.restore()` method
you can use to undo your changes. You can specify either `disable` (as a list or
string), or `enable`. In the latter case, all components not in the `enable`
list will be disabled. Under the hood, this method calls into
[`disable_pipe`](/api/language#disable_pipe) and
[`enable_pipe`](/api/language#enable_pipe).

> #### Example
>
> ```python
> with nlp.select_pipes(disable=["tagger", "parser"]):
>    nlp.initialize()
>
> with nlp.select_pipes(enable="ner"):
>     nlp.initialize()
>
> disabled = nlp.select_pipes(disable=["tagger", "parser"])
> nlp.initialize()
> disabled.restore()
> ```

<Infobox title="Changed in v3.0" variant="warning" id="disable_pipes">

As of spaCy v3.0, the `disable_pipes` method has been renamed to `select_pipes`:

```diff
- nlp.disable_pipes(["tagger", "parser"])
+ nlp.select_pipes(disable=["tagger", "parser"])
```

</Infobox>

| Name           | Description                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------ |
| _keyword-only_ |                                                                                                        |
| `disable`      | Name(s) of pipeline components to disable. ~~Optional[Union[str, Iterable[str]]]~~                     |
| `enable`       | Name(s) of pipeline components that will not be disabled. ~~Optional[Union[str, Iterable[str]]]~~      |
| **RETURNS**    | The disabled pipes that can be restored by calling the object's `.restore()` method. ~~DisabledPipes~~ |

## Language.get_factory_meta {#get_factory_meta tag="classmethod" new="3"}

Get the factory meta information for a given pipeline component name. Expects
the name of the component **factory**. The factory meta is an instance of the
[`FactoryMeta`](/api/language#factorymeta) dataclass and contains the
information about the component and its default provided by the
[`@Language.component`](/api/language#component) or
[`@Language.factory`](/api/language#factory) decorator.

> #### Example
>
> ```python
> factory_meta = Language.get_factory_meta("ner")
> assert factory_meta.factory == "ner"
> print(factory_meta.default_config)
> ```

| Name        | Description                       |
| ----------- | --------------------------------- |
| `name`      | The factory name. ~~str~~         |
| **RETURNS** | The factory meta. ~~FactoryMeta~~ |

## Language.get_pipe_meta {#get_pipe_meta tag="method" new="3"}

Get the factory meta information for a given pipeline component name. Expects
the name of the component **instance** in the pipeline. The factory meta is an
instance of the [`FactoryMeta`](/api/language#factorymeta) dataclass and
contains the information about the component and its default provided by the
[`@Language.component`](/api/language#component) or
[`@Language.factory`](/api/language#factory) decorator.

> #### Example
>
> ```python
> nlp.add_pipe("ner", name="entity_recognizer")
> factory_meta = nlp.get_pipe_meta("entity_recognizer")
> assert factory_meta.factory == "ner"
> print(factory_meta.default_config)
> ```

| Name        | Description                          |
| ----------- | ------------------------------------ |
| `name`      | The pipeline component name. ~~str~~ |
| **RETURNS** | The factory meta. ~~FactoryMeta~~    |

## Language.analyze_pipes {#analyze_pipes tag="method" new="3"}

Analyze the current pipeline components and show a summary of the attributes
they assign and require, and the scores they set. The data is based on the
information provided in the [`@Language.component`](/api/language#component) and
[`@Language.factory`](/api/language#factory) decorator. If requirements aren't
met, e.g. if a component specifies a required property that is not set by a
previous component, a warning is shown.

<Infobox variant="warning" title="Important note">

The pipeline analysis is static and does **not actually run the components**.
This means that it relies on the information provided by the components
themselves. If a custom component declares that it assigns an attribute but it
doesn't, the pipeline analysis won't catch that.

</Infobox>

> #### Example
>
> ```python
> nlp = spacy.blank("en")
> nlp.add_pipe("tagger")
> nlp.add_pipe("entity_linker")
> analysis = nlp.analyze_pipes()
> ```

<Accordion title="Example output" spaced>

```json
### Structured
{
  "summary": {
    "tagger": {
      "assigns": ["token.tag"],
      "requires": [],
      "scores": ["tag_acc", "pos_acc", "lemma_acc"],
      "retokenizes": false
    },
    "entity_linker": {
      "assigns": ["token.ent_kb_id"],
      "requires": ["doc.ents", "doc.sents", "token.ent_iob", "token.ent_type"],
      "scores": [],
      "retokenizes": false
    }
  },
  "problems": {
    "tagger": [],
    "entity_linker": ["doc.ents", "doc.sents", "token.ent_iob", "token.ent_type"]
  },
  "attrs": {
    "token.ent_iob": { "assigns": [], "requires": ["entity_linker"] },
    "doc.ents": { "assigns": [], "requires": ["entity_linker"] },
    "token.ent_kb_id": { "assigns": ["entity_linker"], "requires": [] },
    "doc.sents": { "assigns": [], "requires": ["entity_linker"] },
    "token.tag": { "assigns": ["tagger"], "requires": [] },
    "token.ent_type": { "assigns": [], "requires": ["entity_linker"] }
  }
}
```

```
### Pretty
============================= Pipeline Overview =============================

#   Component       Assigns           Requires         Scores        Retokenizes
-   -------------   ---------------   --------------   -----------   -----------
0   tagger          token.tag                          tag_acc       False

1   entity_linker   token.ent_kb_id   doc.ents         nel_micro_f   False
                                      doc.sents        nel_micro_r
                                      token.ent_iob    nel_micro_p
                                      token.ent_type


================================ Problems (4) ================================
⚠ 'entity_linker' requirements not met: doc.ents, doc.sents,
token.ent_iob, token.ent_type
```

</Accordion>

| Name           | Description                                                                                                                                                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                                                                                                                                                                             |
| `keys`         | The values to display in the table. Corresponds to attributes of the [`FactoryMeta`](/api/language#factorymeta). Defaults to `["assigns", "requires", "scores", "retokenizes"]`. ~~List[str]~~                                              |
| `pretty`       | Pretty-print the results as a table. Defaults to `False`. ~~bool~~                                                                                                                                                                          |
| **RETURNS**    | Dictionary containing the pipe analysis, keyed by `"summary"` (component meta by pipe), `"problems"` (attribute names by pipe) and `"attrs"` (pipes that assign and require an attribute, keyed by attribute). ~~Optional[Dict[str, Any]]~~ |

## Language.replace_listeners {#replace_listeners tag="method" new="3"}

Find [listener layers](/usage/embeddings-transformers#embedding-layers)
(connecting to a shared token-to-vector embedding component) of a given pipeline
component model and replace them with a standalone copy of the token-to-vector
layer. The listener layer allows other components to connect to a shared
token-to-vector embedding component like [`Tok2Vec`](/api/tok2vec) or
[`Transformer`](/api/transformer). Replacing listeners can be useful when
training a pipeline with components sourced from an existing pipeline: if
multiple components (e.g. tagger, parser, NER) listen to the same
token-to-vector component, but some of them are frozen and not updated, their
performance may degrade significally as the token-to-vector component is updated
with new data. To prevent this, listeners can be replaced with a standalone
token-to-vector layer that is owned by the component and doesn't change if the
component isn't updated.

This method is typically not called directly and only executed under the hood
when loading a config with
[sourced components](/usage/training#config-components) that define
`replace_listeners`.

> ```python
> ### Example
> nlp = spacy.load("en_core_web_sm")
> nlp.replace_listeners("tok2vec", "tagger", ["model.tok2vec"])
> ```
>
> ```ini
> ### config.cfg (excerpt)
> [training]
> frozen_components = ["tagger"]
>
> [components]
>
> [components.tagger]
> source = "en_core_web_sm"
> replace_listeners = ["model.tok2vec"]
> ```

| Name           | Description                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tok2vec_name` | Name of the token-to-vector component, typically `"tok2vec"` or `"transformer"`.~~str~~                                                                                                                                                                                                                                                                                                                                                |
| `pipe_name`    | Name of pipeline component to replace listeners for. ~~str~~                                                                                                                                                                                                                                                                                                                                                                           |
| `listeners`    | The paths to the listeners, relative to the component config, e.g. `["model.tok2vec"]`. Typically, implementations will only connect to one tok2vec component, `model.tok2vec`, but in theory, custom models can use multiple listeners. The value here can either be an empty list to not replace any listeners, or a _complete_ list of the paths to all listener layers used by the model that should be replaced.~~Iterable[str]~~ |

## Language.meta {#meta tag="property"}

Meta data for the `Language` class, including name, version, data sources,
license, author information and more. If a trained pipeline is loaded, this
contains meta data of the pipeline. The `Language.meta` is also what's
serialized as the `meta.json` when you save an `nlp` object to disk. See the
[meta data format](/api/data-formats#meta) for more details.

<Infobox variant="warning" title="Changed in v3.0">

As of v3.0, the meta only contains **meta information** about the pipeline and
isn't used to construct the language class and pipeline components. This
information is expressed in the [`config.cfg`](/api/data-formats#config).

</Infobox>

> #### Example
>
> ```python
> print(nlp.meta)
> ```

| Name        | Description                       |
| ----------- | --------------------------------- |
| **RETURNS** | The meta data. ~~Dict[str, Any]~~ |

## Language.config {#config tag="property" new="3"}

Export a trainable [`config.cfg`](/api/data-formats#config) for the current
`nlp` object. Includes the current pipeline, all configs used to create the
currently active pipeline components, as well as the default training config
that can be used with [`spacy train`](/api/cli#train). `Language.config` returns
a [Thinc `Config` object](https://thinc.ai/docs/api-config#config), which is a
subclass of the built-in `dict`. It supports the additional methods `to_disk`
(serialize the config to a file) and `to_str` (output the config as a string).

> #### Example
>
> ```python
> nlp.config.to_disk("./config.cfg")
> print(nlp.config.to_str())
> ```

| Name        | Description            |
| ----------- | ---------------------- |
| **RETURNS** | The config. ~~Config~~ |

## Language.to_disk {#to_disk tag="method" new="2"}

Save the current state to a directory. Under the hood, this method delegates to
the `to_disk` methods of the individual pipeline components, if available. This
means that if a trained pipeline is loaded, all components and their weights
will be saved to disk.

> #### Example
>
> ```python
> nlp.to_disk("/path/to/pipeline")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | Names of pipeline components or [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                |

## Language.from_disk {#from_disk tag="method" new="2"}

Loads state from a directory, including all data that was saved with the
`Language` object. Modifies the object in place and returns it.

<Infobox variant="warning" title="Important note">

Keep in mind that this method **only loads the serialized state** and doesn't
set up the `nlp` object. This means that it requires the correct language class
to be initialized and all pipeline components to be added to the pipeline. If
you want to load a serialized pipeline from a directory, you should use
[`spacy.load`](/api/top-level#spacy.load), which will set everything up for you.

</Infobox>

> #### Example
>
> ```python
> from spacy.language import Language
> nlp = Language().from_disk("/path/to/pipeline")
>
> # Using language-specific subclass
> from spacy.lang.en import English
> nlp = English().from_disk("/path/to/pipeline")
> ```

| Name           | Description                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~             |
| _keyword-only_ |                                                                                                             |
| `exclude`      | Names of pipeline components or [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The modified `Language` object. ~~Language~~                                                                |

## Language.to_bytes {#to_bytes tag="method"}

Serialize the current state to a binary string.

> #### Example
>
> ```python
> nlp_bytes = nlp.to_bytes()
> ```

| Name           | Description                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------ |
| _keyword-only_ |                                                                                                        |
| `exclude`      | Names of pipeline components or [serialization fields](#serialization-fields) to exclude. ~~iterable~~ |
| **RETURNS**    | The serialized form of the `Language` object. ~~bytes~~                                                |

## Language.from_bytes {#from_bytes tag="method"}

Load state from a binary string. Note that this method is commonly used via the
subclasses like `English` or `German` to make language-specific functionality
like the [lexical attribute getters](/usage/linguistic-features#language-data)
available to the loaded object.

Note that if you want to serialize and reload a whole pipeline, using this alone
won't work, you also need to handle the config. See
["Serializing the pipeline"](https://spacy.io/usage/saving-loading#pipeline) for
details.

> #### Example
>
> ```python
> from spacy.lang.en import English
> nlp_bytes = nlp.to_bytes()
> nlp2 = English()
> nlp2.from_bytes(nlp_bytes)
> ```

| Name           | Description                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                                            |
| _keyword-only_ |                                                                                                             |
| `exclude`      | Names of pipeline components or [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `Language` object. ~~Language~~                                                                         |

## Attributes {#attributes}

| Name                                          | Description                                                                                                                                    |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`                                       | A container for the lexical types. ~~Vocab~~                                                                                                   |
| `tokenizer`                                   | The tokenizer. ~~Tokenizer~~                                                                                                                   |
| `make_doc`                                    | Callable that takes a string and returns a `Doc`. ~~Callable[[str], Doc]~~                                                                     |
| `pipeline`                                    | List of `(name, component)` tuples describing the current processing pipeline, in order. ~~List[Tuple[str, Callable[[Doc], Doc]]]~~            |
| `pipe_names` <Tag variant="new">2</Tag>       | List of pipeline component names, in order. ~~List[str]~~                                                                                      |
| `pipe_labels` <Tag variant="new">2.2</Tag>    | List of labels set by the pipeline components, if available, keyed by component name. ~~Dict[str, List[str]]~~                                 |
| `pipe_factories` <Tag variant="new">2.2</Tag> | Dictionary of pipeline component names, mapped to their factory names. ~~Dict[str, str]~~                                                      |
| `factories`                                   | All available factory functions, keyed by name. ~~Dict[str, Callable[[...], Callable[[Doc], Doc]]]~~                                           |
| `factory_names` <Tag variant="new">3</Tag>    | List of all available factory names. ~~List[str]~~                                                                                             |
| `components` <Tag variant="new">3</Tag>       | List of all available `(name, component)` tuples, including components that are currently disabled. ~~List[Tuple[str, Callable[[Doc], Doc]]]~~ |
| `component_names` <Tag variant="new">3</Tag>  | List of all available component names, including components that are currently disabled. ~~List[str]~~                                         |
| `disabled` <Tag variant="new">3</Tag>         | Names of components that are currently disabled and don't run as part of the pipeline. ~~List[str]~~                                           |
| `path` <Tag variant="new">2</Tag>             | Path to the pipeline data directory, if a pipeline is loaded from a path or package. Otherwise `None`. ~~Optional[Path]~~                      |

## Class attributes {#class-attributes}

| Name             | Description                                                                                                                                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Defaults`       | Settings, data and factory methods for creating the `nlp` object and processing pipeline. ~~Defaults~~                                                                            |
| `lang`           | [IETF language tag](https://www.w3.org/International/articles/language-tags/), such as 'en' for English. ~~str~~                                                                  |
| `default_config` | Base [config](/usage/training#config) to use for [Language.config](/api/language#config). Defaults to [`default_config.cfg`](%%GITHUB_SPACY/spacy/default_config.cfg). ~~Config~~ |

## Defaults {#defaults}

The following attributes can be set on the `Language.Defaults` class to
customize the default language data:

> #### Example
>
> ```python
> from spacy.language import language
> from spacy.lang.tokenizer_exceptions import URL_MATCH
> from thinc.api import Config
>
> DEFAULT_CONFIFG = """
> [nlp.tokenizer]
> @tokenizers = "MyCustomTokenizer.v1"
> """
>
> class Defaults(Language.Defaults):
>    stop_words = set()
>    tokenizer_exceptions = {}
>    prefixes = tuple()
>    suffixes = tuple()
>    infixes = tuple()
>    token_match = None
>    url_match = URL_MATCH
>    lex_attr_getters = {}
>    syntax_iterators = {}
>    writing_system = {"direction": "ltr", "has_case": True, "has_letters": True}
>    config = Config().from_str(DEFAULT_CONFIG)
> ```

| Name                              | Description                                                                                                                                                                                                                                                                                                      |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `stop_words`                      | List of stop words, used for `Token.is_stop`.<br />**Example:** [`stop_words.py`](%%GITHUB_SPACY/spacy/lang/en/stop_words.py) ~~Set[str]~~                                                                                                                                                                       |
| `tokenizer_exceptions`            | Tokenizer exception rules, string mapped to list of token attributes.<br />**Example:** [`de/tokenizer_exceptions.py`](%%GITHUB_SPACY/spacy/lang/de/tokenizer_exceptions.py) ~~Dict[str, List[dict]]~~                                                                                                           |
| `prefixes`, `suffixes`, `infixes` | Prefix, suffix and infix rules for the default tokenizer.<br />**Example:** [`puncutation.py`](%%GITHUB_SPACY/spacy/lang/punctuation.py) ~~Optional[Sequence[Union[str, Pattern]]]~~                                                                                                                             |
| `token_match`                     | Optional regex for matching strings that should never be split, overriding the infix rules.<br />**Example:** [`fr/tokenizer_exceptions.py`](%%GITHUB_SPACY/spacy/lang/fr/tokenizer_exceptions.py) ~~Optional[Callable]~~                                                                                        |
| `url_match`                       | Regular expression for matching URLs. Prefixes and suffixes are removed before applying the match.<br />**Example:** [`tokenizer_exceptions.py`](%%GITHUB_SPACY/spacy/lang/tokenizer_exceptions.py) ~~Optional[Callable]~~                                                                                       |
| `lex_attr_getters`                | Custom functions for setting lexical attributes on tokens, e.g. `like_num`.<br />**Example:** [`lex_attrs.py`](%%GITHUB_SPACY/spacy/lang/en/lex_attrs.py) ~~Dict[int, Callable[[str], Any]]~~                                                                                                                    |
| `syntax_iterators`                | Functions that compute views of a `Doc` object based on its syntax. At the moment, only used for [noun chunks](/usage/linguistic-features#noun-chunks).<br />**Example:** [`syntax_iterators.py`](%%GITHUB_SPACY/spacy/lang/en/syntax_iterators.py). ~~Dict[str, Callable[[Union[Doc, Span]], Iterator[Span]]]~~ |
| `writing_system`                  | Information about the language's writing system, available via `Vocab.writing_system`. Defaults to: `{"direction": "ltr", "has_case": True, "has_letters": True}.`.<br />**Example:** [`zh/__init__.py`](%%GITHUB_SPACY/spacy/lang/zh/__init__.py) ~~Dict[str, Any]~~                                            |
| `config`                          | Default [config](/usage/training#config) added to `nlp.config`. This can include references to custom tokenizers or lemmatizers.<br />**Example:** [`zh/__init__.py`](%%GITHUB_SPACY/spacy/lang/zh/__init__.py) ~~Config~~                                                                                       |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = nlp.to_bytes(exclude=["tokenizer", "vocab"])
> nlp.from_disk("/pipeline", exclude=["ner"])
> ```

| Name        | Description                                                        |
| ----------- | ------------------------------------------------------------------ |
| `vocab`     | The shared [`Vocab`](/api/vocab).                                  |
| `tokenizer` | Tokenization rules and exceptions.                                 |
| `meta`      | The meta data, available as [`Language.meta`](/api/language#meta). |
| ...         | String names of pipeline components, e.g. `"ner"`.                 |

## FactoryMeta {#factorymeta new="3" tag="dataclass"}

The `FactoryMeta` contains the information about the component and its default
provided by the [`@Language.component`](/api/language#component) or
[`@Language.factory`](/api/language#factory) decorator. It's created whenever a
component is defined and stored on the `Language` class for each component
instance and factory instance.

| Name                    | Description                                                                                                                                                                                                                                                                                                                        |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `factory`               | The name of the registered component factory. ~~str~~                                                                                                                                                                                                                                                                              |
| `default_config`        | The default config, describing the default values of the factory arguments. ~~Dict[str, Any]~~                                                                                                                                                                                                                                     |
| `assigns`               | `Doc` or `Token` attributes assigned by this component, e.g. `["token.ent_id"]`. Used for [pipe analysis](/usage/processing-pipelines#analysis). ~~Iterable[str]~~                                                                                                                                                                 |
| `requires`              | `Doc` or `Token` attributes required by this component, e.g. `["token.ent_id"]`. Used for [pipe analysis](/usage/processing-pipelines#analysis). ~~Iterable[str]~~                                                                                                                                                                 |
| `retokenizes`           | Whether the component changes tokenization. Used for [pipe analysis](/usage/processing-pipelines#analysis). ~~bool~~                                                                                                                                                                                                               |
| `default_score_weights` | The scores to report during training, and their default weight towards the final score used to select the best model. Weights should sum to `1.0` per component and will be combined and normalized for the whole pipeline. If a weight is set to `None`, the score will not be logged or weighted. ~~Dict[str, Optional[float]]~~ |
| `scores`                | All scores set by the components if it's trainable, e.g. `["ents_f", "ents_r", "ents_p"]`. Based on the `default_score_weights` and used for [pipe analysis](/usage/processing-pipelines#analysis). ~~Iterable[str]~~                                                                                                              |
