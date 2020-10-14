from wasabi import Printer

from .conll_ner_to_docs import n_sents_info
from ...vocab import Vocab
from ...training import iob_to_biluo, tags_to_entities
from ...tokens import Doc, Span
from ...errors import Errors
from ...util import minibatch


def iob_to_docs(input_data, n_sents=10, no_print=False, *args, **kwargs):
    """
    Convert IOB files with one sentence per line and tags separated with '|'
    into Doc objects so they can be saved. IOB and IOB2 are accepted.

    Sample formats:

    I|O like|O London|I-GPE and|O New|B-GPE York|I-GPE City|I-GPE .|O
    I|O like|O London|B-GPE and|O New|B-GPE York|I-GPE City|I-GPE .|O
    I|PRP|O like|VBP|O London|NNP|I-GPE and|CC|O New|NNP|B-GPE York|NNP|I-GPE City|NNP|I-GPE .|.|O
    I|PRP|O like|VBP|O London|NNP|B-GPE and|CC|O New|NNP|B-GPE York|NNP|I-GPE City|NNP|I-GPE .|.|O
    """
    vocab = Vocab()  # need vocab to make a minimal Doc
    msg = Printer(no_print=no_print)
    if n_sents > 0:
        n_sents_info(msg, n_sents)
    docs = read_iob(input_data.split("\n"), vocab, n_sents)
    return docs


def read_iob(raw_sents, vocab, n_sents):
    docs = []
    for group in minibatch(raw_sents, size=n_sents):
        tokens = []
        words = []
        tags = []
        iob = []
        sent_starts = []
        for line in group:
            if not line.strip():
                continue
            sent_tokens = [t.split("|") for t in line.split()]
            if len(sent_tokens[0]) == 3:
                sent_words, sent_tags, sent_iob = zip(*sent_tokens)
            elif len(sent_tokens[0]) == 2:
                sent_words, sent_iob = zip(*sent_tokens)
                sent_tags = ["-"] * len(sent_words)
            else:
                raise ValueError(Errors.E902)
            words.extend(sent_words)
            tags.extend(sent_tags)
            iob.extend(sent_iob)
            tokens.extend(sent_tokens)
            sent_starts.append(True)
            sent_starts.extend([False for _ in sent_words[1:]])
        doc = Doc(vocab, words=words)
        for i, tag in enumerate(tags):
            doc[i].tag_ = tag
        for i, sent_start in enumerate(sent_starts):
            doc[i].is_sent_start = sent_start
        biluo = iob_to_biluo(iob)
        entities = tags_to_entities(biluo)
        doc.ents = [Span(doc, start=s, end=e + 1, label=L) for (L, s, e) in entities]
        docs.append(doc)
    return docs
