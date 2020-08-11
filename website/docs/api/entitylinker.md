---
title: EntityLinker
tag: class
source: spacy/pipeline/entity_linker.py
new: 2.2
teaser: 'Pipeline component for named entity linking and disambiguation'
api_base_class: /api/pipe
api_string_name: entity_linker
api_trainable: true
---

An `EntityLinker` component disambiguates textual mentions (tagged as named
entities) to unique identifiers, grounding the named entities into the "real
world". It requires a `KnowledgeBase`, as well as a function to generate
plausible candidates from that `KnowledgeBase` given a certain textual mention,
and a ML model to pick the right candidate, given the local context of the
mention.

## Config and implementation {#config}

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config). See the
[model architectures](/api/architectures) documentation for details on the
architectures and their arguments and hyperparameters.

> #### Example
>
> ```python
> from spacy.pipeline.entity_linker import DEFAULT_NEL_MODEL
> config = {
>    "labels_discard": [],
>    "incl_prior": True,
>    "incl_context": True,
>    "model": DEFAULT_NEL_MODEL,
>    "kb_loader": {'@assets': 'spacy.EmptyKB.v1', 'entity_vector_length': 64},
>    "get_candidates": {'@assets': 'spacy.CandidateGenerator.v1'},
> }
> nlp.add_pipe("entity_linker", config=config)
> ```

