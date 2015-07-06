#!/usr/bin/env python
from __future__ import division
from __future__ import unicode_literals

import os
from os import path
import shutil
import codecs
import random

import plac
import cProfile
import pstats
import re

from spacy.en import English


def score_model(nlp, semcor_docs):
    n_right = 0
    n_wrong = 0
    n_multi = 0
    for dnum, paras in semcor_docs:
        for pnum, para in paras:
            for snum, sent in para:
                words = [t.orth for t in sent]
                tokens = nlp.tokenizer.tokens_from_list(words)
                nlp.tagger(tokens)
                nlp.senser(tokens)
                for i, token in enumerate(tokens):
                    if '_' in sent[i].orth:
                        n_multi += 1
                    elif sent[i].supersense != 'NO_SENSE':
                        n_right += token.sense_ == sent[i].supersense
                        n_wrong += token.sense_ != sent[i].supersense
    return n_multi, n_right, n_wrong


def train(Language, model_dir, docs, annotations, report_every=1000, n_docs=1000):
    wsd_model_dir = path.join(model_dir, 'wsd')
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(wsd_model_dir)
    
    Config.write(wsd_model_dir, 'config', seed=seed)

    nlp = Language(data_dir=model_dir)

    for doc in corpus:
        tokens = nlp(doc, senser=False)
        loss += nlp.senser.train(tokens)
        if i and not i % report_every:
            acc = score_model(nlp, dev_docs)
            print loss, n_right / (n_right + n_wrong)
    nlp.senser.end_training()
    nlp.vocab.strings.dump(path.join(model_dir, 'vocab', 'strings.txt'))


@plac.annotations(
    docs_db_loc=("Location of the documents SQLite database"),
    model_dir=("Location of the models directory"),
    n_docs=("Number of training documents", "option", "n", int),
    verbose=("Verbose error reporting", "flag", "v", bool),
    debug=("Debug mode", "flag", "d", bool),
)
def main(train_loc, dev_loc, model_dir, n_docs=0):
    train_docs = DocsDB(train_loc)
    dev_docs = read_semcor(dev_loc)
    train(English, model_dir, train_docs, dev_docs, report_every=10, n_docs=1000):


if __name__ == '__main__':
    plac.call(main)
