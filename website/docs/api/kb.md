---
title: KnowledgeBase
teaser: A storage class for entities and aliases of a specific knowledge base (ontology)
tag: class
source: spacy/kb.pyx
---

The `KnowledgeBase` object provides a method to generate [`Candidate`](/api/candidate) 
objects, which are plausible external identifiers given a certain textual mention. 
Each such `Candidate` holds information from the relevant KB entities,
such as its frequency in text and possible aliases. 
Each entity in the knowledge base also has a pre-trained entity vector of a fixed size.

## KnowledgeBase.\_\_init\_\_ {#init tag="method"}

Create the knowledge base.

> #### Example
>
> ```python
> from spacy.kb import KnowledgeBase
> vocab = nlp.vocab
> kb = KnowledgeBase(vocab=vocab, entity_vector_length=64)
> ```

| Name                    | Type             | Description                               |
| ----------------------- | ---------------- | ----------------------------------------- |
| `vocab`                 | `Vocab`          | A `Vocab` object.                         |  
| `entity_vector_length`  | int              | Length of the fixed-size entity vectors.  |   
| **RETURNS**             | `KnowledgeBase`  | The newly constructed object.             |                                                                                     |


## KnowledgeBase.entity_vector_length {#entity_vector_length tag="property"}

The length of the fixed-size entity vectors in the knowledge base.

| Name        | Type | Description                               |
| ----------- | ---- | ----------------------------------------- |
| **RETURNS** | int  | Length of the fixed-size entity vectors.  |

## KnowledgeBase.add_entity {#add_entity tag="method"}

