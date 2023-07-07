# cython: infer_types=True, profile=True

from typing import Iterable

from .kb cimport KnowledgeBase

from ..tokens import Span


cdef class Candidate:
    """A `Candidate` object refers to a textual mention (`alias`) that may or may not be resolved
    to a specific `entity` from a Knowledge Base. This will be used as input for the entity linking
    algorithm which will disambiguate the various candidates to the correct one.
    Each candidate (alias, entity) pair is assigned a certain prior probability.

    DOCS: https://spacy.io/api/kb/#candidate-init
    """

    def __init__(self, KnowledgeBase kb, entity_hash, entity_freq, entity_vector, alias_hash, prior_prob):
        self.kb = kb
        self.entity_hash = entity_hash
        self.entity_freq = entity_freq
        self.entity_vector = entity_vector
        self.alias_hash = alias_hash
        self.prior_prob = prior_prob

    @property
    def entity(self) -> int:
        """RETURNS (uint64): hash of the entity's KB ID/name"""
        return self.entity_hash

    @property
    def entity_(self) -> str:
        """RETURNS (str): ID/name of this entity in the KB"""
        return self.kb.vocab.strings[self.entity_hash]

    @property
    def alias(self) -> int:
        """RETURNS (uint64): hash of the alias"""
        return self.alias_hash

    @property
    def alias_(self) -> str:
        """RETURNS (str): ID of the original alias"""
        return self.kb.vocab.strings[self.alias_hash]

    @property
    def entity_freq(self) -> float:
        return self.entity_freq

    @property
    def entity_vector(self) -> Iterable[float]:
        return self.entity_vector

    @property
    def prior_prob(self) -> float:
        return self.prior_prob


def get_candidates(kb: KnowledgeBase, mention: Span) -> Iterable[Candidate]:
    """
    Return candidate entities for a given mention and fetching appropriate entries from the index.
    kb (KnowledgeBase): Knowledge base to query.
    mention (Span): Entity mention for which to identify candidates.
    RETURNS (Iterable[Candidate]): Identified candidates.
    """
    return kb.get_candidates(mention)


def get_candidates_batch(kb: KnowledgeBase, mentions: Iterable[Span]) -> Iterable[Iterable[Candidate]]:
    """
    Return candidate entities for the given mentions and fetching appropriate entries from the index.
    kb (KnowledgeBase): Knowledge base to query.
    mention (Iterable[Span]): Entity mentions for which to identify candidates.
    RETURNS (Iterable[Iterable[Candidate]]): Identified candidates.
    """
    return kb.get_candidates_batch(mentions)
