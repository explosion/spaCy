import random
import shutil
import tempfile
import srsly
from pathlib import Path
import itertools
from ..tokens import Doc
from .. import util
from ..errors import Errors
from .gold_io import read_json_file
from .augment import make_orth_variants, add_noise
from .example import Example


class GoldCorpus(object):
    """An annotated corpus, using the JSON file format. Manages
    annotations for tagging, dependency parsing and NER.

    DOCS: https://spacy.io/api/goldcorpus
    """

    def __init__(self, train, dev, *, limit=None):
        """Create a GoldCorpus.

        train (str / Path): File or directory of training data.
        dev (str / Path): File or directory of development data.
        RETURNS (GoldCorpus): The newly created object.
        """
        self.limit = limit
        self.train_path = train
        self.dev_path = dev
    
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
            examples = read_json_file(loc)
            for eg_dict in read_json_file(loc):
                yield Example.from_dict(eg_dict, doc=eg_dict["text"])
                i += 1
                if limit and i >= limit:
                    return

    @property
    def dev_examples(self):
        locs = self.walk_corpus(self.dev_path)
        yield from self.read_examples(locs, limit=self.limit)

    @property
    def train_examples(self):
        locs = self.walk_corpus(self.train_path)
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
    ):
        locs = self.walk_corpus(self.train_path)
        random.shuffle(locs)
        train_examples = self.read_examples(locs, limit=self.limit)
        gold_examples = self.iter_gold_docs(
            nlp,
            train_examples,
            gold_preproc,
            max_length=max_length,
            noise_level=noise_level,
            orth_variant_level=orth_variant_level,
        )
        yield from gold_examples

    def train_dataset_without_preprocessing(
        self, nlp, gold_preproc=False
    ):
        examples = self.iter_gold_docs(
            nlp,
            self.train_examples,
            gold_preproc=gold_preproc
        )
        yield from examples

    def dev_dataset(self, nlp, gold_preproc=False):
        examples = self.iter_gold_docs(
            nlp,
            self.dev_examples,
            gold_preproc=gold_preproc,
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
        orth_variant_level=0.0
    ):
        """ Setting gold_preproc will result in creating a doc per sentence """
        for example in examples:
            output = []
            if gold_preproc:
                split_examples = example.split_sents()
                for split_example in split_examples:
                    output.append(
                        cls._append(
                            nlp,
                            split_example,
                            noise_level=noise_level,
                            orth_variant_level=orth_variant_level,
                        )
                    )
            else:
                output.append(
                    cls._add_doc(
                        nlp,
                        example,
                        noise_level=noise_level,
                        orth_variant_level=orth_variant_level,
                    )
                )
            for ex in output:
                if (not max_length) or len(ex.doc) < max_length:
                    yield ex

    @classmethod
    def _add_doc(
        cls, nlp, example, noise_level=0.0, orth_variant_level=0.0
    ):
        var_example = make_orth_variants(
            nlp, example, orth_variant_level=orth_variant_level
        )
        if example.text is not None:
            var_text = add_noise(var_example.text, noise_level)
            var_example.doc = nlp.make_doc(var_text)
        else:
            var_example.doc = Doc(
                nlp.vocab,
                words=add_noise(var_example.token_annotation.words, noise_level),
            )
        return var_example
