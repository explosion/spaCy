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
          use_orig_arc_eager=False, pseudoprojective=False):
    dep_model_dir = path.join(model_dir, 'deps')
    ner_model_dir = path.join(model_dir, 'ner')
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(dep_model_dir):
        shutil.rmtree(dep_model_dir)
    if path.exists(ner_model_dir):
        shutil.rmtree(ner_model_dir)
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(dep_model_dir)
    os.mkdir(ner_model_dir)
    os.mkdir(pos_model_dir)

    if pseudoprojective:
        # preprocess training data here before ArcEager.get_labels() is called
        gold_tuples = PseudoProjectivity.preprocess_training_data(gold_tuples)

    Config.write(dep_model_dir, 'config', features=feat_set, seed=seed,
                 labels=ArcEager.get_labels(gold_tuples),
                 beam_width=beam_width,projectivize=pseudoprojective)
    Config.write(ner_model_dir, 'config', features='ner', seed=seed,
                 labels=BiluoPushDown.get_labels(gold_tuples),
                 beam_width=0)

    if n_sents > 0:
        gold_tuples = gold_tuples[:n_sents]

    nlp = Language(data_dir=model_dir, tagger=False, parser=False, entity=False)
    nlp.tagger = Tagger.blank(nlp.vocab, Tagger.default_templates())
    nlp.parser = Parser.from_dir(dep_model_dir, nlp.vocab.strings, ArcEager)
    nlp.entity = Parser.from_dir(ner_model_dir, nlp.vocab.strings, BiluoPushDown)
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
                if len(annot_tuples[1]) == 1:
                    continue
                score_model(scorer, nlp, raw_text, annot_tuples,
                            verbose=verbose if itn >= 2 else False)
                if raw_text is None:
                    words = add_noise(annot_tuples[1], corruption_level)
                    tokens = nlp.tokenizer.tokens_from_list(words)
                else:
                    raw_text = add_noise(raw_text, corruption_level)
                    tokens = nlp.tokenizer(raw_text)
                nlp.tagger(tokens)
                gold = GoldParse(tokens, annot_tuples)
                if not gold.is_projective:
                    raise Exception("Non-projective sentence in training: %s" % annot_tuples[1])
                loss += nlp.parser.train(tokens, gold)
                nlp.entity.train(tokens, gold)
                nlp.tagger.train(tokens, gold.tags)
        random.shuffle(gold_tuples)
        print('%d:\t%d\t%.3f\t%.3f\t%.3f\t%.3f' % (itn, loss, scorer.uas, scorer.ents_f,
                                                   scorer.tags_acc,
                                                   scorer.token_acc))
    print('end training')
    nlp.end_training(model_dir)
    print('done')


def evaluate(Language, gold_tuples, model_dir, gold_preproc=False, verbose=False,
             beam_width=None, cand_preproc=None):
    nlp = Language(data_dir=model_dir)
    if nlp.lang == 'de':
        nlp.vocab.morphology.lemmatizer = lambda string,pos: set([string])
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
                nlp.parser(tokens)
                nlp.entity(tokens)
            else:
                tokens = nlp(raw_text)
            gold = GoldParse(tokens, annot_tuples)
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
    lang = spacy.util.get_lang_class(language)

    if not eval_only:
        gold_train = list(read_json_file(train_loc))
        train(lang, gold_train, model_dir,
              feat_set='basic' if not debug else 'debug',
              gold_preproc=gold_preproc, n_sents=n_sents,
              corruption_level=corruption_level, n_iter=n_iter,
              verbose=verbose,pseudoprojective=pseudoprojective)
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
