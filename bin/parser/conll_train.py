#!/usr/bin/env python
from __future__ import division
from __future__ import unicode_literals

import os
from os import path
import shutil
import io
import random
import time
import gzip

import plac
import cProfile
import pstats

import spacy.util
from spacy.en import English
from spacy.gold import GoldParse

from spacy.syntax.util import Config
from spacy.syntax.arc_eager import ArcEager
from spacy.syntax.parser import Parser
from spacy.scorer import Scorer
from spacy.tagger import Tagger

# Last updated for spaCy v0.97


def read_conll(file_):
    """Read a standard CoNLL/MALT-style format"""
    sents = []
    for sent_str in file_.read().strip().split('\n\n'):
        ids = []
        words = []
        heads = []
        labels = []
        tags = []
        for i, line in enumerate(sent_str.split('\n')):
            word, pos_string, head_idx, label = _parse_line(line)
            words.append(word)
            if head_idx < 0:
                head_idx = i
            ids.append(i)
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
        text = ' '.join(words)
        annot = (ids, words, tags, heads, labels, ['O'] * len(ids))
        sents.append((None, [(annot, [])]))
    return sents


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
    if head_idx == 0:
        label = 'ROOT'
    return word, pos, head_idx, label

        
def score_model(scorer, nlp, raw_text, annot_tuples, verbose=False):
    tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
    nlp.tagger(tokens)
    nlp.parser(tokens)
    gold = GoldParse(tokens, annot_tuples, make_projective=False)
    scorer.score(tokens, gold, verbose=verbose, punct_labels=('--', 'p', 'punct'))


def train(Language, gold_tuples, model_dir, n_iter=15, feat_set=u'basic', seed=0,
          gold_preproc=False, force_gold=False):
    dep_model_dir = path.join(model_dir, 'deps')
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(dep_model_dir):
        shutil.rmtree(dep_model_dir)
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(dep_model_dir)
    os.mkdir(pos_model_dir)

    Config.write(dep_model_dir, 'config', features=feat_set, seed=seed,
                 labels=ArcEager.get_labels(gold_tuples))

    nlp = Language(data_dir=model_dir, tagger=False, parser=False, entity=False)
    nlp.tagger = Tagger.blank(nlp.vocab, Tagger.default_templates())
    nlp.parser = Parser.from_dir(dep_model_dir, nlp.vocab.strings, ArcEager)
 
    print("Itn.\tP.Loss\tUAS\tNER F.\tTag %\tToken %")
    for itn in range(n_iter):
        scorer = Scorer()
        loss = 0
        for _, sents in gold_tuples:
            for annot_tuples, _ in sents:
                if len(annot_tuples[1]) == 1:
                    continue

                score_model(scorer, nlp, None, annot_tuples, verbose=False)

                tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
                nlp.tagger(tokens)
                gold = GoldParse(tokens, annot_tuples, make_projective=True)
                if not gold.is_projective:
                    raise Exception(
                        "Non-projective sentence in training, after we should "
                        "have enforced projectivity: %s" % annot_tuples
                    )
 
                loss += nlp.parser.train(tokens, gold)
                nlp.tagger.train(tokens, gold.tags)
        random.shuffle(gold_tuples)
        print('%d:\t%d\t%.3f\t%.3f\t%.3f' % (itn, loss, scorer.uas,
                                             scorer.tags_acc, scorer.token_acc))
    print('end training')
    nlp.end_training(model_dir)
    print('done')


@plac.annotations(
    train_loc=("Location of CoNLL 09 formatted training file"),
    dev_loc=("Location of CoNLL 09 formatted development file"),
    model_dir=("Location of output model directory"),
    eval_only=("Skip training, and only evaluate", "flag", "e", bool),
    n_iter=("Number of training iterations", "option", "i", int),
)
def main(train_loc, dev_loc, model_dir, n_iter=15):
    with io.open(train_loc, 'r', encoding='utf8') as file_:
        train_sents = read_conll(file_)
    if not eval_only:
        train(English, train_sents, model_dir, n_iter=n_iter)
    nlp = English(data_dir=model_dir)
    dev_sents = read_conll(io.open(dev_loc, 'r', encoding='utf8'))
    scorer = Scorer()
    for _, sents in dev_sents:
        for annot_tuples, _ in sents:
            score_model(scorer, nlp, None, annot_tuples)
    print('TOK', 100-scorer.token_acc)
    print('POS', scorer.tags_acc)
    print('UAS', scorer.uas)
    print('LAS', scorer.las)


if __name__ == '__main__':
    plac.call(main)
