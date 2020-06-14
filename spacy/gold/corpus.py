import random
import shutil
import tempfile
import srsly
from pathlib import Path
import itertools
from ..tokens import Doc
from .. import util
from ..errors import Errors, AlignmentError
from .gold_io import read_json_file, json_to_annotations
from .augment import make_orth_variants, add_noise
from .example import Example


class GoldCorpus(object):
    """An annotated corpus, using the JSON file format. Manages
    annotations for tagging, dependency parsing and NER.

    DOCS: https://spacy.io/api/goldcorpus
    """

    def __init__(self, train, dev, gold_preproc=False, limit=None):
        """Create a GoldCorpus.

        train (str / Path): File or directory of training data.
        dev (str / Path): File or directory of development data.
        RETURNS (GoldCorpus): The newly created object.
        """
        self.limit = limit
        if isinstance(train, str) or isinstance(train, Path):
            train = self.read_annotations(self.walk_corpus(train))
            dev = self.read_annotations(self.walk_corpus(dev))
        # Write temp directory with one doc per file, so we can shuffle and stream
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.write_msgpack(self.tmp_dir / "train", train, limit=self.limit)
        self.write_msgpack(self.tmp_dir / "dev", dev, limit=self.limit)

    def __del__(self):
        shutil.rmtree(self.tmp_dir)

    @staticmethod
    def write_msgpack(directory, examples, limit=0):
        if not directory.exists():
            directory.mkdir()
        n = 0
        for i, ex_dict in enumerate(examples):
            text = ex_dict["text"]
            srsly.write_msgpack(directory / f"{i}.msg", (text, ex_dict))
            n += 1
            if limit and n >= limit:
                break

    @staticmethod
    def walk_corpus(path):
        path = util.ensure_path(path)
        if not path.is_dir():
            return [path]
        paths = [path]
        locs = []
        seen = set()
        for path in paths:
            if str(path) in seen:
                continue
            seen.add(str(path))
            if path.parts[-1].startswith("."):
                continue
            elif path.is_dir():
                paths.extend(path.iterdir())
            elif path.parts[-1].endswith((".json", ".jsonl")):
                locs.append(path)
        return locs

    @staticmethod
    def read_annotations(locs, limit=0):
        """ Yield training examples """
        i = 0
        for loc in locs:
            loc = util.ensure_path(loc)
            file_name = loc.parts[-1]
            if file_name.endswith("json"):
                examples = read_json_file(loc)
            elif file_name.endswith("jsonl"):
                gold_tuples = srsly.read_jsonl(loc)
                first_gold_tuple = next(gold_tuples)
                gold_tuples = itertools.chain([first_gold_tuple], gold_tuples)
                # TODO: proper format checks with schemas
                if isinstance(first_gold_tuple, dict):
                    if first_gold_tuple.get("paragraphs", None):
                        examples = []
                        for json_doc in gold_tuples:
                            examples.extend(json_to_annotations(json_doc))
                    elif first_gold_tuple.get("doc_annotation", None):
                        examples = []
                        for ex_dict in gold_tuples:
                            doc = ex_dict.get("doc", None)
                            if doc is None:
                                doc = ex_dict.get("text", None)
                            if not (
                                doc is None
                                or isinstance(doc, Doc)
                                or isinstance(doc, str)
                            ):
                                raise ValueError(Errors.E987.format(type=type(doc)))
                            examples.append(ex_dict)

            elif file_name.endswith("msg"):
                text, ex_dict = srsly.read_msgpack(loc)
                examples = [ex_dict]
            else:
                supported = ("json", "jsonl", "msg")
                raise ValueError(Errors.E124.format(path=loc, formats=supported))
            try:
                for example in examples:
                    yield example
                    i += 1
                    if limit and i >= limit:
                        return
            except KeyError as e:
                msg = "Missing key {}".format(e)
                raise KeyError(Errors.E996.format(file=file_name, msg=msg))
            except UnboundLocalError as e:
                msg = "Unexpected document structure"
                raise ValueError(Errors.E996.format(file=file_name, msg=msg))

    @property
    def dev_annotations(self):
        locs = (self.tmp_dir / "dev").iterdir()
        yield from self.read_annotations(locs, limit=self.limit)

    @property
    def train_annotations(self):
        locs = (self.tmp_dir / "train").iterdir()
        yield from self.read_annotations(locs, limit=self.limit)

    def count_train(self):
        """Returns count of words in train examples"""
        n = 0
        i = 0
        for eg_dict in self.train_annotations:
            n += len(eg_dict["token_annotation"]["words"])
            if self.limit and i >= self.limit:
                break
            i += 1
        return n

    def train_dataset(
        self,
        nlp,
        gold_preproc=False,
        max_length=None,
        noise_level=0.0,
        orth_variant_level=0.0,
        ignore_misaligned=False,
    ):
        locs = list((self.tmp_dir / "train").iterdir())
        random.shuffle(locs)
        train_annotations = self.read_annotations(locs, limit=self.limit)
        examples = self.iter_examples(
            nlp,
            train_annotations,
            gold_preproc,
            max_length=max_length,
            noise_level=noise_level,
            orth_variant_level=orth_variant_level,
            make_projective=True,
            ignore_misaligned=ignore_misaligned,
        )
        yield from examples

    def train_dataset_without_preprocessing(
        self, nlp, gold_preproc=False, ignore_misaligned=False
    ):
        examples = self.iter_examples(
            nlp,
            self.train_annotations,
            gold_preproc=gold_preproc,
            ignore_misaligned=ignore_misaligned,
        )
        yield from examples

    def dev_dataset(self, nlp, gold_preproc=False, ignore_misaligned=False):
        examples = self.iter_examples(
            nlp,
            self.dev_annotations,
            gold_preproc=gold_preproc,
            ignore_misaligned=ignore_misaligned,
        )
        yield from examples

    @classmethod
    def iter_examples(
        cls,
        nlp,
        annotations,
        gold_preproc,
        max_length=None,
        noise_level=0.0,
        orth_variant_level=0.0,
        make_projective=False,
        ignore_misaligned=False,
    ):
        """ Setting gold_preproc will result in creating a doc per sentence """
        for eg_dict in annotations:
            if eg_dict["text"]:
                example = Example.from_dict(
                    nlp.make_doc(eg_dict["text"]),
                    eg_dict
                )
            else:
                example = Example.from_dict(
                    Doc(nlp.vocab, words=eg_dict["words"]),
                    eg_dict
                )
            if gold_preproc:
                # TODO: Data augmentation
                examples = example.split_sents()
            else:
                examples = [example]
            for ex in examples:
                if (not max_length) or len(ex.predicted) < max_length:
                    if ignore_misaligned:
                        try:
                            _ = ex._deprecated_get_gold()
                        except AlignmentError:
                            continue
                    yield ex
