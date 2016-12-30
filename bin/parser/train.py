#!/usr/bin/env python
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import os
from os import path
import shutil
import io
import random

import plac
import re

import spacy.util

from spacy.syntax.util import Config
from spacy.gold import read_json_file
from spacy.gold import GoldParse
from spacy.gold import merge_sents

from spacy.scorer import Scorer

from spacy.syntax.arc_eager import ArcEager
from spacy.syntax.ner import BiluoPushDown
from spacy.tagger import Tagger
from spacy.syntax.parser import Parser
from spacy.syntax.nonproj import PseudoProjectivity


def _corrupt(c, noise_level):
    if random.random() >= noise_level:
        return c
    elif c == ' ':
        return '\n'
    elif c == '\n':
        return ' '
    elif c in ['.', "'", "!", "?"]:
        return ''
    else:
        return c.lower()


def add_noise(orig, noise_level):
    if random.random() >= noise_level:
        return orig
    elif type(orig) == list:
        corrupted = [_corrupt(word, noise_level) for word in orig]
        corrupted = [w for w in corrupted if w]
        return corrupted
    else:
        return ''.join(_corrupt(c, noise_level) for c in orig)


def score_model(scorer, nlp, raw_text, annot_tuples, verbose=False):
    if raw_text is None:
        tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
    else:
        tokens = nlp.tokenizer(raw_text)
    nlp.tagger(tokens)
    nlp.entity(tokens)
    nlp.parser(tokens)
    gold = GoldParse(tokens, annot_tuples)
    scorer.score(tokens, gold, verbose=verbose)


def train(Language, train_data, dev_data, model_dir, tagger_cfg, parser_cfg, entity_cfg,
        n_iter=15, seed=0, gold_preproc=False, n_sents=0, corruption_level=0):
    print("Itn.\tP.Loss\tUAS\tNER F.\tTag %\tToken %")
    format_str = '{:d}\t{:d}\t{uas:.3f}\t{ents_f:.3f}\t{tags_acc:.3f}\t{token_acc:.3f}'
    with Language.train(model_dir, train_data,
            tagger_cfg, parser_cfg, entity_cfg) as trainer:
        loss = 0
        for itn, epoch in enumerate(trainer.epochs(n_iter, gold_preproc=gold_preproc,
                                                   augment_data=None)):
            for doc, gold in epoch:
                trainer.update(doc, gold)
            dev_scores = trainer.evaluate(dev_data, gold_preproc=gold_preproc)
            print(format_str.format(itn, loss, **dev_scores.scores))


def evaluate(Language, gold_tuples, model_dir, gold_preproc=False, verbose=False,
             beam_width=None, cand_preproc=None):
    nlp = Language(path=model_dir)
    if nlp.lang == 'de':
        nlp.vocab.morphology.lemmatizer = lambda string,pos: set([string])
    if beam_width is not None:
        nlp.parser.cfg.beam_width = beam_width
    scorer = Scorer()
    for raw_text, sents in gold_tuples:
        if gold_preproc:
            raw_text = None
        else:
            sents = merge_sents(sents)
        for annot_tuples, brackets in sents:
            if raw_text is None:
                tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
                nlp.tagger(tokens)
                nlp.parser(tokens)
                nlp.entity(tokens)
            else:
                tokens = nlp(raw_text)
            gold = GoldParse.from_annot_tuples(tokens, annot_tuples)
            scorer.score(tokens, gold, verbose=verbose)
    return scorer


def write_parses(Language, dev_loc, model_dir, out_loc):
    nlp = Language(data_dir=model_dir)
    gold_tuples = read_json_file(dev_loc)
    scorer = Scorer()
    out_file = io.open(out_loc, 'w', 'utf8')
    for raw_text, sents in gold_tuples:
        sents = _merge_sents(sents)
        for annot_tuples, brackets in sents:
            if raw_text is None:
                tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
                nlp.tagger(tokens)
                nlp.entity(tokens)
                nlp.parser(tokens)
            else:
                tokens = nlp(raw_text)
            #gold = GoldParse(tokens, annot_tuples)
            #scorer.score(tokens, gold, verbose=False)
            for sent in tokens.sents:
                for t in sent:
                    if not t.is_space:
                        out_file.write(
                            '%d\t%s\t%s\t%s\t%s\n' % (t.i, t.orth_, t.tag_, t.head.orth_, t.dep_)
                        )
                out_file.write('\n')


@plac.annotations(
    language=("The language to train", "positional", None, str, ['en','de', 'zh']),
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
    pseudoprojective=("Use pseudo-projective parsing", "flag", "p", bool),
)
def main(language, train_loc, dev_loc, model_dir, n_sents=0, n_iter=15, out_loc="", verbose=False,
         debug=False, corruption_level=0.0, gold_preproc=False, eval_only=False, pseudoprojective=False):
    parser_cfg = dict(locals())
    tagger_cfg = dict(locals())
    entity_cfg = dict(locals())

    lang = spacy.util.get_lang_class(language)
    
    parser_cfg['features'] = lang.Defaults.parser_features
    entity_cfg['features'] = lang.Defaults.entity_features

    if not eval_only:
        gold_train = list(read_json_file(train_loc))
        gold_dev = list(read_json_file(dev_loc))
        train(lang, gold_train, gold_dev, model_dir, tagger_cfg, parser_cfg, entity_cfg,
              n_sents=n_sents, gold_preproc=gold_preproc, corruption_level=corruption_level,
              n_iter=n_iter)
    if out_loc:
        write_parses(lang, dev_loc, model_dir, out_loc)
    scorer = evaluate(lang, list(read_json_file(dev_loc)),
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
