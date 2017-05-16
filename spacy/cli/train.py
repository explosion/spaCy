# coding: utf8
from __future__ import unicode_literals, division, print_function

import json
from collections import defaultdict
import cytoolz

from ..scorer import Scorer
from ..gold import GoldParse, merge_sents
from ..gold import read_json_file as read_gold_json
from ..util import prints
from .. import util


def train(language, output_dir, train_data, dev_data, n_iter, tagger, parser, ner,
          parser_L1):
    output_path = util.ensure_path(output_dir)
    train_path = util.ensure_path(train_data)
    dev_path = util.ensure_path(dev_data)
    if not output_path.exists():
        prints(output_path, title="Output directory not found", exits=True)
    if not train_path.exists():
        prints(train_path, title="Training data not found", exits=True)
    if dev_path and not dev_path.exists():
        prints(dev_path, title="Development data not found", exits=True)

    lang = util.get_lang_class(language)
    parser_cfg = {
        'pseudoprojective': True,
        'L1': parser_L1,
        'n_iter': n_iter,
        'lang': language,
        'features': lang.Defaults.parser_features}
    entity_cfg = {
        'n_iter': n_iter,
        'lang': language,
        'features': lang.Defaults.entity_features}
    tagger_cfg = {
        'n_iter': n_iter,
        'lang': language,
        'features': lang.Defaults.tagger_features}
    gold_train = list(read_gold_json(train_path))[:100]
    gold_dev = list(read_gold_json(dev_path)) if dev_path else None

    gold_dev = gold_dev[:100]

    train_model(lang, gold_train, gold_dev, output_path, n_iter)
    if gold_dev:
        scorer = evaluate(lang, gold_dev, output_path)
        print_results(scorer)


def train_config(config):
    config_path = util.ensure_path(config)
    if not config_path.is_file():
        prints(config_path, title="Config file not found", exits=True)
    config = json.load(config_path)
    for setting in []:
        if setting not in config.keys():
            prints("%s not found in config file." % setting, title="Missing setting")


def train_model(Language, train_data, dev_data, output_path, n_iter, **cfg):
    print("Itn.\tDep. Loss\tUAS\tNER F.\tTag %\tToken %")

    nlp = Language(pipeline=['token_vectors', 'tags', 'dependencies', 'entities'])

    # TODO: Get spaCy using Thinc's trainer and optimizer
    with nlp.begin_training(train_data, **cfg) as (trainer, optimizer):
        for itn, epoch in enumerate(trainer.epochs(n_iter)):
            losses = defaultdict(float)
            for docs, golds in epoch:
                state = nlp.update(docs, golds, drop=0., sgd=optimizer)
                losses['dep_loss'] += state.get('parser_loss', 0.0)
            if dev_data:
                dev_scores = trainer.evaluate(dev_data).scores
            else:
                dev_scores = defaultdict(float)
            print_progress(itn, losses, dev_scores)


def evaluate(Language, gold_tuples, output_path):
    print("Load parser", output_path)
    nlp = Language(path=output_path)
    scorer = Scorer()
    for raw_text, sents in gold_tuples:
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
            scorer.score(tokens, gold)
    return scorer


def print_progress(itn, losses, dev_scores):
    # TODO: Fix!
    scores = {}
    for col in ['dep_loss', 'uas', 'tags_acc', 'token_acc', 'ents_f']:
        scores[col] = 0.0
    scores.update(losses)
    scores.update(dev_scores)
    tpl = '{:d}\t{dep_loss:.3f}\t{uas:.3f}\t{ents_f:.3f}\t{tags_acc:.3f}\t{token_acc:.3f}'
    print(tpl.format(itn, **scores))


def print_results(scorer):
    results = {
        'TOK': '%.2f' % scorer.token_acc,
        'POS': '%.2f' % scorer.tags_acc,
        'UAS': '%.2f' % scorer.uas,
        'LAS': '%.2f' % scorer.las,
        'NER P': '%.2f' % scorer.ents_p,
        'NER R': '%.2f' % scorer.ents_r,
        'NER F': '%.2f' % scorer.ents_f}
    util.print_table(results, title="Results")
