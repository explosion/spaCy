---
title: KnowledgeBase
teaser:
  A storage class for entities and aliases of a specific knowledge base
  (ontology)
tag: class
source: spacy/kb/kb.pyx
new: 2.2
---

The `KnowledgeBase` object is an abstract class providing a method to generate
[`Candidate`](/api/kb#candidate) objects, which are plausible external
identifiers given a certain textual mention. Each such `Candidate` holds
information from the relevant KB entities, such as its frequency in text and
possible aliases. Each entity in the knowledge base also has a pretrained entity
vector of a fixed size.

Beyond that, `KnowledgeBase` classes have to implement a number of utility
functions called by the [`EntityLinker`](/api/entitylinker) component.

<Infobox variant="warning">

This class was not abstract up to spaCy version 3.5. The `KnowledgeBase`
implementation up to that point is available as `InMemoryLookupKB` from 3.5
onwards.

</Infobox>

## KnowledgeBase.\_\_init\_\_ {#init tag="method"}

`KnowledgeBase` is an abstract class and cannot be instantiated. Its child
classes should call `__init__()` to set up some necessary attributes.

> #### Example
>
> ```python
> from spacy.kb import KnowledgeBase
> from spacy.vocab import Vocab
>
> class FullyImplementedKB(KnowledgeBase):
>   def __init__(self, vocab: Vocab, entity_vector_length: int):
>       super().__init__(vocab, entity_vector_length)
>       ...
> vocab = nlp.vocab
> kb = FullyImplementedKB(vocab=vocab, entity_vector_length=64)
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

## KnowledgeBase.get_candidates {#get_candidates tag="method"}

Given a certain textual mention as input, retrieve a list of candidate entities
of type [`Candidate`](/api/kb#candidate).

> #### Example
>
> ```python
> from spacy.lang.en import English
> nlp = English()
> doc = nlp("Douglas Adams wrote 'The Hitchhiker's Guide to the Galaxy'.")
> candidates = kb.get_candidates(doc[0:2])
> ```

| Name        | Description                                                          |
| ----------- | -------------------------------------------------------------------- |
| `mention`   | The textual mention or alias. ~~Span~~                               |
| **RETURNS** | An iterable of relevant `Candidate` objects. ~~Iterable[Candidate]~~ |

## KnowledgeBase.get_candidates_batch {#get_candidates_batch tag="method"}

Same as [`get_candidates()`](/api/kb#get_candidates), but for an arbitrary
number of mentions. The [`EntityLinker`](/api/entitylinker) component will call
`get_candidates_batch()` instead of `get_candidates()`, if the config parameter
`candidates_batch_size` is greater or equal than 1.

The default implementation of `get_candidates_batch()` executes
`get_candidates()` in a loop. We recommend implementing a more efficient way to
retrieve candidates for multiple mentions at once, if performance is of concern
to you.

> #### Example
>
> ```python
> from spacy.lang.en import English
> nlp = English()
> doc = nlp("Douglas Adams wrote 'The Hitchhiker's Guide to the Galaxy'.")
> candidates = kb.get_candidates((doc[0:2], doc[3:]))
> ```

| Name        | Description                                                                                  |
| ----------- | -------------------------------------------------------------------------------------------- |
| `mentions`  | The textual mention or alias. ~~Iterable[Span]~~                                             |
| **RETURNS** | An iterable of iterable with relevant `Candidate` objects. ~~Iterable[Iterable[Candidate]]~~ |

## KnowledgeBase.get_alias_candidates {#get_alias_candidates tag="method"}

<Infobox variant="warning">
This method is _not_ available from spaCy 3.5 onwards.
</Infobox>

From spaCy 3.5 on `KnowledgeBase` is an abstract class (with
[`InMemoryLookupKB`](/api/kb_in_memory) being a drop-in replacement) to allow
more flexibility in customizing knowledge bases. Some of its methods were moved
to [`InMemoryLookupKB`](/api/kb_in_memory) during this refactoring, one of those
being `get_alias_candidates()`. This method is now available as
[`InMemoryLookupKB.get_alias_candidates()`](/api/kb_in_memory#get_alias_candidates).
Note: [`InMemoryLookupKB.get_candidates()`](/api/kb_in_memory#get_candidates)
defaults to
[`InMemoryLookupKB.get_alias_candidates()`](/api/kb_in_memory#get_alias_candidates).

## KnowledgeBase.get_vector {#get_vector tag="method"}

Given a certain entity ID, retrieve its pretrained entity vector.

> #### Example
>
> ```python
> vector = kb.get_vector("Q42")
> ```

| Name        | Description                            |
| ----------- | -------------------------------------- |
| `entity`    | The entity ID. ~~str~~                 |
| **RETURNS** | The entity vector. ~~Iterable[float]~~ |

## KnowledgeBase.get_vectors {#get_vectors tag="method"}

Same as [`get_vector()`](/api/kb#get_vector), but for an arbitrary number of
entity IDs.

The default implementation of `get_vectors()` executes `get_vector()` in a loop.
We recommend implementing a more efficient way to retrieve vectors for multiple
entities at once, if performance is of concern to you.

> #### Example
>
> ```python
> vectors = kb.get_vectors(("Q42", "Q3107329"))
> ```

| Name        | Description                                               |
| ----------- | --------------------------------------------------------- |
| `entities`  | The entity IDs. ~~Iterable[str]~~                         |
| **RETURNS** | The entity vectors. ~~Iterable[Iterable[numpy.ndarray]]~~ |

## KnowledgeBase.to_disk {#to_disk tag="method"}

Save the current state of the knowledge base to a directory.

> #### Example
>
> ```python
> kb.to_disk(path)
> ```

| Name      | Description                                                                                                                                |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| `exclude` | List of components to exclude. ~~Iterable[str]~~                                                                                           |

## KnowledgeBase.from_disk {#from_disk tag="method"}

Restore the state of the knowledge base from a given directory. Note that the
[`Vocab`](/api/vocab) should also be the same as the one used to create the KB.

> #### Example
>
> ```python
> from spacy.vocab import Vocab
> vocab = Vocab().from_disk("/path/to/vocab")
> kb = FullyImplementedKB(vocab=vocab, entity_vector_length=64)
> kb.from_disk("/path/to/kb")
> ```

| Name        | Description                                                                                     |
| ----------- | ----------------------------------------------------------------------------------------------- |
| `loc`       | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| `exclude`   | List of components to exclude. ~~Iterable[str]~~                                                |
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
