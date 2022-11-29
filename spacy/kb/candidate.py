import abc
from typing import List, Union, Callable


class BaseCandidate(abc.ABC):
    """A `BaseCandidate` object refers to a textual mention (`alias`) that may or may not be resolved
    to a specific `entity_id` from a Knowledge Base. This will be used as input for the entity_id linking
    algorithm which will disambiguate the various candidates to the correct one.
    Each candidate (alias, entity_id) pair is assigned a certain prior probability.

    DOCS: https://spacy.io/api/kb/#candidate-init
    """

    def __init__(
        self, mention: str, entity_id: Union[int, str], entity_vector: List[float]
    ):
        """Create new instance of `Candidate`. Note: has to be a sub-class, otherwise error will be raised.
        mention (str): Mention text for this candidate.
        entity_id (Union[int, str]): Unique entity ID.
        entity_vector (List[float]): Entity embedding.
        """
        self._mention = mention
        self._entity_id = entity_id
        self._entity_vector = entity_vector

    @property
    def entity(self) -> Union[int, str]:
        """RETURNS (Union[int, str]): Entity ID."""
        return self._entity_id

    @property
    @abc.abstractmethod
    def entity_(self) -> str:
        """RETURNS (str): Entity name."""

    @property
    def mention(self) -> str:
        """RETURNS (str): Mention."""
        return self._mention

    @property
    def entity_vector(self) -> List[float]:
        """RETURNS (List[float]): Entity vector."""
        return self._entity_vector


class Candidate(BaseCandidate):
    """`Candidate` for InMemoryLookupKBCandidate."""

    # todo
    #  - glue together
    #  - is candidate definition necessary for EL? as long as interface fulfills requirements, this shouldn't matter.
    #    otherwise incorporate new argument.
    #  - fix test failures (100% backwards-compatible should be possible after changing EntityLinker)
    def __init__(
        self,
        retrieve_string_from_hash: Callable[[int], str],
        entity_hash: int,
        entity_freq: int,
        entity_vector: List[float],
        alias_hash: int,
        prior_prob: float,
    ):
        """
        retrieve_string_from_hash (Callable[[int], str]): Callable retrieveing entity name from provided entity/vocab
            hash.
        entity_hash (str): Hashed entity name /ID.
        entity_freq (int): Entity frequency in KB corpus.
        entity_vector (List[float]): Entity embedding.
        alias_hash (int): Hashed alias.
        prior_prob (float): Prior probability of entity for this mention - i.e. the probability that, independent of
            the context, this mention resolves to this entity_id in the corpus used to build the knowledge base. In
            cases in which this isn't always possible (e.g.: the corpus to analyse contains mentions that the KB corpus
            doesn't) it might be better to eschew this information and always supply the same value.
        """
        super().__init__(
            mention=retrieve_string_from_hash(alias_hash),
            entity_id=entity_hash,
            entity_vector=entity_vector,
        )
        self._retrieve_string_from_hash = retrieve_string_from_hash
        self._entity_hash = entity_hash
        self._entity_freq = entity_freq
        self._alias_hash = alias_hash
        self._prior_prob = prior_prob

    @property
    def entity(self) -> int:
        """RETURNS (int): hash of the entity_id's KB ID/name"""
        return self._entity_hash

    @property
    def entity_(self) -> str:
        """RETURNS (str): ID/name of this entity_id in the KB"""
        return self._retrieve_string_from_hash(self._entity_hash)

    @property
    def alias(self) -> int:
        """RETURNS (int): hash of the alias"""
        return self._alias_hash

    @property
    def alias_(self) -> str:
        """RETURNS (str): ID of the original alias"""
        return self._retrieve_string_from_hash(self._alias_hash)

    @property
    def entity_freq(self) -> float:
        return self._entity_freq

    @property
    def prior_prob(self) -> float:
        """RETURNS (List[float]): Entity vector."""
        return self._prior_prob
