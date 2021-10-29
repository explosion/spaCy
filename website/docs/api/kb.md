---
title: KnowledgeBase
teaser:
  A storage class for entities and aliases of a specific knowledge base
  (ontology)
tag: class
source: spacy/kb.pyx
new: 2.2
---

The `KnowledgeBase` object provides a method to generate
[`Candidate`](/api/kb/#candidate) objects, which are plausible external
identifiers given a certain textual mention. Each such `Candidate` holds
information from the relevant KB entities, such as its frequency in text and
possible aliases. Each entity in the knowledge base also has a pretrained entity
vector of a fixed size.

## KnowledgeBase.\_\_init\_\_ {#init tag="method"}

Create the knowledge base.

> #### Example
>
> ```python
> from spacy.kb import KnowledgeBase
> vocab = nlp.vocab
> kb = KnowledgeBase(vocab=vocab, entity_vector_length=64)
> ```

| Name                   | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `vocab`                | The shared vocabulary. ~~Vocab~~                 |
| `entity_vector_length` | Length of the fixed-size entity vectors. ~~int~~ |

## KnowledgeBase.entity_vector_length {#entity_vector_length tag="property"}

The length of the fixed-size entity vectors in the knowledge base.

| Name        | Description                                      |
| ----------- | ------------------------------------------------ |
| **RETURNS** | Length of the fixed-size entity vectors. ~~int~~ |

## KnowledgeBase.add_entity {#add_entity tag="method"}

Add an entity to the knowledge base, specifying its corpus frequency and entity
vector, which should be of length
[`entity_vector_length`](/api/kb#entity_vector_length).

> #### Example
>
> ```python
> kb.add_entity(entity="Q42", freq=32, entity_vector=vector1)
> kb.add_entity(entity="Q463035", freq=111, entity_vector=vector2)
> ```

| Name            | Description                                                |
| --------------- | ---------------------------------------------------------- |
| `entity`        | The unique entity identifier. ~~str~~                      |
| `freq`          | The frequency of the entity in a typical corpus. ~~float~~ |
| `entity_vector` | The pretrained vector of the entity. ~~numpy.ndarray~~     |

## KnowledgeBase.set_entities {#set_entities tag="method"}

Define the full list of entities in the knowledge base, specifying the corpus
frequency and entity vector for each entity.

> #### Example
>
> ```python
> kb.set_entities(entity_list=["Q42", "Q463035"], freq_list=[32, 111], vector_list=[vector1, vector2])
> ```

| Name          | Description                                                      |
| ------------- | ---------------------------------------------------------------- |
| `entity_list` | List of unique entity identifiers. ~~Iterable[Union[str, int]]~~ |
| `freq_list`   | List of entity frequencies. ~~Iterable[int]~~                    |
| `vector_list` | List of entity vectors. ~~Iterable[numpy.ndarray]~~              |

## KnowledgeBase.add_alias {#add_alias tag="method"}

Add an alias or mention to the knowledge base, specifying its potential KB
identifiers and their prior probabilities. The entity identifiers should refer
to entities previously added with [`add_entity`](/api/kb#add_entity) or
[`set_entities`](/api/kb#set_entities). The sum of the prior probabilities
should not exceed 1. Note that an empty string can not be used as alias.

> #### Example
>
> ```python
> kb.add_alias(alias="Douglas", entities=["Q42", "Q463035"], probabilities=[0.6, 0.3])
> ```

| Name            | Description                                                                       |
| --------------- | --------------------------------------------------------------------------------- |
| `alias`         | The textual mention or alias. Can not be the empty string. ~~str~~                |
| `entities`      | The potential entities that the alias may refer to. ~~Iterable[Union[str, int]]~~ |
| `probabilities` | The prior probabilities of each entity. ~~Iterable[float]~~                       |

## KnowledgeBase.\_\_len\_\_ {#len tag="method"}

Get the total number of entities in the knowledge base.

> #### Example
>
> ```python
> total_entities = len(kb)
> ```

| Name        | Description                                           |
| ----------- | ----------------------------------------------------- |
| **RETURNS** | The number of entities in the knowledge base. ~~int~~ |

## KnowledgeBase.get_entity_strings {#get_entity_strings tag="method"}

Get a list of all entity IDs in the knowledge base.

> #### Example
>
> ```python
> all_entities = kb.get_entity_strings()
> ```

| Name        | Description                                               |
| ----------- | --------------------------------------------------------- |
| **RETURNS** | The list of entities in the knowledge base. ~~List[str]~~ |

## KnowledgeBase.get_size_aliases {#get_size_aliases tag="method"}

Get the total number of aliases in the knowledge base.

> #### Example
>
> ```python
> total_aliases = kb.get_size_aliases()
> ```

| Name        | Description                                          |
| ----------- | ---------------------------------------------------- |
| **RETURNS** | The number of aliases in the knowledge base. ~~int~~ |

## KnowledgeBase.get_alias_strings {#get_alias_strings tag="method"}

Get a list of all aliases in the knowledge base.

> #### Example
>
> ```python
> all_aliases = kb.get_alias_strings()
> ```

| Name        | Description                                              |
| ----------- | -------------------------------------------------------- |
| **RETURNS** | The list of aliases in the knowledge base. ~~List[str]~~ |

## KnowledgeBase.get_alias_candidates {#get_alias_candidates tag="method"}

Given a certain textual mention as input, retrieve a list of candidate entities
of type [`Candidate`](/api/kb/#candidate).

> #### Example
>
> ```python
> candidates = kb.get_alias_candidates("Douglas")
> ```

| Name        | Description                                                   |
| ----------- | ------------------------------------------------------------- |
| `alias`     | The textual mention or alias. ~~str~~                         |
| **RETURNS** | The list of relevant `Candidate` objects. ~~List[Candidate]~~ |

## KnowledgeBase.get_vector {#get_vector tag="method"}

Given a certain entity ID, retrieve its pretrained entity vector.

> #### Example
>
> ```python
> vector = kb.get_vector("Q42")
> ```

| Name        | Description                          |
| ----------- | ------------------------------------ |
| `entity`    | The entity ID. ~~str~~               |
| **RETURNS** | The entity vector. ~~numpy.ndarray~~ |

## KnowledgeBase.get_prior_prob {#get_prior_prob tag="method"}

Given a certain entity ID and a certain textual mention, retrieve the prior
probability of the fact that the mention links to the entity ID.

> #### Example
>
> ```python
> probability = kb.get_prior_prob("Q42", "Douglas")
> ```

| Name        | Description                                                               |
| ----------- | ------------------------------------------------------------------------- |
| `entity`    | The entity ID. ~~str~~                                                    |
| `alias`     | The textual mention or alias. ~~str~~                                     |
| **RETURNS** | The prior probability of the `alias` referring to the `entity`. ~~float~~ |

## KnowledgeBase.to_disk {#to_disk tag="method"}

Save the current state of the knowledge base to a directory.

> #### Example
>
> ```python
> kb.to_disk(loc)
> ```

| Name  | Description                                                                                                                                |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `loc` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |

## KnowledgeBase.from_disk {#from_disk tag="method"}

Restore the state of the knowledge base from a given directory. Note that the
[`Vocab`](/api/vocab) should also be the same as the one used to create the KB.

> #### Example
>
> ```python
> from spacy.kb import KnowledgeBase
> from spacy.vocab import Vocab
> vocab = Vocab().from_disk("/path/to/vocab")
> kb = KnowledgeBase(vocab=vocab, entity_vector_length=64)
> kb.from_disk("/path/to/kb")
> ```

| Name        | Description                                                                                     |
| ----------- | ----------------------------------------------------------------------------------------------- |
| `loc`       | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| **RETURNS** | The modified `KnowledgeBase` object. ~~KnowledgeBase~~                                          |

## Candidate {#candidate tag="class"}

A `Candidate` object refers to a textual mention (alias) that may or may not be
resolved to a specific entity from a `KnowledgeBase`. This will be used as input
for the entity linking algorithm which will disambiguate the various candidates
to the correct one. Each candidate `(alias, entity)` pair is assigned to a
certain prior probability.

### Candidate.\_\_init\_\_ {#candidate-init tag="method"}

Construct a `Candidate` object. Usually this constructor is not called directly,
but instead these objects are returned by the `get_candidates` method of the
[`entity_linker`](/api/entitylinker) pipe.

> #### Example
>
> ```python
> from spacy.kb import Candidate
> candidate = Candidate(kb, entity_hash, entity_freq, entity_vector, alias_hash, prior_prob)
> ```

| Name          | Description                                                               |
| ------------- | ------------------------------------------------------------------------- |
| `kb`          | The knowledge base that defined this candidate. ~~KnowledgeBase~~         |
| `entity_hash` | The hash of the entity's KB ID. ~~int~~                                   |
| `entity_freq` | The entity frequency as recorded in the KB. ~~float~~                     |
| `alias_hash`  | The hash of the textual mention or alias. ~~int~~                         |
| `prior_prob`  | The prior probability of the `alias` referring to the `entity`. ~~float~~ |

## Candidate attributes {#candidate-attributes}

| Name            | Description                                                              |
| --------------- | ------------------------------------------------------------------------ |
| `entity`        | The entity's unique KB identifier. ~~int~~                               |
| `entity_`       | The entity's unique KB identifier. ~~str~~                               |
| `alias`         | The alias or textual mention. ~~int~~                                    |
| `alias_`        | The alias or textual mention. ~~str~~                                    |
| `prior_prob`    | The prior probability of the `alias` referring to the `entity`. ~~long~~ |
| `entity_freq`   | The frequency of the entity in a typical corpus. ~~long~~                |
| `entity_vector` | The pretrained vector of the entity. ~~numpy.ndarray~~                   |
