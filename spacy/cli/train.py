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
from timeit import default_timer as timer

from ..tokens.doc import Doc
from ..scorer import Scorer
from ..gold import GoldParse, merge_sents
from ..gold import GoldCorpus, minibatch
from ..util import prints
from .. import util
from .. import displacy
from ..compat import json_dumps


@plac.annotations(
    lang=("model language", "positional", None, str),
    output_dir=("output directory to store model in", "positional", None, str),
    train_data=("location of JSON-formatted training data", "positional", None, str),
    dev_data=("location of JSON-formatted development data (optional)", "positional", None, str),
    n_iter=("number of iterations", "option", "n", int),
    n_sents=("number of sentences", "option", "ns", int),
    use_gpu=("Use GPU", "option", "g", int),
    resume=("Whether to resume training", "flag", "R", bool),
    no_tagger=("Don't train tagger", "flag", "T", bool),
    no_parser=("Don't train parser", "flag", "P", bool),
    no_entities=("Don't train NER", "flag", "N", bool)
)
def train(cmd, lang, output_dir, train_data, dev_data, n_iter=20, n_sents=0,
          use_gpu=-1, resume=False, no_tagger=False, no_parser=False, no_entities=False):
    """
    Train a model. Expects data in spaCy's JSON format.
    """
    util.set_env_log(True)
    n_sents = n_sents or None
    output_path = util.ensure_path(output_dir)
    train_path = util.ensure_path(train_data)
    dev_path = util.ensure_path(dev_data)
    if not output_path.exists():
        output_path.mkdir()
    if not train_path.exists():
        prints(train_path, title="Training data not found", exits=1)
    if dev_path and not dev_path.exists():
        prints(dev_path, title="Development data not found", exits=1)

    lang_class = util.get_lang_class(lang)

    pipeline = ['token_vectors', 'tags', 'dependencies', 'entities']
    if no_tagger and 'tags' in pipeline: pipeline.remove('tags')
    if no_parser and 'dependencies' in pipeline: pipeline.remove('dependencies')
    if no_entities and 'entities' in pipeline: pipeline.remove('entities')

    # Take dropout and batch size as generators of values -- dropout
    # starts high and decays sharply, to force the optimizer to explore.
    # Batch size starts at 1 and grows, so that we make updates quickly
    # at the beginning of training.
    dropout_rates = util.decaying(util.env_opt('dropout_from', 0.2),
                                  util.env_opt('dropout_to', 0.2),
                                  util.env_opt('dropout_decay', 0.0))
    batch_sizes = util.compounding(util.env_opt('batch_from', 1),
                                   util.env_opt('batch_to', 64),
                                   util.env_opt('batch_compound', 1.001))

    if resume:
        prints(output_path / 'model19.pickle', title="Resuming training")
        nlp = dill.load((output_path / 'model19.pickle').open('rb'))
    else:
        nlp = lang_class(pipeline=pipeline)
    corpus = GoldCorpus(train_path, dev_path, limit=n_sents)
    n_train_words = corpus.count_train()

    optimizer = nlp.begin_training(lambda: corpus.train_tuples, device=use_gpu)

    print("Itn.\tLoss\tUAS\tNER P.\tNER R.\tNER F.\tTag %\tToken %")
    try:
        for i in range(n_iter):
            if resume:
                i += 20
            with tqdm.tqdm(total=n_train_words, leave=False) as pbar:
                train_docs = corpus.train_docs(nlp, projectivize=True,
                                               gold_preproc=False, max_length=0)
                losses = {}
                for batch in minibatch(train_docs, size=batch_sizes):
                    docs, golds = zip(*batch)
                    nlp.update(docs, golds, sgd=optimizer,
                               drop=next(dropout_rates), losses=losses)
                    pbar.update(sum(len(doc) for doc in docs))

            with nlp.use_params(optimizer.averages):
                util.set_env_log(False)
                epoch_model_path = output_path / ('model%d' % i)
                nlp.to_disk(epoch_model_path)
                with (output_path / ('model%d.pickle' % i)).open('wb') as file_:
                    dill.dump(nlp, file_, -1)
                nlp_loaded = lang_class(pipeline=pipeline)
                nlp_loaded = nlp_loaded.from_disk(epoch_model_path)
                scorer = nlp_loaded.evaluate(
                            corpus.dev_docs(
                                nlp_loaded,
                                gold_preproc=False))
                acc_loc =(output_path / ('model%d' % i) / 'accuracy.json')
                with acc_loc.open('w') as file_:
                    file_.write(json_dumps(scorer.scores))
                util.set_env_log(True)
            print_progress(i, losses, scorer.scores)
    finally:
        print("Saving model...")
        with (output_path / 'model-final.pickle').open('wb') as file_:
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


def print_progress(itn, losses, dev_scores, wps=0.0):
    scores = {}
    for col in ['dep_loss', 'tag_loss', 'uas', 'tags_acc', 'token_acc',
                'ents_p', 'ents_r', 'ents_f', 'wps']:
        scores[col] = 0.0
    scores['dep_loss'] = losses.get('parser', 0.0)
    scores['tag_loss'] = losses.get('tagger', 0.0)
    scores.update(dev_scores)
    scores['wps'] = wps
    tpl = '\t'.join((
        '{:d}',
        '{dep_loss:.3f}',
        '{uas:.3f}',
        '{ents_p:.3f}',
        '{ents_r:.3f}',
        '{ents_f:.3f}',
        '{tags_acc:.3f}',
        '{token_acc:.3f}',
        '{wps:.1f}'))
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
