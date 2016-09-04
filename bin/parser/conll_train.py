#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
from os import path
import shutil
import io
import random
import time
import gzip
import re
import numpy
from math import sqrt

import plac
import cProfile
import pstats

import spacy.util
from spacy.en import English
from spacy.gold import GoldParse

from spacy.syntax.util import Config
from spacy.syntax.arc_eager import ArcEager
from spacy.syntax.parser import Parser, get_templates
from spacy.syntax.beam_parser import BeamParser
from spacy.scorer import Scorer
from spacy.tagger import Tagger
from spacy.syntax.nonproj import PseudoProjectivity
from spacy.syntax import _parse_features as pf

# Last updated for spaCy v0.97


def read_conll(file_, n=0):
    """Read a standard CoNLL/MALT-style format"""
    text = file_.read().strip()
    sent_strs = re.split(r'\n\s*\n', text)
    for sent_id, sent_str in enumerate(sent_strs):
        if not sent_str.strip():
            continue
        ids = []
        words = []
        heads = []
        labels = []
        tags = []
        for i, line in enumerate(sent_str.strip().split('\n')):
            word, pos_string, head_idx, label = _parse_line(line)
            words.append(word)
            if head_idx < 0:
                head_idx = i
            ids.append(i)
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
        annot = (ids, words, tags, heads, labels, ['O'] * len(ids))
        yield (None, [(annot, None)])
        if n and sent_id >= n:
            break


def _parse_line(line):
    pieces = line.split()
    if len(pieces) == 4:
        word, pos, head_idx, label = pieces
        head_idx = int(head_idx)
    elif len(pieces) == 15:
        id_ = int(pieces[0].split('_')[-1])
        word = pieces[1]
        pos = pieces[4]
        head_idx = int(pieces[8])-1
        label = pieces[10]
    else:
        id_ = int(pieces[0].split('_')[-1])
        word = pieces[1]
        pos = pieces[4]
        head_idx = int(pieces[6])-1
        label = pieces[7]
    if head_idx < 0:
        label = 'ROOT'
    return word, pos, head_idx, label


def print_words(strings, words, embeddings):
    ids = {strings[word]: word for word in words}
    vectors = {}
    for key, values in embeddings[5]:
        if key in ids:
            vectors[strings[key]] = values
    for word in words:
        if word in vectors:
            print(word, vectors[word])

        
def score_model(scorer, nlp, raw_text, annot_tuples, verbose=False):
    tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
    nlp.tagger.tag_from_strings(tokens, annot_tuples[2])
    nlp.parser(tokens)
    gold = GoldParse(tokens, annot_tuples, make_projective=False)
    scorer.score(tokens, gold, verbose=verbose, punct_labels=('--', 'p', 'punct'))


def score_file(nlp, loc):
    scorer = Scorer()
    with io.open(loc, 'r', encoding='utf8') as file_:
        for _, sents in read_conll(file_):
            for annot_tuples, _ in sents:
                score_model(scorer, nlp, None, annot_tuples)
    return scorer


def score_sents(nlp, gold_tuples):
    scorer = Scorer()
    for _, sents in gold_tuples:
        for annot_tuples, _ in sents:
            score_model(scorer, nlp, None, annot_tuples)
    return scorer


