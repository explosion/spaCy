# coding: utf8
from __future__ import unicode_literals, division, print_function

import plac
import json
from collections import defaultdict
import cytoolz
from pathlib import Path
import dill
import tqdm
from thinc.neural.optimizers import linear_decay

from ..tokens.doc import Doc
from ..scorer import Scorer
from ..gold import GoldParse, merge_sents
from ..gold import GoldCorpus
from ..util import prints
from .. import util
from .. import displacy


@plac.annotations(
    lang=("model language", "positional", None, str),
    output_dir=("output directory to store model in", "positional", None, str),
    train_data=("location of JSON-formatted training data", "positional", None, str),
    dev_data=("location of JSON-formatted development data (optional)", "positional", None, str),
    n_iter=("number of iterations", "option", "n", int),
    n_sents=("number of sentences", "option", "ns", int),
    use_gpu=("Use GPU", "flag", "G", bool),
    no_tagger=("Don't train tagger", "flag", "T", bool),
    no_parser=("Don't train parser", "flag", "P", bool),
    no_entities=("Don't train NER", "flag", "N", bool)
)
def train(_, lang, output_dir, train_data, dev_data, n_iter=20, n_sents=0,
          use_gpu=False, no_tagger=False, no_parser=False, no_entities=False):
    """Train a model. Expects data in spaCy's JSON format."""
    n_sents = n_sents or None
    output_path = util.ensure_path(output_dir)
    train_path = util.ensure_path(train_data)
    dev_path = util.ensure_path(dev_data)
    if not output_path.exists():
        prints(output_path, title="Output directory not found", exits=1)
    if not train_path.exists():
        prints(train_path, title="Training data not found", exits=1)
    if dev_path and not dev_path.exists():
        prints(dev_path, title="Development data not found", exits=1)

    lang_class = util.get_lang_class(lang)

    pipeline = ['token_vectors', 'tags', 'dependencies', 'entities']
    if no_tagger and 'tags' in pipeline: pipeline.remove('tags')
    if no_parser and 'dependencies' in pipeline: pipeline.remove('dependencies')
    if no_entities and 'entities' in pipeline: pipeline.remove('entities')

    nlp = lang_class(pipeline=pipeline)
    corpus = GoldCorpus(train_path, dev_path)

    dropout = util.env_opt('dropout', 0.0)
    dropout_decay = util.env_opt('dropout_decay', 0.0)

    optimizer = nlp.begin_training(lambda: corpus.train_tuples, use_gpu=use_gpu)
    n_train_docs = corpus.count_train()
    batch_size = float(util.env_opt('min_batch_size', 4))
    max_batch_size = util.env_opt('max_batch_size', 64)
    batch_accel = util.env_opt('batch_accel', 1.001)
    print("Itn.\tDep. Loss\tUAS\tNER F.\tTag %\tToken %")
    for i in range(n_iter):
        with tqdm.tqdm(total=n_train_docs) as pbar:
            train_docs = corpus.train_docs(nlp, shuffle=i, projectivize=True)
            idx = 0
            while idx < n_train_docs:
                batch = list(cytoolz.take(int(batch_size), train_docs))
                if not batch:
                    break
                docs, golds = zip(*batch)
                nlp.update(docs, golds, drop=dropout, sgd=optimizer)
                pbar.update(len(docs))
                idx += len(docs)
                batch_size *= batch_accel
                batch_size = min(int(batch_size), max_batch_size)
                dropout = linear_decay(dropout, dropout_decay, i*n_train_docs+idx)
        with nlp.use_params(optimizer.averages):
            scorer = nlp.evaluate(corpus.dev_docs(nlp))
        print_progress(i, {}, scorer.scores)
    with (output_path / 'model.bin').open('wb') as file_:
        with nlp.use_params(optimizer.averages):
            dill.dump(nlp, file_, -1)


def _render_parses(i, to_render):
    to_render[0].user_data['title'] = "Batch %d" % i
    with Path('/tmp/entities.html').open('w') as file_:
        html = displacy.render(to_render[:5], style='ent', page=True)
        file_.write(html)
    with Path('/tmp/parses.html').open('w') as file_:
        html = displacy.render(to_render[:5], style='dep', page=True)
        file_.write(html)


def evaluate(Language, gold_tuples, path):
    with (path / 'model.bin').open('rb') as file_:
        nlp = dill.load(file_)
    # TODO:
    # 1. This code is duplicate with spacy.train.Trainer.evaluate
    # 2. There's currently a semantic difference between pipe and
    #    not pipe! It matters whether we batch the inputs. Must fix!
    all_docs = []
    all_golds = []
    for raw_text, paragraph_tuples in dev_sents:
        if gold_preproc:
            raw_text = None
        else:
            paragraph_tuples = merge_sents(paragraph_tuples)
        docs = self.make_docs(raw_text, paragraph_tuples)
        golds = self.make_golds(docs, paragraph_tuples)
        all_docs.extend(docs)
        all_golds.extend(golds)
    scorer = Scorer()
    for doc, gold in zip(self.nlp.pipe(all_docs), all_golds):
        scorer.score(doc, gold)
    return scorer


def print_progress(itn, losses, dev_scores):
    # TODO: Fix!
    scores = {}
    for col in ['dep_loss', 'tag_loss', 'uas', 'tags_acc', 'token_acc', 'ents_f']:
        scores[col] = 0.0
    scores.update(losses)
    scores.update(dev_scores)
    tpl = '{:d}\t{dep_loss:.3f}\t{tag_loss:.3f}\t{uas:.3f}\t{ents_f:.3f}\t{tags_acc:.3f}\t{token_acc:.3f}'
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
