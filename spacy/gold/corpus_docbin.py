import srsly
from pathlib import Path
from .. import util
from .example import Example
from ..tokens import DocBin


class Corpus:
    """An annotated corpus, using the JSON file format. Manages
    annotations for tagging, dependency parsing and NER.

    DOCS: https://spacy.io/api/goldcorpus
    """
    def __init__(self, vocab, train_loc, dev_loc, limit=0):
        """Create a GoldCorpus.

        train (str / Path): File or directory of training data.
        dev (str / Path): File or directory of development data.
        RETURNS (GoldCorpus): The newly created object.
        """
        self.vocab = vocab
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

    def read_docbin(self, locs, limit=0):
        """ Yield training examples as example dicts """
        i = 0
        for loc in locs:
            loc = util.ensure_path(loc)
            if loc.parts[-1].endswith(".spacy"):
                with loc.open("rb") as file_:
                    doc_bin = DocBin().from_bytes(file_.read())
                docs = list(doc_bin.get_docs(self.vocab))
                assert len(docs) % 2 == 0
                # Pair up the docs into the (predicted, reference) pairs.
                for i in range(0, len(docs), 2):
                    predicted = docs[i]
                    reference = docs[i+1]
                    yield Example(predicted, reference)
    
    def count_train(self):
        """Returns count of words in train examples"""
        n = 0
        i = 0
        for example in self.train_dataset():
            n += len(example.predicted)
            if self.limit and i >= self.limit:
                break
            i += 1
        return n

    def train_dataset(self):
        examples = self.read_docbin(self.walk_corpus(self.train_loc))
        random.shuffle(examples)
        yield from examples

    def dev_dataset(self):
        examples = self.read_docbin(self.walk_corpus(self.dev_loc))
        random.shuffle(examples)
        yield from examples
