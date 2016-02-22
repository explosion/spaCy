#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from os import path
import shutil
import codecs
import random
import time
import gzip

import plac
import cProfile
import pstats
import numpy.random

from spacy.en import English
from spacy.de import German

import spacy.util
from spacy.syntax.util import Config

from spacy.scorer import Scorer
from spacy.tagger import Tagger


from spacy.tagger import P2_orth, P2_shape, P2_prefix, P2_suffix, P2_pos, P2_flags
from spacy.tagger import P1_orth, P1_shape, P1_prefix, P1_suffix, P1_pos, P1_flags
from spacy.tagger import W_orth, W_shape, W_prefix, W_suffix, W_pos, W_flags
from spacy.tagger import N1_orth, N1_shape, N1_prefix, N1_suffix, N1_pos, N1_flags
from spacy.tagger import N2_orth, N2_shape, N2_prefix, N2_suffix, N2_pos, N2_flags


templates = {
    'de': [
        (W_orth,),
        (P1_orth, P1_pos),
        (P2_orth, P2_pos),
        (N1_orth,),
        (N2_orth,),

        (W_suffix,),
        (W_prefix,),

        (P1_pos,),
        (P2_pos,),
        (P1_pos, P2_pos),
        (P1_pos, W_orth),
        (P1_suffix,),
        (N1_suffix,),

        (W_shape,),

        (W_flags,),
        (N1_flags,),
        (N2_flags,),
        (P1_flags,),
        (P2_flags,)
    ]
}
 

def read_conll(file_):
    """Read a standard CoNLL/MALT-style format"""
    sents = []
    for sent_str in file_.read().strip().split('\n\n'):
        words = []
        tags = []
        for i, line in enumerate(sent_str.split('\n')):
            if line.startswith('#'):
                continue
            idx, word, pos_string = _parse_line(line)
            words.append(word)
            tags.append(pos_string)
        sents.append((words, tags))
    return sents


def _parse_line(line):
    pieces = line.split()
    id_ = int(pieces[0].split('_')[-1])-1
    word = pieces[1]
    pos = pieces[4]
    return id_, word, pos

        
def score_model(nlp, gold_tuples, verbose=False):
    scorer = Scorer()
    for words, gold_tags in gold_tuples:
        tokens = nlp.tokenizer.tokens_from_list(words)
        nlp.tagger(tokens)
        for token, gold in zip(tokens, gold_tags):
            scorer.tags.tp += token.tag_ == gold
            scorer.tags.fp += token.tag_ != gold
            scorer.tags.fn += token.tag_ != gold
    return scorer.tags_acc


def train(Language, train_sents, dev_sents, model_dir, n_iter=15, seed=0,
          gold_preproc=False, eta=0.005):
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(pos_model_dir)
    nlp = Language(data_dir=model_dir, tagger=False, parser=False, entity=False)
    # Insert words into the vocab. Yes, confusing...
    for words, tags in train_sents:
        for word in words:
            _ = nlp.vocab[word]
    nlp.tagger = Tagger.blank(nlp.vocab, templates['de'], learn_rate=eta)
    print(nlp.tagger.model.widths)
    print("Itn.\tTrain\tCheck\tDev")
    nr_train = len(train_sents)
    random.shuffle(train_sents)
    heldout_sents = train_sents[:int(nr_train * 0.1)] 
    train_sents = train_sents[len(heldout_sents):]
    #train_sents = train_sents[:500]
    #assert len(heldout_sents) < len(train_sents)
    prev_score = 0.0
    variance = 0.001
    last_good_learn_rate = nlp.tagger.model.eta
    n = 0
    total = 0
    acc = 0
    while True:
        words, gold_tags = random.choice(train_sents)
        tokens = nlp.tokenizer.tokens_from_list(words)
        acc += nlp.tagger.train(tokens, gold_tags)
        total += len(tokens)
        n += 1
        if n and n % 10000 == 0:
            dev_score = score_model(nlp, heldout_sents)
            eval_score = score_model(nlp, dev_sents)
            if dev_score > prev_score:
                nlp.tagger.model.keep_update()
                prev_score = dev_score
                variance = 0.001
                last_good_learn_rate = nlp.tagger.model.eta
                nlp.tagger.model.eta *= 1.05
                print('%d:\t%.3f\t%.3f\t%.3f\t%.4f' % (n, acc/total, dev_score, eval_score, nlp.tagger.model.eta))
            else:
                nlp.tagger.model.backtrack()
                new_eta = numpy.random.normal(loc=last_good_learn_rate, scale=variance)
                if new_eta >= 0.0001:
                    nlp.tagger.model.eta = new_eta
                else:
                    nlp.tagger.model.eta = 0.0001
                print('X:\t%.3f\t%.3f\t%.3f\t%.4f' % (acc/total, dev_score, eval_score, nlp.tagger.model.eta))
                variance *= 1.1
                prev_score *= 0.9999
            acc = 0.0
            total = 0.0
    nlp.end_training(data_dir=model_dir)
    return nlp


@plac.annotations(
    train_loc=("Location of training file or directory"),
    dev_loc=("Location of development file or directory"),
    model_dir=("Location of output model directory",),
    eta=("Learning rate for Adagrad optimizer", "option", "e", float),
    n_iter=("Number of training iterations", "option", "i", int),
)
def main(lang_id, train_loc, dev_loc, model_dir, n_iter=5, eta=0.005):
    if lang_id == 'en':
        Language = English
    elif lang_id == 'de':
        Language = German
    elif lang_id == 'fi':
        Language = Finnish
    elif lang_id == 'it':
        Language = Italian
    with codecs.open(train_loc, 'r', 'utf8') as file_:
        train_sents = read_conll(file_)
    dev_sents = read_conll(codecs.open(dev_loc, 'r', 'utf8'))
    nlp = train(Language, train_sents, dev_sents, model_dir, n_iter=n_iter, eta=eta)
    #nlp = Language(data_dir=model_dir)
    scorer = score_model(nlp, dev_sents)
    print('TOK', 100-scorer.token_acc)
    print('POS', scorer.tags_acc)


if __name__ == '__main__':
    plac.call(main)
