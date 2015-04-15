#!/usr/bin/env python
from __future__ import division
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

import spacy.util
from spacy.en import English
from spacy.en.pos import POS_TEMPLATES, POS_TAGS, setup_model_dir

from spacy.syntax.parser import GreedyParser
from spacy.syntax.parser import OracleError
from spacy.syntax.util import Config
from spacy.syntax.conll import read_docparse_file
from spacy.syntax.conll import GoldParse

from spacy.scorer import Scorer


def train(Language, train_loc, model_dir, n_iter=15, feat_set=u'basic', seed=0,
          gold_preproc=False, n_sents=0):
    dep_model_dir = path.join(model_dir, 'deps')
    pos_model_dir = path.join(model_dir, 'pos')
    ner_model_dir = path.join(model_dir, 'ner')
    if path.exists(dep_model_dir):
        shutil.rmtree(dep_model_dir)
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    if path.exists(ner_model_dir):
        shutil.rmtree(ner_model_dir)
    os.mkdir(dep_model_dir)
    os.mkdir(pos_model_dir)
    os.mkdir(ner_model_dir)

    setup_model_dir(sorted(POS_TAGS.keys()), POS_TAGS, POS_TEMPLATES, pos_model_dir)

    gold_tuples = read_docparse_file(train_loc)

    Config.write(dep_model_dir, 'config', features=feat_set, seed=seed,
                 labels=Language.ParserTransitionSystem.get_labels(gold_tuples))
    Config.write(ner_model_dir, 'config', features='ner', seed=seed,
                 labels=Language.EntityTransitionSystem.get_labels(gold_tuples))

    if n_sents > 0:
        gold_tuples = gold_tuples[:n_sents]
    nlp = Language(data_dir=model_dir)

    print "Itn.\tUAS\tNER F.\tTag %"
    for itn in range(n_iter):
        scorer = Scorer()
        for raw_text, segmented_text, annot_tuples in gold_tuples:
            # Eval before train
            tokens = nlp(raw_text, merge_mwes=False)
            gold = GoldParse(tokens, annot_tuples)
            scorer.score(tokens, gold, verbose=False)

            if gold_preproc:
                sents = [nlp.tokenizer.tokens_from_list(s) for s in segmented_text]
            else:
                sents = [nlp.tokenizer(raw_text)]
            for tokens in sents:
                gold = GoldParse(tokens, annot_tuples)
                nlp.tagger(tokens)
                nlp.parser.train(tokens, gold)
                if gold.ents:
                    nlp.entity.train(tokens, gold)
                nlp.tagger.train(tokens, gold.tags)

        print '%d:\t%.3f\t%.3f\t%.3f' % (itn, scorer.uas, scorer.ents_f, scorer.tags_acc)
        random.shuffle(gold_tuples)
    nlp.parser.model.end_training()
    nlp.entity.model.end_training()
    nlp.tagger.model.end_training()
    nlp.vocab.strings.dump(path.join(model_dir, 'vocab', 'strings.txt'))


def evaluate(Language, dev_loc, model_dir, gold_preproc=False, verbose=True):
    assert not gold_preproc
    nlp = Language(data_dir=model_dir)
    gold_tuples = read_docparse_file(dev_loc)
    scorer = Scorer()
    for raw_text, segmented_text, annot_tuples in gold_tuples:
        tokens = nlp(raw_text, merge_mwes=False)
        gold = GoldParse(tokens, annot_tuples)
        scorer.score(tokens, gold, verbose=verbose)
    return scorer


def write_parses(Language, dev_loc, model_dir, out_loc):
    nlp = Language()
    gold_tuples = read_docparse_file(dev_loc)
    scorer = Scorer()
    out_file = codecs.open(out_loc, 'w', 'utf8')
    for raw_text, segmented_text, annot_tuples in gold_tuples:
        tokens = nlp(raw_text)
        for t in tokens:
            out_file.write(
                '%s\t%s\t%s\t%s\n' % (t.orth_, t.tag_, t.head.orth_, t.dep_)
            )
    return scorer


@plac.annotations(
    train_loc=("Training file location",),
    dev_loc=("Dev. file location",),
    model_dir=("Location of output model directory",),
    out_loc=("Out location", "option", "o", str),
    n_sents=("Number of training sentences", "option", "n", int),
    verbose=("Verbose error reporting", "flag", "v", bool),
    debug=("Debug mode", "flag", "d", bool)
)
def main(train_loc, dev_loc, model_dir, n_sents=0, out_loc="", verbose=False,
         debug=False):
    train(English, train_loc, model_dir, feat_set='basic' if not debug else 'debug',
          gold_preproc=False, n_sents=n_sents)
    if out_loc:
        write_parses(English, dev_loc, model_dir, out_loc)
    scorer = evaluate(English, dev_loc, model_dir, gold_preproc=False, verbose=verbose)
    print 'TOK', scorer.mistokened
    print 'POS', scorer.tags_acc
    print 'UAS', scorer.uas
    print 'LAS', scorer.las

    print 'NER P', scorer.ents_p
    print 'NER R', scorer.ents_r
    print 'NER F', scorer.ents_f
    

if __name__ == '__main__':
    plac.call(main)
