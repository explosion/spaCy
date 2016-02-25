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

from spacy.tagger import Tagger


class GoldSents(object):
    def __init__(self, tokenizer, sents, n=5000):
        self.tokenizer = tokenizer
        self.sents = sents
        self.n = n

    def __iter__(self):
        random.shuffle(self.sents)
        for words, gold in self.sents[:self.n]:
            tokens = self.tokenizer.tokens_from_list(words)
            yield tokens, gold


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


def beam_sgd(tagger, train_data, check_data):
    print(tagger.model.widths)
    print("Itn.\tTrain\tPrev\tNew")
    queue = [(score_model(check_data, tagger), 0, tagger)]
    workers = [None] * 100
    limit = 4
    while True:
        for prev_score, i, tagger in list(queue):
            #prev_score, i, tagger = max(queue)
            train_acc, new_model = get_new_model(train_data, tagger)
            new_score = score_model(check_data, new_model)
            queue.append((new_score, i+1, new_model))
            print('%d:\t%.3f\t%.3f\t%.3f\t%.4f' % (i, train_acc, prev_score, new_score,
                tagger.model.eta))
        queue.sort(reverse=True)
        queue = queue[:limit]
    return max(queue)


def score_model(gold_sents, tagger):
    correct = 0.0
    total = 0.0
    for tokens, gold_tags in gold_sents:
        tagger(tokens)
        for token, gold in zip(tokens, gold_tags):
            correct += token.tag_ == gold
            total += 1
    return (correct / total) * 100


def get_new_model(gold_sents, tagger):
    learn_rate = numpy.random.normal(loc=tagger.model.learn_rate, scale=0.001)
    if learn_rate < 0.0001:
        learn_rate = 0.0001

    new_model = Tagger.blank(tagger.vocab, [],
                    learn_rate=learn_rate,
                    depth=tagger.model.depth,
                    hidden_width=tagger.model.hidden_width,
                    chars_width=tagger.model.chars_width,
                    tags_width=tagger.model.tags_width,
                    left_window=tagger.model.left_window,
                    right_window=tagger.model.right_window,
                    tags_window=tagger.model.tags_window,
                    chars_per_word=tagger.model.chars_per_word)
    new_model.model.embeddings = tagger.model.embeddings
    new_model.model.weights = tagger.model.weights
    correct = 0.0
    total = 0.0
    for tokens, gold in gold_sents:
        correct += new_model.train(tokens, gold)
        total += len(tokens)
    return (correct / total), new_model
 

def train(Language, train_sents, dev_sents, model_dir, n_iter=15, seed=0,
          gold_preproc=False, **model_args):
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(pos_model_dir)
    nlp = Language(data_dir=model_dir, tagger=False, parser=False, entity=False)
    # Insert words into the vocab. Yes, confusing...
    for words, tags in train_sents:
        for word in words:
            _ = nlp.vocab[word]
    nr_train = len(train_sents)
    random.shuffle(train_sents)
    heldout_sents = train_sents[:int(nr_train * 0.1)] 
    train_sents = train_sents[len(heldout_sents):]

    train_sents = GoldSents(nlp.tokenizer, train_sents)
    heldout_sents = GoldSents(nlp.tokenizer, heldout_sents)

    tagger = Tagger.blank(nlp.vocab, [], **model_args)
    return beam_sgd(tagger, train_sents, heldout_sents)

    #prev_score = 0.0
    #variance = 0.001
    #last_good_learn_rate = nlp.tagger.model.eta
    #n = 0
    #total = 0
    #acc = 0
    #last_model = (nlp.tagger.model.weights, nlp.tagger.model.embeddings)
    #while True:
    #    words, gold_tags = random.choice(train_sents)
    #    tokens = nlp.tokenizer.tokens_from_list(words)
    #    acc += nlp.tagger.train(tokens, gold_tags)
    #    total += len(tokens)
    #    n += 1
    #    if n and n % 20000 == 0:
    #        dev_score = score_model(nlp, heldout_sents)
    #        eval_score = score_model(nlp, dev_sents)
    #        if dev_score >= prev_score:
    #            last_model = (nlp.tagger.model.weights, nlp.tagger.model.embeddings)
    #            prev_score = dev_score
    #            variance = 0.001
    #            last_good_learn_rate = nlp.tagger.model.eta
    #            nlp.tagger.model.eta *= 1.01
    #            
    #        else:
    #            nlp.tagger.model.weights = last_model[0]
    #            nlp.tagger.model.embeddings = last_model[1]
    #            new_eta = numpy.random.normal(loc=last_good_learn_rate, scale=variance)
    #            if new_eta >= 0.0001:
    #                nlp.tagger.model.eta = new_eta
    #            else:
    #                nlp.tagger.model.eta = 0.0001
    #            print('X:\t%.3f\t%.3f\t%.3f\t%.4f' % (acc/total, dev_score, eval_score, nlp.tagger.model.eta))
    #            variance *= 1.1
    #            prev_score *= 0.9999
    #        acc = 0.0
    #        total = 0.0
    #nlp.end_training(data_dir=model_dir)
    #return nlp


@plac.annotations(
    train_loc=("Location of training file or directory"),
    dev_loc=("Location of development file or directory"),
    model_dir=("Location of output model directory",),
    learn_rate=("Learning rate for SGD", "option", "e", float),
    n_iter=("Number of training iterations", "option", "i", int),
    depth=("Number of hidden layers", "option", "d", int),
    hidden_width=("Number of neurons in each hidden layers", "option", "H", int),
    chars_width=("Width of character embedding", "option", "C", int),
    tags_width=("Width of tag embedding", "option", "T", int),
    left_window=("Number of words of left context", "option", "l", int),
    right_window=("Number of words of right context", "option", "r", int),
    tags_window=("Number of tags in history", "option", "t", int),
    chars_per_word=("Number of characters per word", "option", "c", int),
)
def main(lang_id, train_loc, dev_loc, model_dir, n_iter=5, learn_rate=0.005,
        depth=3, hidden_width=100, chars_width=5, tags_width=10, left_window=2,
        right_window=2, tags_window=2, chars_per_word=8):
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
    nlp = train(Language, train_sents, dev_sents, model_dir,
        n_iter=n_iter, learn_rate=learn_rate,
        depth=depth, hidden_width=hidden_width, chars_width=chars_width, tags_width=tags_width,
        left_window=left_window, right_window=right_window, tags_window=tags_window,
        chars_per_word=chars_per_word)


if __name__ == '__main__':
    plac.call(main)
