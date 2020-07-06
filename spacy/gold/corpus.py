import random
from .. import util
from .example import Example
from ..tokens import DocBin, Doc


class Corpus:
    """An annotated corpus, reading train and dev datasets from
    the DocBin (.spacy) format.

    DOCS: https://spacy.io/api/corpus
    """

    def __init__(self, train_loc, dev_loc, limit=0):
        """Create a Corpus.

        train (str / Path): File or directory of training data.
        dev (str / Path): File or directory of development data.
        limit (int): Max. number of examples returned
        RETURNS (Corpus): The newly created object.
        """
        self.train_loc = train_loc
        self.dev_loc = dev_loc
        self.limit = limit

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

    def _make_example(self, nlp, reference, gold_preproc):
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

    def make_examples(self, nlp, reference_docs, max_length=0):
        for reference in reference_docs:
            if len(reference) == 0:
                continue
            elif max_length == 0 or len(reference) < max_length:
                yield self._make_example(nlp, reference, False)
            elif reference.is_sentenced:
                for ref_sent in reference.sents:
                    if len(ref_sent) == 0:
                        continue
                    elif max_length == 0 or len(ref_sent) < max_length:
                        yield self._make_example(nlp, ref_sent.as_doc(), False)

    def make_examples_gold_preproc(self, nlp, reference_docs):
        for reference in reference_docs:
            if reference.is_sentenced:
                ref_sents = [sent.as_doc() for sent in reference.sents]
            else:
                ref_sents = [reference]
            for ref_sent in ref_sents:
                eg = self._make_example(nlp, ref_sent, True)
                if len(eg.x):
                    yield eg

    def read_docbin(self, vocab, locs):
        """ Yield training examples as example dicts """
        i = 0
        for loc in locs:
            loc = util.ensure_path(loc)
            if loc.parts[-1].endswith(".spacy"):
                with loc.open("rb") as file_:
                    doc_bin = DocBin().from_bytes(file_.read())
                docs = doc_bin.get_docs(vocab)
                for doc in docs:
                    if len(doc):
                        yield doc
                        i += 1
                        if self.limit >= 1 and i >= self.limit:
                            break

    def count_train(self, nlp):
        """Returns count of words in train examples"""
        n = 0
        i = 0
        for example in self.train_dataset(nlp):
            n += len(example.predicted)
            if self.limit >= 0 and i >= self.limit:
                break
            i += 1
        return n

    def train_dataset(
        self, nlp, *, shuffle=True, gold_preproc=False, max_length=0, **kwargs
    ):
        ref_docs = self.read_docbin(nlp.vocab, self.walk_corpus(self.train_loc))
        if gold_preproc:
            examples = self.make_examples_gold_preproc(nlp, ref_docs)
        else:
            examples = self.make_examples(nlp, ref_docs, max_length)
        if shuffle:
            examples = list(examples)
            random.shuffle(examples)
        yield from examples

    def dev_dataset(self, nlp, *, gold_preproc=False, **kwargs):
        ref_docs = self.read_docbin(nlp.vocab, self.walk_corpus(self.dev_loc))
        if gold_preproc:
            examples = self.make_examples_gold_preproc(nlp, ref_docs)
        else:
            examples = self.make_examples(nlp, ref_docs, max_length=0)
        yield from examples
