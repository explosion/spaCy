---
title: Candidate
teaser:
  Object associating a textual mention with a specific entity contained in a
  `KnowledgeBase`.
tag: class
source: spacy/kb/candidate.pyx
new: 2.2
---

A `Candidate` object refers to a textual mention that may or may not be resolved
to a specific entity from a `KnowledgeBase`. This will be used as input for the
entity linking algorithm which will disambiguate the various candidates to the
correct one. Each candidate `(alias, entity)` pair is assigned to a certain
prior probability.

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
