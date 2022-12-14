# cython: infer_types=True, profile=True

from pathlib import Path
from typing import Iterable, Tuple, Union, Iterator, TypeVar, Type, Optional
from cymem.cymem cimport Pool

from .candidate import Candidate
from ..tokens import Span, Doc
from ..util import SimpleFrozenList
from ..errors import Errors


cdef class KnowledgeBase:
    """A `KnowledgeBase` instance stores unique identifiers for entities and their textual aliases,
    to support entity linking of named entities to real-world concepts.
    This is an abstract class and requires its operations to be implemented.

    DOCS: https://spacy.io/api/kb
    """

    _KBType = TypeVar("_KBType", bound=KnowledgeBase)

    def __init__(self, vocab: Vocab, entity_vector_length: int):
        """Create a KnowledgeBase."""
        # Make sure abstract KB is not instantiated.
        if self.__class__ == KnowledgeBase:
            raise TypeError(
                Errors.E1045.format(cls_name=self.__class__.__name__)
            )

        self.vocab = vocab
        self.entity_vector_length = entity_vector_length
        self.mem = Pool()

    def get_candidates_all(self, docs: Iterator[Doc]) -> Iterator[Iterable[Iterable[Candidate]]]:
        """
        Return candidate entities for mentions stored in `ent` attribute in passed docs. Each candidate defines the
        entity, the original alias, and the prior probability of that alias resolving to that entity.
        If no candidate is found for a given mention, an empty list is returned.
        docs (Iterator[Doc]): Doc instances with mentions (stored in `.ent`).
        RETURNS (Iterator[Iterable[Iterable[Candidate]]]): Identified candidates per document.
        """
        for doc in docs:
            yield [self.get_candidates(ent_span, doc) for ent_span in doc.ents]

    def get_candidates(self, mention: Span, doc: Optional[Doc] = None) -> Iterable[Candidate]:
        """
        Return candidate entities for specified text. Each candidate defines the entity, the original alias,
        and the prior probability of that alias resolving to that entity.
        If the no candidate is found for a given text, an empty list is returned.
        Note that doc is not utilized for further context in this implementation.
        mention (Span): Mention for which to get candidates.
        doc (Optional[Doc]): Doc to use for context.
        RETURNS (Iterable[Candidate]): Identified candidates.
        """
        raise NotImplementedError(
            Errors.E1044.format(parent="KnowledgeBase", method="get_candidates", name=self.__name__)
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
            Errors.E1044.format(parent="KnowledgeBase", method="get_vector", name=self.__name__)
        )

    def to_bytes(self, **kwargs) -> bytes:
        """Serialize the current state to a binary string.
        RETURNS (bytes): Current state as binary string.
        """
        raise NotImplementedError(
            Errors.E1044.format(parent="KnowledgeBase", method="to_bytes", name=self.__name__)
        )

    def from_bytes(self, bytes_data: bytes, *, exclude: Tuple[str] = tuple()):
        """Load state from a binary string.
        bytes_data (bytes): KB state.
        exclude (Tuple[str]): Properties to exclude when restoring KB.
        """
        raise NotImplementedError(
            Errors.E1044.format(parent="KnowledgeBase", method="from_bytes", name=self.__name__)
        )

    def to_disk(self, path: Union[str, Path], exclude: Iterable[str] = SimpleFrozenList()) -> None:
        """Write KnowledgeBase content to disk.
        path (Union[str, Path]): Target file path.
        exclude (Iterable[str]): List of components to exclude.
        """
        raise NotImplementedError(
            Errors.E1044.format(parent="KnowledgeBase", method="to_disk", name=self.__name__)
        )

    def from_disk(self, path: Union[str, Path], exclude: Iterable[str] = SimpleFrozenList()) -> None:
        """Load KnowledgeBase content from disk.
        path (Union[str, Path]): Target file path.
        exclude (Iterable[str]): List of components to exclude.
        """
        raise NotImplementedError(
            Errors.E1044.format(parent="KnowledgeBase", method="from_disk", name=self.__name__)
        )

    @classmethod
    def generate_from_disk(
        cls: Type[_KBType], path: Union[str, Path], exclude: Iterable[str] = SimpleFrozenList()
    ) -> _KBType:
        """
        Factory method for generating KnowledgeBase subclass instance from file.
        path (Union[str, Path]): Target file path.
        exclude (Iterable[str]): List of components to exclude.
        return (_KBType): Instance of KnowledgeBase subclass generated from file.
        """
        raise NotImplementedError(
            Errors.E1044.format(parent="KnowledgeBase", method="generate_from_disk", name=cls.__name__)
        )

    def __len__(self) -> int:
        """Returns number of entities in the KnowledgeBase.
        RETURNS (int): Number of entities in the KnowledgeBase.
        """
        raise NotImplementedError(
            Errors.E1044.format(parent="KnowledgeBase", method="__len__", name=self.__name__)
        )
