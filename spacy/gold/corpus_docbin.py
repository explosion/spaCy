import srsly
from pathlib import Path
import random
from .. import util
from .example import Example
from ..tokens import DocBin


class Corpus:
    """An annotated corpus, using the JSON file format. Manages
    annotations for tagging, dependency parsing and NER.

    DOCS: https://spacy.io/api/goldcorpus
    """
    def __init__(self, train_loc, dev_loc, limit=0):
        """Create a GoldCorpus.

        train (str / Path): File or directory of training data.
        dev (str / Path): File or directory of development data.
        RETURNS (GoldCorpus): The newly created object.
        """
        self.train_loc = train_loc 
        self.dev_loc = dev_loc

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
            elif path.parts[-1].endswith(".spacy"):
                locs.append(path)
        return locs

    def make_examples(self, nlp, reference_docs, **kwargs):
        for reference in reference_docs:
            predicted = nlp.make_doc(reference.text)
            yield Example(predicted, reference)

    def read_docbin(self, vocab, locs, limit=0):
        """ Yield training examples as example dicts """
        i = 0
        for loc in locs:
            loc = util.ensure_path(loc)
            if loc.parts[-1].endswith(".spacy"):
                with loc.open("rb") as file_:
                    doc_bin = DocBin().from_bytes(file_.read())
                yield from doc_bin.get_docs(vocab)
    
    def count_train(self, nlp):
        """Returns count of words in train examples"""
        n = 0
        i = 0
        for example in self.train_dataset(nlp):
            n += len(example.predicted)
            if self.limit and i >= self.limit:
                break
            i += 1
        return n

    def train_dataset(self, nlp, shuffle=True, **kwargs):
        ref_docs = self.read_docbin(nlp.vocab, self.walk_corpus(self.train_loc))
        examples = self.make_examples(nlp, ref_docs, **kwargs)
        if shuffle:
            examples = list(examples)
            random.shuffle(examples)
        yield from examples

    def dev_dataset(self, nlp):
        ref_docs = self.read_docbin(nlp.vocab, self.walk_corpus(self.train_loc))
        examples = self.make_examples(nlp, ref_docs, **kwargs)
        yield from examples
