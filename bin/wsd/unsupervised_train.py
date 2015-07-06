#!/usr/bin/env python
from __future__ import division
from __future__ import unicode_literals

import os
from os import path
import random
import shutil

import plac

from spacy.munge.corpus import DocsDB
from spacy.munge.read_semcor import read_semcor

from spacy.en import English
from spacy.syntax.util import Config


def score_model(nlp, semcor_docs):
    n_right = 0
    n_wrong = 0
    n_multi = 0
    for dnum, paras in semcor_docs:
        for pnum, para in paras:
            for snum, sent in para:
                words = [t.orth for t in sent]
                if len(words) < 2:
                    continue
                tokens = nlp.tokenizer.tokens_from_list(words)
                nlp.tagger(tokens)
                nlp.parser(tokens)
                nlp.senser(tokens)
                for i, token in enumerate(tokens):
                    if '_' in sent[i].orth:
                        n_multi += 1
                    elif sent[i].supersense != 'NO_SENSE':
                        n_right += token.sense_ == sent[i].supersense
                        n_wrong += token.sense_ != sent[i].supersense
    return n_right / (n_right + n_wrong)


def train(Language, model_dir, train_docs, dev_docs,
          report_every=1000, n_docs=1000, seed=0):
    wsd_model_dir = path.join(model_dir, 'wsd')
    if path.exists(wsd_model_dir):
        shutil.rmtree(wsd_model_dir)
    os.mkdir(wsd_model_dir)
    
    Config.write(wsd_model_dir, 'config', seed=seed)

    nlp = Language(data_dir=model_dir, load_vectors=False)

    loss = 0
    n_tokens = 0
    for i, doc in enumerate(train_docs):
        tokens = nlp(doc, parse=True, entity=False)
        loss += nlp.senser.train(tokens)
        n_tokens += len(tokens)
        if i and i % report_every == 0:
            acc = score_model(nlp, dev_docs)
            print i, loss / n_tokens, acc
    nlp.senser.end_training()
    nlp.vocab.strings.dump(path.join(model_dir, 'vocab', 'strings.txt'))


@plac.annotations(
    train_loc=("Location of the documents SQLite database"),
    dev_loc=("Location of the SemCor corpus directory"),
    model_dir=("Location of the models directory"),
    n_docs=("Number of training documents", "option", "n", int),
    seed=("Random seed", "option", "s", int),
)
def main(train_loc, dev_loc, model_dir, n_docs=1000000, seed=0):
    train_docs = DocsDB(train_loc, limit=n_docs)
    dev_docs = read_semcor(dev_loc)
    train(English, model_dir, train_docs, dev_docs, report_every=100, seed=seed)


if __name__ == '__main__':
    plac.call(main)
