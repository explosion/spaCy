# coding: utf8
from __future__ import unicode_literals, division, print_function

import plac
import json
from collections import defaultdict
import cytoolz
from pathlib import Path
import dill
import tqdm
from thinc.neural._classes.model import Model
from thinc.neural.optimizers import linear_decay
from timeit import default_timer as timer
import random
import numpy.random

from ..tokens.doc import Doc
from ..scorer import Scorer
from ..gold import GoldParse, merge_sents
from ..gold import GoldCorpus, minibatch
from ..util import prints
from .. import util
from .. import about
from .. import displacy
from ..compat import json_dumps

random.seed(0)
numpy.random.seed(0)


@plac.annotations(
    model=("Model name or path", "positional", None, str),
    data_path=("Location of JSON-formatted evaluation data", "positional", None, str),
    gold_preproc=("Use gold preprocessing", "flag", "G", bool),
    gpu_id=("Use GPU", "option", "g", int),
)
def evaluate(cmd, model, data_path, gpu_id=-1, gold_preproc=False):
    """
    Train a model. Expects data in spaCy's JSON format.
    """
    util.use_gpu(gpu_id)
    util.set_env_log(True)
    data_path = util.ensure_path(data_path)
    if not data_path.exists():
        prints(data_path, title="Evaluation data not found", exits=1)
    corpus = GoldCorpus(data_path, data_path)
    nlp = util.load_model(model)
    dev_docs = list(corpus.dev_docs(nlp, gold_preproc=gold_preproc))
    begin = timer()
    scorer = nlp.evaluate(dev_docs, verbose=False)
    end = timer()
    nwords = sum(len(doc_gold[0]) for doc_gold in dev_docs)
    print('Time', end-begin, 'words', nwords, 'w.p.s', nwords/(end-begin))
    print_results(scorer)


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
    scores['ner_loss'] = losses.get('ner', 0.0)
    scores['tag_loss'] = losses.get('tagger', 0.0)
    scores.update(dev_scores)
    scores['wps'] = wps
    tpl = '\t'.join((
        '{:d}',
        '{dep_loss:.3f}',
        '{ner_loss:.3f}',
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
