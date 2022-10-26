# cython: infer_types=True, profile=True

from pathlib import Path
from typing import Iterable, Tuple, Union
from cymem.cymem cimport Pool

from .candidate import Candidate
from ..tokens import Span
from ..util import SimpleFrozenList
from ..errors import Errors


cdef class KnowledgeBase:
    """A `KnowledgeBase` instance stores unique identifiers for entities and their textual aliases,
    to support entity linking of named entities to real-world concepts.
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

    def get_candidates_batch(self, mentions: Iterable[Span]) -> Iterable[Iterable[Candidate]]:
        """
        Return candidate entities for specified texts. Each candidate defines the entity, the original alias,
        and the prior probability of that alias resolving to that entity.
        If no candidate is found for a given text, an empty list is returned.
        mentions (Iterable[Span]): Mentions for which to get candidates.
        RETURNS (Iterable[Iterable[Candidate]]): Identified candidates.
        """
        return [self.get_candidates(span) for span in mentions]

    def get_candidates(self, mention: Span) -> Iterable[Candidate]:
        """
        Return candidate entities for specified text. Each candidate defines the entity, the original alias,
        and the prior probability of that alias resolving to that entity.
        If the no candidate is found for a given text, an empty list is returned.
        mention (Span): Mention for which to get candidates.
        RETURNS (Iterable[Candidate]): Identified candidates.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="KnowledgeBase", method="get_candidates", name=self.__name__)
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
            Errors.E1045.format(parent="KnowledgeBase", method="get_vector", name=self.__name__)
        )

    def to_bytes(self, **kwargs) -> bytes:
        """Serialize the current state to a binary string.
        RETURNS (bytes): Current state as binary string.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="KnowledgeBase", method="to_bytes", name=self.__name__)
        )

    def from_bytes(self, bytes_data: bytes, *, exclude: Tuple[str] = tuple()):
        """Load state from a binary string.
        bytes_data (bytes): KB state.
        exclude (Tuple[str]): Properties to exclude when restoring KB.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="KnowledgeBase", method="from_bytes", name=self.__name__)
        )

    def to_disk(self, path: Union[str, Path], exclude: Iterable[str] = SimpleFrozenList()) -> None:
        """
        Write KnowledgeBase content to disk.
        path (Union[str, Path]): Target file path.
        exclude (Iterable[str]): List of components to exclude.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="KnowledgeBase", method="to_disk", name=self.__name__)
        )

    def from_disk(self, path: Union[str, Path], exclude: Iterable[str] = SimpleFrozenList()) -> None:
        """
        Load KnowledgeBase content from disk.
        path (Union[str, Path]): Target file path.
        exclude (Iterable[str]): List of components to exclude.
        """
        raise NotImplementedError(
            Errors.E1045.format(parent="KnowledgeBase", method="from_disk", name=self.__name__)
        )