Add an entity to the knowledge base, specifying its corpus frequency 
and entity vector, which should be of length [`entity_vector_length`](/api/kb#entity_vector_length).

> #### Example
>
> ```python
> kb.add_entity(entity="Q42", freq=0.3, entity_vector=vector1)
> kb.add_entity(entity="Q463035", freq=0.1, entity_vector=vector2)
> ```

| Name            | Type          | Description                                       |
| --------------- | ------------- | ------------------------------------------------- |
| `entity`        | unicode       | The unique entity identifier                      |
| `freq`          | float         | The frequency of the entity in a typical corpus   |
| `entity_vector` | vector        | The entity vector of the entity                   |

## KnowledgeBase.set_entities {#set_entities tag="method"}

Define the full list of entities in the knowledge base, specifying the corpus frequency 
and entity vector for each entity.

> #### Example
>
> ```python
> kb.set_entities(entity_list=["Q42", "Q463035"], freq_list=[0.3, 0.1], vector_list=[vector1, vector2])
> ```

| Name          | Type          | Description                                       |
| ------------- | ------------- | ------------------------------------------------- |
| `entity_list` | iterable      | List of unique entity identifiers                 |
| `freq_list`   | iterable      | List of entity frequencies                        |
| `vector_list` | iterable      | List of entity vectors                            |

## KnowledgeBase.add_alias {#add_alias tag="method"}

Add an alias or mention to the knowledge base, specifying its potential KB identifiers 
and their prior probabilities. The entity identifiers should refer to entities previously
added with [`add_entity`](/api/kb#add_entity) or [`set_entities`](/api/kb#set_entities). 
The sum of the prior probabilities should not exceed 1.

> #### Example
>
> ```python
> kb.add_alias(alias="Douglas", entities=["Q42", "Q463035"], probabilities=[0.6, 0.3])
> ```

| Name           | Type          | Description                                        |
| -------------- | ------------- | -------------------------------------------------- |
| `alias`        | unicode       | The textual mention or alias                       |
| `entities`     | iterable      | The potential entities that the alias may refer to |
| `probabilities`| iterable      | The prior probabilities of each entity             |

## KnowledgeBase.\_\_len\_\_ {#len tag="method"}

Get the total number of entities in the knowledge base.

> #### Example
>
> ```python
> total_entities = len(kb)
> ```

| Name        | Type | Description                                   |
| ----------- | ---- | --------------------------------------------- |
| **RETURNS** | int  | The number of entities in the knowledge base. |

## KnowledgeBase.get_entity_strings {#get_entity_strings tag="method"}

Get a list of all entity IDs in the knowledge base.

> #### Example
>
> ```python
> all_entities = kb.get_entity_strings
> ```

| Name        | Type | Description                                   |
| ----------- | ---- | --------------------------------------------- |
| **RETURNS** | list | The list of entities in the knowledge base.   |

## KnowledgeBase.get_size_aliases {#get_size_aliases tag="method"}

Get the total number of aliases in the knowledge base.

> #### Example
>
> ```python
> total_aliases = kb.get_size_aliases
> ```

| Name        | Type | Description                                   |
| ----------- | ---- | --------------------------------------------- |
| **RETURNS** | int  | The number of aliases in the knowledge base.  |

## KnowledgeBase.get_alias_strings {#get_alias_strings tag="method"}

Get a list of all aliases in the knowledge base.

> #### Example
>
> ```python
> all_aliases = kb.get_alias_strings
> ```

| Name        | Type | Description                                   |
| ----------- | ---- | --------------------------------------------- |
| **RETURNS** | list | The list of aliases in the knowledge base.    |

## KnowledgeBase.get_candidates {#get_candidates tag="method"}

Given a certain textual mention as input, retrieve a list of candidate entities 
of type [`Candidate`](/api/candidate).

> #### Example
>
> ```python
> candidates = kb.get_candidates("Douglas")
> ```

| Name          | Type          | Description                                        |
| ------------- | ------------- | -------------------------------------------------- |
| `alias`       | unicode       | The textual mention or alias                       |
| **RETURNS**   | iterable      | The list of relevant `Candidate` objects           |

## KnowledgeBase.get_vector {#get_vector tag="method"}

Given a certain entity ID, retrieve its pre-trained entity vector.

> #### Example
>
> ```python
> vector = kb.get_vector("Q42")
> ```

| Name          | Type          | Description                                        |
| ------------- | ------------- | -------------------------------------------------- |
| `entity`      | unicode       | The entity ID                                      |
| **RETURNS**   | vector        | The entity vector                                  |

## KnowledgeBase.get_prior_prob {#get_prior_prob tag="method"}

Given a certain entity ID and a certain textual mention, retrieve 
the prior probability of the fact that the mention links to the entity ID.

> #### Example
>
> ```python
> probability = kb.get_prior_prob("Q42", "douglas")
> ```

| Name          | Type          | Description                                                     |
| ------------- | ------------- | --------------------------------------------------------------- |
| `entity`      | unicode       | The entity ID                                                   |
| `alias`       | unicode       | The textual mention or alias                                    |
| **RETURNS**   | float         | The prior probability of the `alias` referring to the `entity`  |

## KnowledgeBase.dump {#dump tag="method"}

Save the current state of the knowledge base to a directory.

> #### Example
>
> ```python
> kb.dump(my_location)
> ```

| Name          | Type             | Description                                                                                                              |
| ------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `loc`         | unicode / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects.    |

## KnowledgeBase.load_bulk {#load_bulk tag="method"}

Restore the state of the knowledge base from a given directory. Note that the [`Vocab`](/api/vocab) 
should also be the same as the one used to create the KB.

> #### Example
>
> ```python
> from spacy.kb import KnowledgeBase
> from spacy.vocab import Vocab
> vocab = Vocab().from_disk("/path/to/vocab")
> kb = KnowledgeBase(vocab=vocab, entity_vector_length=64)
> kb.load_bulk("/path/to/kb")
> ```


| Name        | Type             | Description                                                                               |
| ----------- | ---------------- | ----------------------------------------------------------------------------------------- |
| `loc`       | unicode / `Path` | A path to a directory. Paths may be either strings or `Path`-like objects.                |
| **RETURNS** | `KnowledgeBase`  | The modified `KnowledgeBase` object.                                                           |
