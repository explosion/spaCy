# cython: infer_types=True, profile=True
import warnings
from typing import Optional, Tuple, Iterable, Iterator, Callable, Union, Dict
import srsly

from ..tokens.doc cimport Doc

from ..training import Example
from ..errors import Errors, Warnings
from .. import util
from ..vocab import Vocab
from ..language import Language

cdef class Pipe:
    """This class is a base class and not instantiated directly. It provides
    an interface for pipeline components to implement.
    Trainable pipeline components like the EntityRecognizer or TextCategorizer
    should inherit from the subclass 'TrainablePipe'.

    DOCS: https://nightly.spacy.io/api/pipe
    """
    def __init__(self, vocab: Vocab, name: str, **cfg):
        """Initialize a pipeline component.

        vocab (Vocab): The shared vocabulary.
        name (str): The component instance name.
        **cfg: Additonal settings and config parameters.

        DOCS: https://nightly.spacy.io/api/pipe#init
        """
        self.vocab = vocab
        self.name = name
        self.cfg = dict(cfg)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Raise a warning if an inheriting class implements 'begin_training'
         (from v2) instead of the new 'initialize' method (from v3)"""
        if hasattr(cls, "begin_training"):
            warnings.warn(Warnings.W088.format(name=cls.__name__))

    @property
    def labels(self) -> Optional[Tuple[str]]:
        return []

    @property
    def label_data(self):
        """Optional JSON-serializable data that would be sufficient to recreate
        the label set if provided to the `pipe.initialize()` method.
        """
        return None

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
        # TODO: this implemention, or language._pipe() ?
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

    def is_trainable(self) -> bool:
        return False

    def _require_labels(self) -> None:
        """Raise an error if this component has no labels defined."""
        if not self.labels or list(self.labels) == [""]:
            raise ValueError(Errors.E143.format(name=self.name))

    def _ensure_examples(self, get_examples) -> None:
        """Raise an error if the provided examples are not of the expected type."""
        if get_examples is None or not hasattr(get_examples, "__call__"):
            err = Errors.E930.format(name=self.name, obj=type(get_examples))
            raise ValueError(err)
        if not get_examples():
            err = Errors.E930.format(name=self.name, obj=get_examples())
            raise ValueError(err)

    def score(self, examples: Iterable[Example], **kwargs) -> Dict[str, Union[float, Dict[str, float]]]:
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores.

        DOCS: https://nightly.spacy.io/api/pipe#score
        """
        return {}

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the pipe to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://nightly.spacy.io/api/pipe#to_bytes
        """
        serialize = {}
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        if hasattr(self, "vocab"):
            serialize["vocab"] = self.vocab.to_bytes
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Load the pipe from a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Pipe): The loaded object.

        DOCS: https://nightly.spacy.io/api/pipe#from_bytes
        """
        deserialize = {}
        if hasattr(self, "vocab"):
            deserialize["vocab"] = lambda b: self.vocab.from_bytes(b)
        deserialize["cfg"] = lambda b: self.cfg.update(srsly.json_loads(b))
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, *, exclude=tuple()):
        """Serialize the pipe to disk.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.

        DOCS: https://nightly.spacy.io/api/pipe#to_disk
        """
        serialize = {}
        serialize["cfg"] = lambda p: srsly.write_json(p, self.cfg)
        serialize["vocab"] = lambda p: self.vocab.to_disk(p)
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, *, exclude=tuple()):
        """Load the pipe from disk.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Pipe): The loaded object.

        DOCS: https://nightly.spacy.io/api/pipe#from_disk
        """
        deserialize = {}
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p)
        deserialize["cfg"] = lambda p: self.cfg.update(deserialize_config(p))
        util.from_disk(path, deserialize, exclude)
        return self


def deserialize_config(path):
    if path.exists():
        return srsly.read_json(path)
    else:
        return {}
