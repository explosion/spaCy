#!/usr/bin/env python
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import os
from os import path
import shutil
import codecs
import random

import plac
import re

import spacy.util
from spacy.en import English

from spacy.tagger import Tagger

from spacy.syntax.util import Config
from spacy.gold import read_json_file
from spacy.gold import GoldParse

from spacy.scorer import Scorer


def score_model(scorer, nlp, raw_text, annot_tuples):
    if raw_text is None:
        tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
    else:
        tokens = nlp.tokenizer(raw_text)
    nlp.tagger(tokens)
    gold = GoldParse(tokens, annot_tuples)
    scorer.score(tokens, gold)


def _merge_sents(sents):
    m_deps = [[], [], [], [], [], []]
    m_brackets = []
    i = 0
    for (ids, words, tags, heads, labels, ner), brackets in sents:
        m_deps[0].extend(id_ + i for id_ in ids)
        m_deps[1].extend(words)
        m_deps[2].extend(tags)
        m_deps[3].extend(head + i for head in heads)
        m_deps[4].extend(labels)
        m_deps[5].extend(ner)
        m_brackets.extend((b['first'] + i, b['last'] + i, b['label']) for b in brackets)
        i += len(ids)
    return [(m_deps, m_brackets)]


def train(Language, gold_tuples, model_dir, n_iter=15, feat_set=u'basic',
          seed=0, gold_preproc=False, n_sents=0, corruption_level=0,
          beam_width=1, verbose=False,
          use_orig_arc_eager=False):
    if n_sents > 0:
        gold_tuples = gold_tuples[:n_sents]
   
    templates = Tagger.default_templates()
    nlp = Language(data_dir=model_dir, tagger=False)
    nlp.tagger = Tagger.blank(nlp.vocab, templates)

    print("Itn.\tP.Loss\tUAS\tNER F.\tTag %\tToken %")
    for itn in range(n_iter):
        scorer = Scorer()
        loss = 0
        for raw_text, sents in gold_tuples:
            if gold_preproc:
                raw_text = None
            else:
                sents = _merge_sents(sents)
            for annot_tuples, ctnt in sents:
                words = annot_tuples[1]
                gold_tags = annot_tuples[2]
                score_model(scorer, nlp, raw_text, annot_tuples)
                if raw_text is None:
                    tokens = nlp.tokenizer.tokens_from_list(words)
                else:
                    tokens = nlp.tokenizer(raw_text)
                loss += nlp.tagger.train(tokens, gold_tags)
        random.shuffle(gold_tuples)
        print('%d:\t%d\t%.3f\t%.3f\t%.3f\t%.3f' % (itn, loss, scorer.uas, scorer.ents_f,
                                                   scorer.tags_acc,
                                                   scorer.token_acc))
    nlp.end_training(model_dir)

def evaluate(Language, gold_tuples, model_dir, gold_preproc=False, verbose=False,
             beam_width=None):
    nlp = Language(data_dir=model_dir)
    if beam_width is not None:
        nlp.parser.cfg.beam_width = beam_width
    scorer = Scorer()
    for raw_text, sents in gold_tuples:
        if gold_preproc:
            raw_text = None
        else:
            sents = _merge_sents(sents)
        for annot_tuples, brackets in sents:
            if raw_text is None:
                tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
                nlp.tagger(tokens)
                nlp.entity(tokens)
                nlp.parser(tokens)
            else:
                tokens = nlp(raw_text, merge_mwes=False)
            gold = GoldParse(tokens, annot_tuples)
            scorer.score(tokens, gold, verbose=verbose)
    return scorer


def write_parses(Language, dev_loc, model_dir, out_loc, beam_width=None):
    nlp = Language(data_dir=model_dir)
    if beam_width is not None:
        nlp.parser.cfg.beam_width = beam_width
    gold_tuples = read_json_file(dev_loc)
    scorer = Scorer()
    out_file = codecs.open(out_loc, 'w', 'utf8')
    for raw_text, sents in gold_tuples:
        sents = _merge_sents(sents)
        for annot_tuples, brackets in sents:
            if raw_text is None:
                tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
                nlp.tagger(tokens)
                nlp.entity(tokens)
                nlp.parser(tokens)
            else:
                tokens = nlp(raw_text, merge_mwes=False)
            gold = GoldParse(tokens, annot_tuples)
            scorer.score(tokens, gold, verbose=False)
            for t in tokens:
                out_file.write(
                    '%s\t%s\t%s\t%s\n' % (t.orth_, t.tag_, t.head.orth_, t.dep_)
                )
    return scorer


@plac.annotations(
    train_loc=("Location of training file or directory"),
    dev_loc=("Location of development file or directory"),
    model_dir=("Location of output model directory",),
    eval_only=("Skip training, and only evaluate", "flag", "e", bool),
    corruption_level=("Amount of noise to add to training data", "option", "c", float),
    gold_preproc=("Use gold-standard sentence boundaries in training?", "flag", "g", bool),
    out_loc=("Out location", "option", "o", str),
    n_sents=("Number of training sentences", "option", "n", int),
    n_iter=("Number of training iterations", "option", "i", int),
    verbose=("Verbose error reporting", "flag", "v", bool),
    debug=("Debug mode", "flag", "d", bool),
)
def main(train_loc, dev_loc, model_dir, n_sents=0, n_iter=15, out_loc="", verbose=False,
         debug=False, corruption_level=0.0, gold_preproc=False, eval_only=False):
    if not eval_only:
        gold_train = list(read_json_file(train_loc))
        train(English, gold_train, model_dir,
              feat_set='basic' if not debug else 'debug',
              gold_preproc=gold_preproc, n_sents=n_sents,
              corruption_level=corruption_level, n_iter=n_iter,
              verbose=verbose)
    #if out_loc:
    #    write_parses(English, dev_loc, model_dir, out_loc, beam_width=beam_width)
    scorer = evaluate(English, list(read_json_file(dev_loc)),
                      model_dir, gold_preproc=gold_preproc, verbose=verbose)
    print('TOK', scorer.token_acc)
    print('POS', scorer.tags_acc)
    print('UAS', scorer.uas)
    print('LAS', scorer.las)

    print('NER P', scorer.ents_p)
    print('NER R', scorer.ents_r)
    print('NER F', scorer.ents_f)


if __name__ == '__main__':
    plac.call(main)
