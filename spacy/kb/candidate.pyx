# cython: infer_types=True, profile=True

from .kb_in_memory cimport InMemoryLookupKB
from ..errors import Errors

cdef class Candidate:
    """A `Candidate` object refers to a textual mention that may or may not be resolved
    to a specific entity from a Knowledge Base. This will be used as input for the entity linking
    algorithm which will disambiguate the various candidates to the correct one.
    Each candidate (mention, entity_id) pair is assigned a certain prior probability.

    DOCS: https://spacy.io/api/kb/#candidate-init
    """

    def __init__(
        self,
        entity_id: str,
        entity_vector: vector[float],
        prior_prob: float,
    ):
        """Initializes properties of abstract base class `Candidate`.
        entity_id (Union[str, int]): Unique entity ID.
        entity_vector (List[float]): Entity embedding.
        prior_prob (float): Prior probability of entity for this mention - i.e. the probability that, independent of
            the context, this mention resolves to this entity_id in the corpus used to build the knowledge base. In
            cases in which this isn't always possible (e.g.: the corpus to analyse contains mentions that the KB corpus
            doesn't) it might be better to eschew this information and always supply the same value.
        """
        # Make sure abstract KB is not instantiated.
        if self.__class__ == Candidate:
            raise TypeError(
                Errors.E1046.format(cls_name=self.__class__.__name__)
            )

        self._entity_id_ = entity_id
        # Note that hashing an int value yields the same int value.
        self._entity_id = hash(entity_id)
        self._entity_vector = entity_vector
        self._prior_prob = prior_prob

    @property
    def entity_id(self) -> int:
        """RETURNS (int): Numerical representation of entity ID (if entity ID is numerical, this is just the entity ID,
        otherwise the hash of the entity ID string)."""
        return self._entity_id

    @property
    def entity_id_(self) -> str:
        """RETURNS (str): String representation of entity ID."""
        return self._entity_id_

    @property
    def mention(self) -> str:
        """RETURNS (str): Mention."""
        raise NotImplementedError

    @property
    def entity_vector(self) -> vector[float]:
        """RETURNS (vector[float]): Entity vector."""
        return self._entity_vector

    @property
    def prior_prob(self) -> float:
        """RETURNS (List[float]): Entity vector."""
        return self._prior_prob


cdef class InMemoryCandidate(Candidate):
    """Candidate for InMemoryLookupKB."""

    def __init__(
        self,
        kb: InMemoryLookupKB,
        entity_hash: int,
        mention_hash: int,
        entity_vector: vector[float],
        prior_prob: float,
        entity_freq: float
    ):
        """
        kb (InMemoryLookupKB]): InMemoryLookupKB instance.
        entity_id (int): Entity ID as hash that can be looked up with InMemoryKB.vocab.strings.__getitem__().
        entity_freq (int): Entity frequency in KB corpus.
        entity_vector (List[float]): Entity embedding.
        mention_hash (int): Mention hash.
        prior_prob (float): Prior probability of entity for this mention - i.e. the probability that, independent of
            the context, this mention resolves to this entity in the corpus used to build the knowledge base. In
            cases in which this isn't always possible (e.g.: the corpus to analyse contains mentions that the KB corpus
            doesn't) it might be better to eschew this information and always supply the same value.
        """
        super().__init__(
            entity_id=kb.vocab.strings[entity_hash],
            entity_vector=entity_vector,
            prior_prob=prior_prob,
        )
        self._kb = kb
        self._mention = mention_hash
        self._entity_id = entity_hash
        self._entity_freq = entity_freq

    @property
    def mention(self) -> str:
        """RETURNS (str): Mention."""
        return self._kb.vocab.strings[self._mention]

    @property
    def entity_id_(self) -> str:
        """RETURNS (str): ID/name of this entity in the KB."""
        return self._kb.vocab.strings[self._entity_id]

    @property
    def entity_freq(self) -> float:
        """RETURNS (float): Entity frequence of this candidate's entity in the KB."""
        return self._entity_freq