def train(Language, gold_tuples, model_dir, dev_loc, n_iter=15, feat_set=u'basic',
          width=128, depth=3,
          learn_rate=0.001, noise=0.01, update_step='sgd_cm', regularization=0.0,
          batch_norm=False, seed=0, gold_preproc=False, force_gold=False):
    dep_model_dir = path.join(model_dir, 'deps')
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(dep_model_dir):
        shutil.rmtree(dep_model_dir)
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(dep_model_dir)
    os.mkdir(pos_model_dir)

    if feat_set != 'neural':
        Config.write(dep_model_dir, 'config', feat_set=feat_set, seed=seed,
            labels=ArcEager.get_labels(gold_tuples),
            eta=learn_rate, rho=regularization)

    else:
        hidden_layers = [width] * depth
        Config.write(dep_model_dir, 'config',
                     model='neural',
                     seed=seed,
                     labels=ArcEager.get_labels(gold_tuples),
                     feat_set=feat_set,
                     hidden_layers=hidden_layers,
                     update_step=update_step,
                     batch_norm=batch_norm,
                     eta=learn_rate,
                     mu=0.9,
                     noise=noise,
                     rho=regularization)

    nlp = Language(data_dir=model_dir, tagger=False, parser=False, entity=False)
    # Insert into vocab
    for _, sents in gold_tuples:
        for annot_tuples, _ in sents:
            for word in annot_tuples[1]:
                _ = nlp.vocab[word] 
    nlp.tagger = Tagger.blank(nlp.vocab, Tagger.default_templates())
    #nlp.parser = BeamParser.from_dir(dep_model_dir, nlp.vocab.strings, ArcEager)
    nlp.parser = Parser.from_dir(dep_model_dir, nlp.vocab.strings, ArcEager)
    for word in nlp.vocab:
        word.norm = word.orth
    
    print(nlp.parser.model.widths)
 
    print("Itn.\tP.Loss\tTrain\tDev\tnr_weight\tnr_feat")
    last_score = 0.0
    nr_trimmed = 0
    eg_seen = 0
    loss = 0
    micro_eval = gold_tuples[:50]
    for itn in range(n_iter):
        try:
            eg_seen = _train_epoch(nlp, gold_tuples, eg_seen, itn,
                                   dev_loc, micro_eval)
        except KeyboardInterrupt:
            print("Saving model...")
            break
    dev_uas = score_file(nlp, dev_loc).uas
    print("Dev before average", dev_uas)

    nlp.parser.model.end_training()
    nlp.parser.model.dump(path.join(model_dir, 'deps', 'model'))
    print("Saved. Evaluating...")
    return nlp


def _train_epoch(nlp, gold_tuples, eg_seen, itn, dev_loc, micro_eval):
    random.shuffle(gold_tuples)
    loss = 0
    nr_trimmed = 0
    for _, sents in gold_tuples:
        for annot_tuples, _ in sents:
            tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
            nlp.tagger.tag_from_strings(tokens, annot_tuples[2])
            gold = GoldParse(tokens, annot_tuples)
            loss += nlp.parser.train(tokens, gold, itn=itn)
            eg_seen += 1
            if eg_seen % 1000 == 0:
                if eg_seen % 20000 == 0:
                    dev_uas = score_file(nlp, dev_loc).uas
                else:
                    dev_uas = 0.0
                train_uas = score_sents(nlp, micro_eval).uas
                nr_upd = nlp.parser.model.time
                nr_weight = nlp.parser.model.nr_weight
                nr_feat = nlp.parser.model.nr_active_feat
                print('%d,%d:\t%d\t%.3f\t%.3f\t%d\t%d' % (itn, nr_upd, int(loss),
                                                          train_uas, dev_uas,
                                                          nr_weight, nr_feat))
                loss = 0
    nlp.parser.model.learn_rate *= 0.99
    return eg_seen


@plac.annotations(
    train_loc=("Location of CoNLL 09 formatted training file"),
    dev_loc=("Location of CoNLL 09 formatted development file"),
    model_dir=("Location of output model directory"),
    n_iter=("Number of training iterations", "option", "i", int),
    batch_norm=("Use batch normalization and residual connections", "flag", "b"),
    update_step=("Update step", "option", "u", str),
    learn_rate=("Learn rate", "option", "e", float),
    regularization=("Regularization penalty", "option", "r", float),
    gradient_noise=("Gradient noise", "option", "W", float),
    neural=("Use neural network?", "flag", "N"),
    width=("Width of hidden layers", "option", "w", int),
    depth=("Number of hidden layers", "option", "d", int),
)
def main(train_loc, dev_loc, model_dir, n_iter=15, neural=False, batch_norm=False,
         width=128, depth=3, learn_rate=0.001, gradient_noise=0.0, regularization=0.0,
         update_step='sgd_cm'):
    with io.open(train_loc, 'r', encoding='utf8') as file_:
        train_sents = list(read_conll(file_))
    # Preprocess training data here before ArcEager.get_labels() is called
    train_sents = PseudoProjectivity.preprocess_training_data(train_sents)

    nlp = train(English, train_sents, model_dir, dev_loc, n_iter=n_iter,
                width=width, depth=depth,
                feat_set='neural' if neural else 'basic',
                batch_norm=batch_norm,
                learn_rate=learn_rate,
                regularization=regularization,
                update_step=update_step,
                noise=gradient_noise)

    scorer = score_file(nlp, dev_loc)
    print('TOK', scorer.token_acc)
    print('POS', scorer.tags_acc)
    print('UAS', scorer.uas)
    print('LAS', scorer.las)
    print('nr_weight', nlp.parser.model.nr_weight)
    print('nr_feat', nlp.parser.model.nr_active_feat)


if __name__ == '__main__':
    plac.call(main)
