from spacy.util import minibatch


def merge_sentences(docs, n_sents):
    merged = []
    for group in minibatch(docs, size=n_sents):
        raise NotImplementedError
    return merged