| Setting          | Type                                                     | Description                                                                 | Default                                                |
| ---------------- | -------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------ |
| `labels_discard` | `Iterable[str]`                                          | NER labels that will automatically get a "NIL" prediction.                  | `[]`                                                   |
| `incl_prior`     | bool                                                     | Whether or not to include prior probabilities from the KB in the model.     | `True`                                                 |
| `incl_context`   | bool                                                     | Whether or not to include the local context in the model.                   | `True`                                                 |
| `model`          | [`Model`](https://thinc.ai/docs/api-model)               | The model to use.                                                           | [EntityLinker](/api/architectures#EntityLinker)        |
| `kb_loader`      | `Callable[[Vocab], KnowledgeBase]`                       | Function that creates a [`KnowledgeBase`](/api/kb) from a `Vocab` instance. | An empty KnowledgeBase with `entity_vector_length` 64. |
| `get_candidates` | `Callable[[KnowledgeBase, "Span"], Iterable[Candidate]]` | Function that generates plausible candidates for a given `Span` object.     | Built-in dictionary-lookup function.                   |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/entity_linker.py
```

## EntityLinker.\_\_init\_\_ {#init tag="method"}

> #### Example
>
> ```python
> # Construction via add_pipe with default model
> entity_linker = nlp.add_pipe("entity_linker")
>
> # Construction via add_pipe with custom model
> config = {"model": {"@architectures": "my_el.v1"}}
> entity_linker = nlp.add_pipe("entity_linker", config=config)
>
> # Construction via add_pipe with custom KB and candidate generation
> config = {"kb_loader": {"@assets": "my_kb.v1"}, "get_candidates": {"@assets": "my_candidates.v1"},}
> entity_linker = nlp.add_pipe("entity_linker", config=config)
>
> # Construction from class
> from spacy.pipeline import EntityLinker
> entity_linker = EntityLinker(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe).

Note that both the internal KB as well as the Candidate generator can be
customized by providing custom registered functions.

| Name             | Type                                                     | Description                                                                                 |
| ---------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `vocab`          | `Vocab`                                                  | The shared vocabulary.                                                                      |
| `model`          | `Model`                                                  | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component.             |
| `name`           | str                                                      | String name of the component instance. Used to add entries to the `losses` during training. |
| _keyword-only_   |                                                          |                                                                                             |
| `kb_loader`      | `Callable[[Vocab], KnowledgeBase]`                       | Function that creates a [`KnowledgeBase`](/api/kb) from a `Vocab` instance.                 |
| `get_candidates` | `Callable[[KnowledgeBase, "Span"], Iterable[Candidate]]` | Function that generates plausible candidates for a given `Span` object.                     |
| `labels_discard` | `Iterable[str]`                                          | NER labels that will automatically get a "NIL" prediction.                                  |
| `incl_prior`     | bool                                                     | Whether or not to include prior probabilities from the KB in the model.                     |
| `incl_context`   | bool                                                     | Whether or not to include the local context in the model.                                   |

## EntityLinker.\_\_call\_\_ {#call tag="method"}

Apply the pipe to one document. The document is modified in place, and returned.
This usually happens under the hood when the `nlp` object is called on a text
and all pipeline components are applied to the `Doc` in order. Both
[`__call__`](/api/entitylinker#call) and [`pipe`](/api/entitylinker#pipe)
delegate to the [`predict`](/api/entitylinker#predict) and
[`set_annotations`](/api/entitylinker#set_annotations) methods.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> entity_linker = nlp.add_pipe("entity_linker")
> # This usually happens under the hood
> processed = entity_linker(doc)
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| `doc`       | `Doc` | The document to process. |
| **RETURNS** | `Doc` | The processed document.  |

## EntityLinker.pipe {#pipe tag="method"}

Apply the pipe to a stream of documents. This usually happens under the hood
when the `nlp` object is called on a text and all pipeline components are
applied to the `Doc` in order. Both [`__call__`](/api/entitylinker#call) and
[`pipe`](/api/entitylinker#pipe) delegate to the
[`predict`](/api/entitylinker#predict) and
[`set_annotations`](/api/entitylinker#set_annotations) methods.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> for doc in entity_linker.pipe(docs, batch_size=50):
>     pass
> ```

| Name           | Type            | Description                                            |
| -------------- | --------------- | ------------------------------------------------------ |
| `stream`       | `Iterable[Doc]` | A stream of documents.                                 |
| _keyword-only_ |                 |                                                        |
| `batch_size`   | int             | The number of texts to buffer. Defaults to `128`.      |
| **YIELDS**     | `Doc`           | Processed documents in the order of the original text. |

## EntityLinker.begin_training {#begin_training tag="method"}

Initialize the component for training and return an
[`Optimizer`](https://thinc.ai/docs/api-optimizers). `get_examples` should be a
function that returns an iterable of [`Example`](/api/example) objects. The data
examples are used to **initialize the model** of the component and can either be
the full training data or a representative sample. Initialization includes
validating the network,
[inferring missing shapes](https://thinc.ai/docs/usage-models#validation) and
setting up the label scheme based on the data.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker", last=True)
> optimizer = entity_linker.begin_training(lambda: [], pipeline=nlp.pipeline)
> ```

| Name           | Type                                                | Description                                                                                                         |
| -------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | `Callable[[], Iterable[Example]]`                   | Optional function that returns gold-standard annotations in the form of [`Example`](/api/example) objects.          |
| _keyword-only_ |                                                     |                                                                                                                     |
| `pipeline`     | `List[Tuple[str, Callable]]`                        | Optional list of pipeline components that this component is part of.                                                |
| `sgd`          | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | An optional optimizer. Will be created via [`create_optimizer`](/api/dependencyparser#create_optimizer) if not set. |
| **RETURNS**    | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                      |

## EntityLinker.predict {#predict tag="method"}

Apply the component's model to a batch of [`Doc`](/api/doc) objects, without
modifying them. Returns the KB IDs for each entity in each doc, including `NIL`
if there is no prediction.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> kb_ids = entity_linker.predict([doc1, doc2])
> ```

| Name        | Type            | Description                                                  |
| ----------- | --------------- | ------------------------------------------------------------ |
| `docs`      | `Iterable[Doc]` | The documents to predict.                                    |
| **RETURNS** | `List[str]`     | The predicted KB identifiers for the entities in the `docs`. |

## EntityLinker.set_annotations {#set_annotations tag="method"}

Modify a batch of documents, using pre-computed entity IDs for a list of named
entities.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> kb_ids = entity_linker.predict([doc1, doc2])
> entity_linker.set_annotations([doc1, doc2], kb_ids)
> ```

| Name     | Type            | Description                                                                                       |
| -------- | --------------- | ------------------------------------------------------------------------------------------------- |
| `docs`   | `Iterable[Doc]` | The documents to modify.                                                                          |
| `kb_ids` | `List[str]`     | The knowledge base identifiers for the entities in the docs, predicted by `EntityLinker.predict`. |

## EntityLinker.update {#update tag="method"}

Learn from a batch of [`Example`](/api/example) objects, updating both the
pipe's entity linking model and context encoder. Delegates to
[`predict`](/api/entitylinker#predict).

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> optimizer = nlp.begin_training()
> losses = entity_linker.update(examples, sgd=optimizer)
> ```

| Name              | Type                                                | Description                                                                                                                                   |
| ----------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | `Iterable[Example]`                                 | A batch of [`Example`](/api/example) objects to learn from.                                                                                   |
| _keyword-only_    |                                                     |                                                                                                                                               |
| `drop`            | float                                               | The dropout rate.                                                                                                                             |
| `set_annotations` | bool                                                | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](/api/textcategorizer#set_annotations). |
| `sgd`             | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer.                                                                                                                                |
| `losses`          | `Dict[str, float]`                                  | Optional record of the loss during training. Updated using the component name as the key.                                                     |
| **RETURNS**       | `Dict[str, float]`                                  | The updated `losses` dictionary.                                                                                                              |

## EntityLinker.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> optimizer = entity_linker.create_optimizer()
> ```

| Name        | Type                                                | Description    |
| ----------- | --------------------------------------------------- | -------------- |
| **RETURNS** | [`Optimizer`](https://thinc.ai/docs/api-optimizers) | The optimizer. |

## EntityLinker.use_params {#use_params tag="method, contextmanager"}

Modify the pipe's model, to use the given parameter values. At the end of the
context, the original parameters are restored.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> with entity_linker.use_params(optimizer.averages):
>     entity_linker.to_disk("/best_model")
> ```

| Name     | Type | Description                               |
| -------- | ---- | ----------------------------------------- |
| `params` | dict | The parameter values to use in the model. |

## EntityLinker.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> entity_linker.to_disk("/path/to/entity_linker")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## EntityLinker.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> entity_linker.from_disk("/path/to/entity_linker")
> ```

| Name           | Type            | Description                                                                |
| -------------- | --------------- | -------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                            |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `EntityLinker`  | The modified `EntityLinker` object.                                        |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = entity_linker.to_disk("/path", exclude=["vocab"])
> ```

| Name    | Description                                                    |
| ------- | -------------------------------------------------------------- |
| `vocab` | The shared [`Vocab`](/api/vocab).                              |
| `cfg`   | The config file. You usually don't want to exclude this.       |
| `model` | The binary model data. You usually don't want to exclude this. |
| `kb`    | The knowledge base. You usually don't want to exclude this.    |
