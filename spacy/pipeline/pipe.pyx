# cython: infer_types=True, profile=True
import warnings
from typing import Optional, Tuple, Iterable, Iterator, Callable, Union, Dict
import srsly

from ..tokens.doc cimport Doc

from ..training import Example
from ..errors import Errors, Warnings
from ..language import Language

cdef class Pipe:
    """This class is a base class and not instantiated directly. It provides
    an interface for pipeline components to implement.
    Trainable pipeline components like the EntityRecognizer or TextCategorizer
    should inherit from the subclass 'TrainablePipe'.

    DOCS: https://nightly.spacy.io/api/pipe
    """

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Raise a warning if an inheriting class implements 'begin_training'
         (from v2) instead of the new 'initialize' method (from v3)"""
        if hasattr(cls, "begin_training"):
            warnings.warn(Warnings.W088.format(name=cls.__name__))

    def __call__(self, Doc doc) -> Doc:
        """Apply the pipe to one document. The document is modified in place,
        and returned. This usually happens under the hood when the nlp object
        is called on a text and all components are applied to the Doc.

        docs (Doc): The Doc to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://nightly.spacy.io/api/pipe#call
        """
        raise NotImplementedError(Errors.E931.format(parent="Pipe", method="__call__", name=self.name))

    def pipe(self, stream: Iterable[Doc], *, batch_size: int=128) -> Iterator[Doc]:
        """Apply the pipe to a stream of documents. This usually happens under
        the hood when the nlp object is called on a text and all components are
        applied to the Doc.

        stream (Iterable[Doc]): A stream of documents.
        batch_size (int): The number of documents to buffer.
        YIELDS (Doc): Processed documents in order.

        DOCS: https://nightly.spacy.io/api/pipe#pipe
        """
        for doc in stream:
            doc = self(doc)
            yield doc

    def initialize(self, get_examples: Callable[[], Iterable[Example]], *, nlp: Language=None):
        """Initialize the pipe. For non-trainable components, this method
        is optional. For trainable components, which should inherit
        from the subclass TrainablePipe, the provided data examples
        should be used to ensure that the internal model is initialized
        properly and all input/output dimensions throughout the network are
        inferred.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.

        DOCS: https://nightly.spacy.io/api/pipe#initialize
        """
        pass

    def score(self, examples: Iterable[Example], **kwargs) -> Dict[str, Union[float, Dict[str, float]]]:
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores.

        DOCS: https://nightly.spacy.io/api/pipe#score
        """
        return {}

    @property
    def is_trainable(self) -> bool:
        return False

    @property
    def labels(self) -> Optional[Tuple[str]]:
        return tuple()

    @property
    def label_data(self):
        """Optional JSON-serializable data that would be sufficient to recreate
        the label set if provided to the `pipe.initialize()` method.
        """
        return None

    def _require_labels(self) -> None:
        """Raise an error if this component has no labels defined."""
        if not self.labels or list(self.labels) == [""]:
            raise ValueError(Errors.E143.format(name=self.name))

def deserialize_config(path):
    if path.exists():
        return srsly.read_json(path)
    else:
        return {}
