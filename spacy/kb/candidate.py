import abc
from typing import List, Union, Callable

from ..errors import Errors


class Candidate(abc.ABC):
    """A `Candidate` object refers to a textual mention that may or may not be resolved
    to a specific `entity_id` from a Knowledge Base. This will be used as input for the entity_id linking
    algorithm which will disambiguate the various candidates to the correct one.
    Each candidate (mention, entity_id) pair is assigned a certain prior probability.

    DOCS: https://spacy.io/api/kb/#candidate-init
    """

    def __init__(
        self,
        mention: str,
        entity_id: Union[str, int],
        entity_vector: List[float],
        prior_prob: float,
    ):
        """Initializes properties of `Candidate` instance.
        mention (str): Mention text for this candidate.
        entity_id (Union[str, int]): Unique entity ID.
        entity_vector (List[float]): Entity embedding.
        prior_prob (float): Prior probability of entity for this mention - i.e. the probability that, independent of
            the context, this mention resolves to this entity_id in the corpus used to build the knowledge base. In
            cases in which this isn't always possible (e.g.: the corpus to analyse contains mentions that the KB corpus
            doesn't) it might be better to eschew this information and always supply the same value.
        """
        self._mention = mention
        self._entity_id = entity_id
        # Note that hashing an int value yields the same int value.
        self._entity_id_hash = hash(entity_id)
        self._entity_vector = entity_vector
        self._prior_prob = prior_prob

    @property
    def entity_id(self) -> Union[str, int]:
        """RETURNS (Union[str, int]): Unique entity ID."""
        return self._entity_id

    @property
    def entity_id_int(self) -> int:
        """RETURNS (int): Numerical representation of entity ID (if entity ID is numerical, this is just the entity ID,
        otherwise the hash of the entity ID string)."""
        return self._entity_id_hash

    @property
    def entity_id_str(self) -> str:
        """RETURNS (str): String representation of entity ID."""
        return str(self._entity_id)

    @property
    def mention(self) -> str:
        """RETURNS (str): Mention."""
        return self._mention

    @property
    def entity_vector(self) -> List[float]:
        """RETURNS (List[float]): Entity vector."""
        return self._entity_vector

    @property
    def prior_prob(self) -> float:
        """RETURNS (List[float]): Entity vector."""
        return self._prior_prob


class InMemoryCandidate(Candidate):
    """Candidate for InMemoryLookupKB."""

    def __init__(
        self,
        hash_to_str: Callable[[int], str],
        entity_id: int,
        mention: str,
        entity_vector: List[float],
        prior_prob: float,
        entity_freq: int,
    ):
        """
        hash_to_str (Callable[[int], str]): Callable retrieving entity name from provided entity/vocab hash.
        entity_id (int): Entity ID as hash that can be looked up with InMemoryKB.vocab.strings.__getitem__().
        entity_freq (int): Entity frequency in KB corpus.
        entity_vector (List[float]): Entity embedding.
        mention (str): Mention.
        prior_prob (float): Prior probability of entity for this mention - i.e. the probability that, independent of
            the context, this mention resolves to this entity_id in the corpus used to build the knowledge base. In
            cases in which this isn't always possible (e.g.: the corpus to analyse contains mentions that the KB corpus
            doesn't) it might be better to eschew this information and always supply the same value.
        """
        super().__init__(
            mention=mention,
            entity_id=entity_id,
            entity_vector=entity_vector,
            prior_prob=prior_prob,
        )
        self._hash_to_str = hash_to_str
        self._entity_freq = entity_freq
        if not isinstance(self._entity_id, int):
            raise ValueError(
                Errors.E4005.format(should_type="int", is_type=str(type(entity_id)))
            )
        self._entity_id_str = self._hash_to_str(self._entity_id)

    @property
    def entity_freq(self) -> float:
        """RETURNS (float): Relative entity frequency."""
        return self._entity_freq

    @property
    def entity_id_str(self) -> str:
        """RETURNS (str): String representation of entity ID."""
        return self._entity_id_str
