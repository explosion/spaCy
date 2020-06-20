from wasabi import Printer

from ...gold import iob_to_biluo, tags_to_entities
from ...util import minibatch
from .util import merge_sentences
from .conll_ner2json import n_sents_info


def iob2docs(input_data, n_sents=10, no_print=False, *args, **kwargs):
    """
    Convert IOB files with one sentence per line and tags separated with '|'
    into Doc objects so they can be saved. IOB and IOB2 are accepted.

    Sample formats:

    I|O like|O London|I-GPE and|O New|B-GPE York|I-GPE City|I-GPE .|O
    I|O like|O London|B-GPE and|O New|B-GPE York|I-GPE City|I-GPE .|O
    I|PRP|O like|VBP|O London|NNP|I-GPE and|CC|O New|NNP|B-GPE York|NNP|I-GPE City|NNP|I-GPE .|.|O
    I|PRP|O like|VBP|O London|NNP|B-GPE and|CC|O New|NNP|B-GPE York|NNP|I-GPE City|NNP|I-GPE .|.|O
    """
    msg = Printer(no_print=no_print)
    docs = read_iob(input_data.split("\n"))
    if n_sents > 0:
        n_sents_info(msg, n_sents)
        docs = merge_sentences(docs, n_sents)
    return docs


def read_iob(raw_sents):
    docs = []
    for line in raw_sents:
        if not line.strip():
            continue
        tokens = [t.split("|") for t in line.split()]
        if len(tokens[0]) == 3:
            words, tags, iob = zip(*tokens)
        elif len(tokens[0]) == 2:
            words, iob = zip(*tokens)
            tags = ["-"] * len(words)
        else:
            raise ValueError(
                "The sentence-per-line IOB/IOB2 file is not formatted correctly. Try checking whitespace and delimiters. See https://spacy.io/api/cli#convert"
            )
        doc = Doc(vocab, words=words)
        for i, tag in enumerate(pos):
            doc[i].tag_ = tag
        biluo = iob_to_biluo(iob)
        entities = biluo_tags_to_entities(biluo)
        doc.ents = [Span(doc, start=s, end=e, label=L) for (L, s, e) in entities]
        docs.append(doc)
    return docs
