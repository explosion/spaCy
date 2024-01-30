# cython: infer_types=True

from .kb_in_memory cimport InMemoryLookupKB

from ..errors import Errors


cdef class Candidate:
    """A `Candidate` object refers to a textual mention that may or may not be resolved
    to a specific entity from a Knowledge Base. This will be used as input for the entity linking
    algorithm which will disambiguate the various candidates to the correct one.
    Each candidate, which represents a possible link between one textual mention and one entity in the knowledge base,
    is assigned a certain prior probability.

    DOCS: https://spacy.io/api/kb/#candidate-init
    """

    def __init__(self):
        # Make sure abstract Candidate is not instantiated.
        if self.__class__ == Candidate:
            raise TypeError(
                Errors.E1046.format(cls_name=self.__class__.__name__)
            )

    @property
    def entity_id(self) -> int:
        """RETURNS (int): Numerical representation of entity ID (if entity ID is numerical, this is just the entity ID,
        otherwise the hash of the entity ID string)."""
        raise NotImplementedError

    @property
    def entity_id_(self) -> str:
        """RETURNS (str): String representation of entity ID."""
        raise NotImplementedError

    @property
    def entity_vector(self) -> vector[float]:
        """RETURNS (vector[float]): Entity vector."""
        raise NotImplementedError


cdef class InMemoryCandidate(Candidate):
    """Candidate for InMemoryLookupKB."""

    def __init__(
        self,
        kb: InMemoryLookupKB,
        entity_hash: int,
        alias_hash: int,
        entity_vector: vector[float],
        prior_prob: float,
        entity_freq: float
    ):
        """
        kb (InMemoryLookupKB]): InMemoryLookupKB instance.
        entity_id (int): Entity ID as hash that can be looked up with InMemoryKB.vocab.strings.__getitem__().
        entity_freq (int): Entity frequency in KB corpus.
        entity_vector (List[float]): Entity embedding.
        alias_hash (int): Alias hash.
        prior_prob (float): Prior probability of entity for this alias. I. e. the probability that, independent of
            the context, this alias - which matches one of this entity's aliases - resolves to one this entity.
        """
        super().__init__()

        self._entity_hash = entity_hash
        self._entity_vector = entity_vector
        self._prior_prob = prior_prob
        self._kb = kb
        self._alias_hash = alias_hash
        self._entity_freq = entity_freq

    @property
    def entity_id(self) -> int:
        return self._entity_hash

    @property
    def entity_vector(self) -> vector[float]:
        return self._entity_vector

    @property
    def prior_prob(self) -> float:
        """RETURNS (float): Prior probability that this alias, which matches one of this entity's synonyms, resolves to
        this entity."""
        return self._prior_prob

    @property
    def alias(self) -> str:
        """RETURNS (str): Alias."""
        return self._kb.vocab.strings[self._alias_hash]

    @property
    def entity_id_(self) -> str:
        return self._kb.vocab.strings[self._entity_hash]

    @property
    def entity_freq(self) -> float:
        """RETURNS (float): Entity frequency in KB corpus."""
        return self._entity_freq
