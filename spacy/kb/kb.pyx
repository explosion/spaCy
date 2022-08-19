# cython: infer_types=True, profile=True

from pathlib import Path
from typing import Iterable, Tuple, Union
from cymem.cymem cimport Pool

from .tokens import Span
from .util import SimpleFrozenList
from .errors import Errors


cdef class Candidate:
    """A `Candidate` object refers to a textual mention (`alias`) that may or may not be resolved
    to a specific `entity` from a Knowledge Base. This will be used as input for the entity linking
    algorithm which will disambiguate the various candidates to the correct one.
    Each candidate (alias, entity) pair is assigned a certain prior probability.

    DOCS: https://spacy.io/api/kb/#candidate_init
    """

    def __init__(self, KnowledgeBase kb, entity_hash, entity_freq, entity_vector, alias_hash, prior_prob):
        self.kb = kb
        self.entity_hash = entity_hash
        self.entity_freq = entity_freq
        self.entity_vector = entity_vector
        self.alias_hash = alias_hash
        self.prior_prob = prior_prob

    @property
    def entity(self):
        """RETURNS (uint64): hash of the entity's KB ID/name"""
        return self.entity_hash

    @property
    def entity_(self):
        """RETURNS (str): ID/name of this entity in the KB"""
        return self.kb.vocab.strings[self.entity_hash]

    @property
    def alias(self):
        """RETURNS (uint64): hash of the alias"""
        return self.alias_hash

    @property
    def alias_(self):
        """RETURNS (str): ID of the original alias"""
        return self.kb.vocab.strings[self.alias_hash]

    @property
    def entity_freq(self):
        return self.entity_freq

    @property
    def entity_vector(self):
        return self.entity_vector

    @property
    def prior_prob(self):
        return self.prior_prob


def get_candidates_batch(kb: KnowledgeBase, mentions: Iterable[Union[Span, str]]) -> Iterable[Iterable[Candidate]]:
    """
    Return candidate entities for the given mentions and fetching appropriate entries from the index.
    kb (KnowledgeBase): Knowledge base to query.
    mention (Iterable[Union[Span, str]]): Entity mentions for which to identify candidates.
    RETURNS (Iterable[Iterable[Candidate]]): Identified candidates.
    """
    return kb.get_candidates_batch(mentions)


def get_candidates(kb: KnowledgeBase, mention: Union[Span, str]) -> Iterable[Candidate]:
    """
    Return candidate entities for a given mention and fetching appropriate entries from the index.
    kb (KnowledgeBase): Knowledge base to query.
    mention (Union[Span, str]): Entity mention for which to identify candidates.
    RETURNS (Iterable[Candidate]): Identified candidates.
    """
    return kb.get_candidates(mention)


cdef class KnowledgeBase:
    """A `KnowledgeBase` instance stores unique identifiers for entities and their textual aliases,
    to support entity linking of named entities to real-world concepts.
    This is an abstract class and requires its operations to be implemented.

    DOCS: https://spacy.io/api/kb
    """

    def __init__(self, vocab: Vocab, entity_vector_length: int):
        """Create a InMemoryLookupKB."""
        self.vocab = vocab
        self.entity_vector_length = entity_vector_length
        self.mem = Pool()

    def get_candidates_batch(self, mentions: Union[Iterable[Span], Iterable[str]]) -> Iterable[Iterable[Candidate]]:
        """
        Return candidate entities for specified texts. Each candidate defines the entity, the original alias,
        and the prior probability of that alias resolving to that entity.
        If no candidate is found for a given text, an empty list is returned.
        mentions (Union[Iterable[Span], Iterable[str]]): Mentions for which to get candidates.
        RETURNS (Iterable[Iterable[Candidate]]): Identified candidates.
        """
        return [self.get_candidates(span) for span in mentions]

    def get_candidates(self, mention: Union[Span, str]) -> Iterable[Candidate]:
        """
        Return candidate entities for specified text. Each candidate defines the entity, the original alias,
        and the prior probability of that alias resolving to that entity.
        If the no candidate is found for a given text, an empty list is returned.
        mention (Union[Span, str]): Mention for which to get candidates.
        RETURNS (Iterable[Candidate]): Identified candidates.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="InMemoryLookupKB", method="get_candidates", name=self.__name__)
        )

    def get_vectors(self, entities: Iterable[str]) -> Iterable[Iterable[float]]:
        """
        Return vectors for entities.
        entity (str): Entity name/ID.
        RETURNS (Iterable[Iterable[float]]): Vectors for specified entities.
        """
        return [self.get_vector(entity) for entity in entities]

    def get_vector(self, str entity) -> Iterable[float]:
        """
        Return vector for entity.
        entity (str): Entity name/ID.
        RETURNS (Iterable[float]): Vector for specified entity.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="InMemoryLookupKB", method="get_vector", name=self.__name__)
        )

    def to_bytes(self, **kwargs) -> bytes:
        """Serialize the current state to a binary string.
        RETURNS (bytes): Current state as binary string.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="InMemoryLookupKB", method="to_bytes", name=self.__name__)
        )

    def from_bytes(self, bytes_data: bytes, *, exclude: Tuple[str] = tuple()):
        """Load state from a binary string.
        bytes_data (bytes): KB state.
        exclude (Tuple[str]): Properties to exclude when restoring KB.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="InMemoryLookupKB", method="from_bytes", name=self.__name__)
        )

    def to_disk(self, path: Union[str, Path], exclude: Iterable[str] = SimpleFrozenList()) -> None:
        """
        Write InMemoryLookupKB content to disk.
        path (Union[str, Path]): Target file path.
        exclude (Iterable[str]): List of components to exclude.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="InMemoryLookupKB", method="to_disk", name=self.__name__)
        )

    def from_disk(self, path: Union[str, Path], exclude: Iterable[str] = SimpleFrozenList()) -> None:
        """
        Load InMemoryLookupKB content from disk.
        path (Union[str, Path]): Target file path.
        exclude (Iterable[str]): List of components to exclude.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="InMemoryLookupKB", method="from_disk", name=self.__name__)
        )
