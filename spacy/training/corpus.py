import warnings
from typing import Union, List, Iterable, Iterator, TYPE_CHECKING, Callable
from typing import Optional
from pathlib import Path
import random
import srsly

from .. import util
from .augment import dont_augment
from .example import Example
from ..errors import Warnings, Errors
from ..tokens import DocBin, Doc
from ..vocab import Vocab

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from ..language import Language  # noqa: F401

FILE_TYPE = ".spacy"


@util.registry.readers("spacy.Corpus.v1")
def create_docbin_reader(
    path: Optional[Path],
    gold_preproc: bool,
    max_length: int = 0,
    limit: int = 0,
    augmenter: Optional[Callable] = None,
) -> Callable[["Language"], Iterable[Example]]:
    if path is None:
        raise ValueError(Errors.E913)
    util.logger.debug(f"Loading corpus from path: {path}")
    return Corpus(
        path,
        gold_preproc=gold_preproc,
        max_length=max_length,
        limit=limit,
        augmenter=augmenter,
    )


@util.registry.readers("spacy.JsonlCorpus.v1")
def create_jsonl_reader(
    path: Optional[Path], min_length: int = 0, max_length: int = 0, limit: int = 0
) -> Callable[["Language"], Iterable[Doc]]:
    return JsonlCorpus(path, min_length=min_length, max_length=max_length, limit=limit)


@util.registry.readers("spacy.read_labels.v1")
def read_labels(path: Path, *, require: bool = False):
    # I decided not to give this a generic name, because I don't want people to
    # use it for arbitrary stuff, as I want this require arg with default False.
    if not require and not path.exists():
        return None
    return srsly.read_json(path)


def walk_corpus(path: Union[str, Path], file_type) -> List[Path]:
    path = util.ensure_path(path)
    if not path.is_dir() and path.parts[-1].endswith(file_type):
        return [path]
    orig_path = path
    paths = [path]
    locs = []
    seen = set()
    for path in paths:
        if str(path) in seen:
            continue
        seen.add(str(path))
        if path.parts and path.parts[-1].startswith("."):
            continue
        elif path.is_dir():
            paths.extend(path.iterdir())
        elif path.parts[-1].endswith(file_type):
            locs.append(path)
    if len(locs) == 0:
        warnings.warn(Warnings.W090.format(path=orig_path, format=file_type))
    # It's good to sort these, in case the ordering messes up a cache.
    locs.sort()
    return locs


