import abc
from typing import List, Union, Optional

from spacy import Errors
from ..tokens import Span


class Candidate(abc.ABC):
    """A `Candidate` object refers to a textual mention (`alias`) that may or may not be resolved
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
        entity_id (Union[int, str]): Unique ID of entity_id.
        """
        self.mention = mention
        self.entity = entity_id
        self.entity_vector = entity_vector

    @property
    def entity_id(self) -> Union[int, str]:
        """RETURNS (Union[int, str]): Entity ID."""
        return self.entity

    def entity_(self) -> Union[int, str]:
        """RETURNS (Union[int, str]): Entity ID (for backwards compatibility)."""
        return self.entity

    @property
    def mention(self) -> str:
        """RETURNS (str): Mention."""
        return self.mention

    @property
    def entity_vector(self) -> List[float]:
        """RETURNS (List[float]): Entity vector."""
        return self.entity_vector


class InMemoryLookupKBCandidate(Candidate):
    """`Candidate` for InMemoryLookupKBCandidate."""

    # todo how to resolve circular import issue? -> replace with callable for hash?
    def __init__(
        self,
        kb: KnowledgeBase,
        entity_hash,
        entity_freq,
        entity_vector,
        alias_hash,
        prior_prob,
    ):
        """
        prior_prob (float): Prior probability of entity_id for this mention - i.e. the probability that, independent of the
            context, this mention resolves to this entity_id in the corpus used to build the knowledge base. In cases in
            which this isn't always possible (e.g.: the corpus to analyse contains mentions that the KB corpus doesn't)
            it might be better to eschew this information and always supply the same value.
        """
        self.kb = kb
        self.entity_hash = entity_hash
        self.entity_freq = entity_freq
        self.entity_vector = entity_vector
        self.alias_hash = alias_hash
        self.prior_prob = prior_prob

    @property
    def entity(self) -> int:
        """RETURNS (uint64): hash of the entity_id's KB ID/name"""
        return self.entity_hash

    @property
    def entity_(self) -> str:
        """RETURNS (str): ID/name of this entity_id in the KB"""
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
        """RETURNS (List[float]): Entity vector."""
        return self.prior_prob


def get_candidates(kb: KnowledgeBase, mention: Span) -> Iterable[Candidate]:
    """
    Return candidate entities for a given mention and fetching appropriate entries from the index.
    kb (KnowledgeBase): Knowledge base to query.
    mention (Span): Entity mention for which to identify candidates.
    RETURNS (Iterable[Candidate]): Identified candidates.
    """
    return kb.get_candidates(mention)


def get_candidates_all(
    kb: KnowledgeBase, mentions: Generator[Iterable[Span], None, None]
) -> Iterator[Iterable[Iterable[Candidate]]]:
    """
    Return candidate entities for the given mentions and fetching appropriate entries from the index.
    kb (KnowledgeBase): Knowledge base to query.
    mention (Generator[Iterable[Span]]): Entity mentions per document for which to identify candidates.
    RETURNS (Generator[Iterable[Iterable[Candidate]]]): Identified candidates per document.
    """
    return kb.get_candidates_all(mentions)
