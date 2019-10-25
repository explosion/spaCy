# coding: utf8
from __future__ import unicode_literals

from spacy.gold import GoldCorpus

from spacy.lang.en import English


def test_issue4402():
    json_path = "../../../examples/training/textcat_example_data/cooking.json"
    nlp = English()
    corpus = GoldCorpus(train=json_path, dev=json_path, limit=10)
    train_docs = corpus.train_docs(nlp, gold_preproc=True, max_length=0)
    # checking that iterating over the training docs works fine
    for text, gold in train_docs:
        pass