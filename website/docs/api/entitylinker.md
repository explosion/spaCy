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

| Setting          | Description                                                                                                                                                                                                                                                              |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `labels_discard` | NER labels that will automatically get a "NIL" prediction. Defaults to `[]`. ~~Iterable[str]~~                                                                                                                                                                           |
| `incl_prior`     | Whether or not to include prior probabilities from the KB in the model. Defaults to `True`. ~~bool~~                                                                                                                                                                     |
| `incl_context`   | Whether or not to include the local context in the model. Defaults to `True`. ~~bool~~                                                                                                                                                                                   |
| `model`          | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. Defaults to [EntityLinker](/api/architectures#EntityLinker). ~~Model~~                                                                                                                   |
| `kb_loader`      | Function that creates a [`KnowledgeBase`](/api/kb) from a `Vocab` instance. Defaults to [EmptyKB](/api/architectures#EmptyKB), a function returning an empty `KnowledgeBase` with an `entity_vector_length` of `64`. ~~Callable[[Vocab], KnowledgeBase]~~                |
| `get_candidates` | Function that generates plausible candidates for a given `Span` object. Defaults to [CandidateGenerator](/api/architectures#CandidateGenerator), a function looking up exact, case-dependent aliases in the KB. ~~Callable[[KnowledgeBase, Span], Iterable[Candidate]]~~ |

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
> config = {"kb": {"@assets": "my_kb.v1"}}
> entity_linker = nlp.add_pipe("entity_linker", config=config)
>
> # Construction from class
> from spacy.pipeline import EntityLinker
> entity_linker = EntityLinker(nlp.vocab, model)
> ```

Create a new pipeline instance. In your application, you would normally use a
shortcut for this and instantiate the component using its string name and
[`nlp.add_pipe`](/api/language#add_pipe). Note that both the internal
`KnowledgeBase` as well as the Candidate generator can be customized by
providing custom registered functions.

| Name             | Description                                                                                                                      |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`          | The shared vocabulary. ~~Vocab~~                                                                                                 |
| `model`          | The [`Model`](https://thinc.ai/docs/api-model) powering the pipeline component. ~~Model~~                                        |
| `name`           | String name of the component instance. Used to add entries to the `losses` during training. ~~str~~                              |
| _keyword-only_   |                                                                                                                                  |  |
| `kb_loader`      | Function that creates a [`KnowledgeBase`](/api/kb) from a `Vocab` instance. ~~Callable[[Vocab], KnowledgeBase]~~                 |
| `get_candidates` | Function that generates plausible candidates for a given `Span` object. ~~Callable[[KnowledgeBase, Span], Iterable[Candidate]]~~ |
| `labels_discard` | NER labels that will automatically get a `"NIL"` prediction. ~~Iterable[str]~~                                                   |
| `incl_prior`     | Whether or not to include prior probabilities from the KB in the model. ~~bool~~                                                 |
| `incl_context`   | Whether or not to include the local context in the model. ~~bool~~                                                               |

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

| Name        | Description                      |
| ----------- | -------------------------------- |
| `doc`       | The document to process. ~~Doc~~ |
| **RETURNS** | The processed document. ~~Doc~~  |

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

| Name           | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `stream`       | A stream of documents. ~~Iterable[Doc]~~                      |
| _keyword-only_ |                                                               |
| `batch_size`   | The number of documents to buffer. Defaults to `128`. ~~int~~ |
| **YIELDS**     | The processed documents in order. ~~Doc~~                     |

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

| Name           | Description                                                                                                                           |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. ~~Callable[[], Iterable[Example]]~~ |
| _keyword-only_ |                                                                                                                                       |
| `pipeline`     | Optional list of pipeline components that this component is part of. ~~Optional[List[Tuple[str, Callable[[Doc], Doc]]]]~~             |
| `sgd`          | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~                         |
| **RETURNS**    | The optimizer. ~~Optimizer~~                                                                                                          |

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

| Name        | Description                                 |
| ----------- | ------------------------------------------- |
| `docs`      | The documents to predict. ~~Iterable[Doc]~~ |
| **RETURNS** | `List[str]`                                 | The predicted KB identifiers for the entities in the `docs`. ~~List[str]~~ |

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

| Name     | Description                                                                                                     |
| -------- | --------------------------------------------------------------------------------------------------------------- |
| `docs`   | The documents to modify. ~~Iterable[Doc]~~                                                                      |
| `kb_ids` | The knowledge base identifiers for the entities in the docs, predicted by `EntityLinker.predict`. ~~List[str]~~ |

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

| Name              | Description                                                                                                                        |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `examples`        | A batch of [`Example`](/api/example) objects to learn from. ~~Iterable[Example]~~                                                  |
| _keyword-only_    |                                                                                                                                    |  |
| `drop`            | The dropout rate. ~~float~~                                                                                                        |
| `set_annotations` | Whether or not to update the `Example` objects with the predictions, delegating to [`set_annotations`](#set_annotations). ~~bool~~ |
| `sgd`             | An optimizer. Will be created via [`create_optimizer`](#create_optimizer) if not set. ~~Optional[Optimizer]~~                      |
| `losses`          | Optional record of the loss during training. Updated using the component name as the key. ~~Optional[Dict[str, float]]~~           |
| **RETURNS**       | The updated `losses` dictionary. ~~Dict[str, float]~~                                                                              |

## EntityLinker.create_optimizer {#create_optimizer tag="method"}

Create an optimizer for the pipeline component.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> optimizer = entity_linker.create_optimizer()
> ```

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The optimizer. ~~Optimizer~~ |

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

| Name     | Description                                        |
| -------- | -------------------------------------------------- |
| `params` | The parameter values to use in the model. ~~dict~~ |

## EntityLinker.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> entity_linker.to_disk("/path/to/entity_linker")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## EntityLinker.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> entity_linker = nlp.add_pipe("entity_linker")
> entity_linker.from_disk("/path/to/entity_linker")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `EntityLinker` object. ~~EntityLinker~~                                            |

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
