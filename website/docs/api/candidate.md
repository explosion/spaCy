---
title: Candidate
teaser: A candidate entity (from a knowledge base) to resolve a textual mention (named entity) to.
tag: class
source: spacy/kb.pyx
---

## Candidate.\_\_init\_\_ {#init tag="method"}

Construct a `Candidate` object. Usually this constructor is not called directly,
but instead these objects are returned by the [`get_candidates`](/api/kb#get_candidates) method
of a `KnowledgeBase`.

> #### Example
>
> ```python
> from spacy.kb import Candidate
> candidate = Candidate(kb, entity_hash, entity_freq, entity_vector, alias_hash, prior_prob)
> ```

| Name          | Type            | Description                                                    |
| ------------- | --------------- | -------------------------------------------------------------- |
| `kb`          | `KnowledgeBase` | The knowledge base that defined this candidate.                |
| `entity_hash` | int             | The hash of the entity's KB ID.                                |
| `entity_freq` | float           | The entity frequency as recorded in the KB.                    |
| `alias_hash`  | int             | The hash of the textual mention or alias.                      |
| `prior_prob`  | float           | The prior probability of the `alias` referring to the `entity` |
| **RETURNS**   | `Candidate`     | The newly constructed object.                                  |

## Attributes {#attributes}

| Name                   | Type         | Description                                                        |
| ---------------------- | ------------ | ------------------------------------------------------------------ |
| `entity`               | int          | The entity's unique KB identifier                                  |
| `entity_`              | unicode      | The entity's unique KB identifier                                  |
| `alias`                | int          | The alias or textual mention                                       |
| `alias_`               | unicode      | The alias or textual mention                                       |
| `prior_prob`           | long         | The prior probability of the `alias` referring to the `entity`     |
| `entity_freq`          | long         | The frequency of the entity in a typical corpus                    |
| `entity_vector`        | vector       | The pre-trained vector of the entity                               |
