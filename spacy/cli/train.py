# coding: utf8
from __future__ import unicode_literals, division, print_function

import json
from pathlib import Path

from ..scorer import Scorer
from ..tagger import Tagger
from ..syntax.parser import Parser
from ..gold import GoldParse, merge_sents
from ..gold import read_json_file as read_gold_json
from .. import util


def train(language, output_dir, train_data, dev_data, n_iter, tagger, parser, ner,
          parser_L1):
    output_path = Path(output_dir)
    train_path = Path(train_data)
    dev_path = Path(dev_data)
    check_dirs(output_path, train_path, dev_path)

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
    gold_train = list(read_gold_json(train_path))
    gold_dev = list(read_gold_json(dev_path)) if dev_path else None

    train_model(lang, gold_train, gold_dev, output_path, tagger_cfg, parser_cfg,
                entity_cfg, n_iter)
    if gold_dev:
        scorer = evaluate(lang, gold_dev, output_path)
        print_results(scorer)


def train_config(config):
    config_path = Path(config)
    if not config_path.is_file():
        util.sys_exit(config_path.as_posix(), title="Config file not found")
    config = json.load(config_path)
    for setting in []:
        if setting not in config.keys():
            util.sys_exit("{s} not found in config file.".format(s=setting),
                          title="Missing setting")


def train_model(Language, train_data, dev_data, output_path, tagger_cfg, parser_cfg,
                entity_cfg, n_iter):
    print("Itn.\tN weight\tN feats\tUAS\tNER F.\tTag %\tToken %")

    with Language.train(output_path, train_data, tagger_cfg, parser_cfg, entity_cfg) as trainer:
        loss = 0
        for itn, epoch in enumerate(trainer.epochs(n_iter, augment_data=None)):
            for doc, gold in epoch:
                trainer.update(doc, gold)
            dev_scores = trainer.evaluate(dev_data) if dev_data else []
            print_progress(itn, trainer.nlp.parser.model.nr_weight,
                           trainer.nlp.parser.model.nr_active_feat,
                           **dev_scores.scores)


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


def check_dirs(output_path, train_path, dev_path):
    if not output_path.exists():
        util.sys_exit(output_path.as_posix(), title="Output directory not found")
    if not train_path.exists():
        util.sys_exit(train_path.as_posix(), title="Training data not found")
    if dev_path and not dev_path.exists():
        util.sys_exit(dev_path.as_posix(), title="Development data not found")


def print_progress(itn, nr_weight, nr_active_feat, **scores):
    tpl = '{:d}\t{:d}\t{:d}\t{uas:.3f}\t{ents_f:.3f}\t{tags_acc:.3f}\t{token_acc:.3f}'
    print(tpl.format(itn, nr_weight, nr_active_feat, **scores))


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