class Corpus:
    """Iterate Example objects from a file or directory of DocBin (.spacy)
    formatted data files.

    path (Path): The directory or filename to read from.
    gold_preproc (bool): Whether to set up the Example object with gold-standard
        sentences and tokens for the predictions. Gold preprocessing helps
        the annotations align to the tokenization, and may result in sequences
        of more consistent length. However, it may reduce run-time accuracy due
        to train/test skew. Defaults to False.
    max_length (int): Maximum document length. Longer documents will be
        split into sentences, if sentence boundaries are available. Defaults to
        0, which indicates no limit.
    limit (int): Limit corpus to a subset of examples, e.g. for debugging.
        Defaults to 0, which indicates no limit.
    augment (Callable[Example, Iterable[Example]]): Optional data augmentation
        function, to extrapolate additional examples from your annotations.
    shuffle (bool): Whether to shuffle the examples.

    DOCS: https://spacy.io/api/corpus
    """

    def __init__(
        self,
        path: Union[str, Path],
        *,
        limit: int = 0,
        gold_preproc: bool = False,
        max_length: int = 0,
        augmenter: Optional[Callable] = None,
        shuffle: bool = False,
    ) -> None:
        self.path = util.ensure_path(path)
        self.gold_preproc = gold_preproc
        self.max_length = max_length
        self.limit = limit
        self.augmenter = augmenter if augmenter is not None else dont_augment
        self.shuffle = shuffle

    def __call__(self, nlp: "Language") -> Iterator[Example]:
        """Yield examples from the data.

        nlp (Language): The current nlp object.
        YIELDS (Example): The examples.

        DOCS: https://spacy.io/api/corpus#call
        """
        ref_docs = self.read_docbin(nlp.vocab, walk_corpus(self.path, FILE_TYPE))
        if self.shuffle:
            ref_docs = list(ref_docs)
            random.shuffle(ref_docs)

        if self.gold_preproc:
            examples = self.make_examples_gold_preproc(nlp, ref_docs)
        else:
            examples = self.make_examples(nlp, ref_docs)
        for real_eg in examples:
            for augmented_eg in self.augmenter(nlp, real_eg):
                yield augmented_eg

    def _make_example(
        self, nlp: "Language", reference: Doc, gold_preproc: bool
    ) -> Example:
        if gold_preproc or reference.has_unknown_spaces:
            return Example(
                Doc(
                    nlp.vocab,
                    words=[word.text for word in reference],
                    spaces=[bool(word.whitespace_) for word in reference],
                ),
                reference,
            )
        else:
            return Example(nlp.make_doc(reference.text), reference)

    def make_examples(
        self, nlp: "Language", reference_docs: Iterable[Doc]
    ) -> Iterator[Example]:
        for reference in reference_docs:
            if len(reference) == 0:
                continue
            elif self.max_length == 0 or len(reference) < self.max_length:
                yield self._make_example(nlp, reference, False)
            elif reference.has_annotation("SENT_START"):
                for ref_sent in reference.sents:
                    if len(ref_sent) == 0:
                        continue
                    elif self.max_length == 0 or len(ref_sent) < self.max_length:
                        yield self._make_example(nlp, ref_sent.as_doc(), False)

    def make_examples_gold_preproc(
        self, nlp: "Language", reference_docs: Iterable[Doc]
    ) -> Iterator[Example]:
        for reference in reference_docs:
            if reference.has_annotation("SENT_START"):
                ref_sents = [sent.as_doc() for sent in reference.sents]
            else:
                ref_sents = [reference]
            for ref_sent in ref_sents:
                eg = self._make_example(nlp, ref_sent, True)
                if len(eg.x):
                    yield eg

    def read_docbin(
        self, vocab: Vocab, locs: Iterable[Union[str, Path]]
    ) -> Iterator[Doc]:
        """Yield training examples as example dicts"""
        i = 0
        for loc in locs:
            loc = util.ensure_path(loc)
            if loc.parts[-1].endswith(FILE_TYPE):
                doc_bin = DocBin().from_disk(loc)
                docs = doc_bin.get_docs(vocab)
                for doc in docs:
                    if len(doc):
                        yield doc
                        i += 1
                        if self.limit >= 1 and i >= self.limit:
                            break


class JsonlCorpus:
    """Iterate Doc objects from a file or directory of jsonl
    formatted raw text files.

    path (Path): The directory or filename to read from.
    min_length (int): Minimum document length (in tokens). Shorter documents
        will be skipped. Defaults to 0, which indicates no limit.

    max_length (int): Maximum document length (in tokens). Longer documents will
        be skipped. Defaults to 0, which indicates no limit.
    limit (int): Limit corpus to a subset of examples, e.g. for debugging.
        Defaults to 0, which indicates no limit.

    DOCS: https://spacy.io/api/corpus#jsonlcorpus
    """

    file_type = "jsonl"

    def __init__(
        self,
        path: Union[str, Path],
        *,
        limit: int = 0,
        min_length: int = 0,
        max_length: int = 0,
    ) -> None:
        self.path = util.ensure_path(path)
        self.min_length = min_length
        self.max_length = max_length
        self.limit = limit

    def __call__(self, nlp: "Language") -> Iterator[Example]:
        """Yield examples from the data.

        nlp (Language): The current nlp object.
        YIELDS (Example): The example objects.

        DOCS: https://spacy.io/api/corpus#jsonlcorpus-call
        """
        for loc in walk_corpus(self.path, ".jsonl"):
            records = srsly.read_jsonl(loc)
            for record in records:
                doc = nlp.make_doc(record["text"])
                if self.min_length >= 1 and len(doc) < self.min_length:
                    continue
                elif self.max_length >= 1 and len(doc) >= self.max_length:
                    continue
                else:
                    words = [w.text for w in doc]
                    spaces = [bool(w.whitespace_) for w in doc]
                    # We don't *need* an example here, but it seems nice to
                    # make it match the Corpus signature.
                    yield Example(doc, Doc(nlp.vocab, words=words, spaces=spaces))
