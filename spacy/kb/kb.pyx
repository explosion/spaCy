# cython: infer_types=True

from pathlib import Path
from typing import Iterable, Tuple, Union

from cymem.cymem cimport Pool

from ..errors import Errors
from ..tokens import Span, SpanGroup
from ..util import SimpleFrozenList
from .candidate import Candidate


cdef class KnowledgeBase:
    """A `KnowledgeBase` instance stores unique identifiers for entities and
    their textual aliases, to support entity linking of named entities to
    real-world concepts.
    This is an abstract class and requires its operations to be implemented.

    DOCS: https://spacy.io/api/kb
    """

    def __init__(self, vocab: Vocab, entity_vector_length: int):
        """Create a KnowledgeBase."""
        # Make sure abstract KB is not instantiated.
        if self.__class__ == KnowledgeBase:
            raise TypeError(
                Errors.E1046.format(cls_name=self.__class__.__name__)
            )

        self.vocab = vocab
        self.entity_vector_length = entity_vector_length
        self.mem = Pool()

    def get_candidates_batch(
            self, mentions: SpanGroup
    ) -> Iterable[Iterable[Candidate]]:
        """
        Return candidate entities for a specified Span mention. Each candidate defines at least the entity and the
        entity's embedding vector. Depending on the KB implementation, further properties - such as the prior
        probability of the specified mention text resolving to that entity - might be included.
        If no candidates are found for a given mention, an empty list is returned.
        mentions (SpanGroup): Mentions for which to get candidates.
        RETURNS (Iterable[Iterable[Candidate]]): Identified candidates.
        """
        return [self.get_candidates(span) for span in mentions]

    def get_candidates(self, mention: Span) -> Iterable[Candidate]:
        """
        Return candidate entities for a specific mention. Each candidate defines at least the entity and the
        entity's embedding vector. Depending on the KB implementation, further properties - such as the prior
        probability of the specified mention text resolving to that entity - might be included.
        If no candidate is found for the given mention, an empty list is returned.
        mention (Span): Mention for which to get candidates.
        RETURNS (Iterable[Candidate]): Identified candidates.
        """
        raise NotImplementedError(
            Errors.E1045.format(
                parent="KnowledgeBase", method="get_candidates", name=self.__name__
            )
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
            Errors.E1045.format(
                parent="KnowledgeBase", method="get_vector", name=self.__name__
            )
        )

    def to_bytes(self, **kwargs) -> bytes:
        """Serialize the current state to a binary string.
        RETURNS (bytes): Current state as binary string.
        """
        raise NotImplementedError(
            Errors.E1045.format(
                parent="KnowledgeBase", method="to_bytes", name=self.__name__
            )
        )

    def from_bytes(self, bytes_data: bytes, *, exclude: Tuple[str] = tuple()):
        """Load state from a binary string.
        bytes_data (bytes): KB state.
        exclude (Tuple[str]): Properties to exclude when restoring KB.
        """
        raise NotImplementedError(
            Errors.E1045.format(
                parent="KnowledgeBase", method="from_bytes", name=self.__name__
            )
        )

    def to_disk(
            self, path: Union[str, Path], exclude: Iterable[str] = SimpleFrozenList()
    ) -> None:
        """
        Write KnowledgeBase content to disk.
        path (Union[str, Path]): Target file path.
        exclude (Iterable[str]): List of components to exclude.
        """
        raise NotImplementedError(
            Errors.E1045.format(
                parent="KnowledgeBase", method="to_disk", name=self.__name__
            )
        )

    def from_disk(
            self, path: Union[str, Path], exclude: Iterable[str] = SimpleFrozenList()
    ) -> None:
        """
        Load KnowledgeBase content from disk.
        path (Union[str, Path]): Target file path.
        exclude (Iterable[str]): List of components to exclude.
        """
        raise NotImplementedError(
            Errors.E1045.format(
                parent="KnowledgeBase", method="from_disk", name=self.__name__
            )
        )

    @property
    def supports_prior_probs(self) -> bool:
        """RETURNS (bool): Whether this KB type supports looking up prior probabilities for entity mentions."""
        raise NotImplementedError(
            Errors.E1045.format(parent="KnowledgeBase", method="supports_prior_probs", name=self.__name__)
        )
