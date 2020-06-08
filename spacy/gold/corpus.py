import random
import shutil
import tempfile
import srsly
from pathlib import Path
import itertools
from ..tokens import Doc
from .. import util
from ..errors import Errors, AlignmentError
from .gold_io import read_json_file, json_to_examples
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
            train = self.read_examples(self.walk_corpus(train))
            dev = self.read_examples(self.walk_corpus(dev))
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
    def read_examples(locs, limit=0):
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
                            examples.extend(json_to_examples(json_doc))
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
                            examples.append(Example.from_dict(ex_dict, doc=doc))

            elif file_name.endswith("msg"):
                text, ex_dict = srsly.read_msgpack(loc)
                examples = [Example.from_dict(ex_dict, doc=text)]
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
    def dev_examples(self):
        locs = (self.tmp_dir / "dev").iterdir()
        yield from self.read_examples(locs, limit=self.limit)

    @property
    def train_examples(self):
        locs = (self.tmp_dir / "train").iterdir()
        yield from self.read_examples(locs, limit=self.limit)

    def count_train(self):
        """Returns count of words in train examples"""
        n = 0
        i = 0
        for example in self.train_examples:
            n += len(example.token_annotation.words)
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
        train_examples = self.read_examples(locs, limit=self.limit)
        gold_examples = self.iter_gold_docs(
            nlp,
            train_examples,
            gold_preproc,
            max_length=max_length,
            noise_level=noise_level,
            orth_variant_level=orth_variant_level,
            make_projective=True,
            ignore_misaligned=ignore_misaligned,
        )
        yield from gold_examples

    def train_dataset_without_preprocessing(
        self, nlp, gold_preproc=False, ignore_misaligned=False
    ):
        examples = self.iter_gold_docs(
            nlp,
            self.train_examples,
            gold_preproc=gold_preproc,
            ignore_misaligned=ignore_misaligned,
        )
        yield from examples

    def dev_dataset(self, nlp, gold_preproc=False, ignore_misaligned=False):
        examples = self.iter_gold_docs(
            nlp,
            self.dev_examples,
            gold_preproc=gold_preproc,
            ignore_misaligned=ignore_misaligned,
        )
        yield from examples

    @classmethod
    def iter_gold_docs(
        cls,
        nlp,
        examples,
        gold_preproc,
        max_length=None,
        noise_level=0.0,
        orth_variant_level=0.0,
        make_projective=False,
        ignore_misaligned=False,
    ):
        """ Setting gold_preproc will result in creating a doc per sentence """
        for example in examples:
            example_docs = []
            if gold_preproc:
                split_examples = example.split_sents()
                for split_example in split_examples:
                    split_example_docs = cls._make_docs(
                        nlp,
                        split_example,
                        gold_preproc,
                        noise_level=noise_level,
                        orth_variant_level=orth_variant_level,
                    )
                    example_docs.extend(split_example_docs)
            else:
                example_docs = cls._make_docs(
                    nlp,
                    example,
                    gold_preproc,
                    noise_level=noise_level,
                    orth_variant_level=orth_variant_level,
                )
            for ex in example_docs:
                if (not max_length) or len(ex.doc) < max_length:
                    if ignore_misaligned:
                        try:
                            _ = ex._deprecated_get_gold()
                        except AlignmentError:
                            continue
                    yield ex

    @classmethod
    def _make_docs(
        cls, nlp, example, gold_preproc, noise_level=0.0, orth_variant_level=0.0
    ):
        var_example = make_orth_variants(
            nlp, example, orth_variant_level=orth_variant_level
        )
        # gold_preproc is not used ?!
        if example.text is not None:
            var_text = add_noise(var_example.text, noise_level)
            var_doc = nlp.make_doc(var_text)
            var_example.doc = var_doc
        else:
            var_doc = Doc(
                nlp.vocab,
                words=add_noise(var_example.token_annotation.words, noise_level),
            )
            var_example.doc = var_doc
        return [var_example]
