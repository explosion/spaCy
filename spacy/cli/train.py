# coding: utf8
from __future__ import unicode_literals, division, print_function

import plac
from pathlib import Path
import tqdm
from thinc.neural._classes.model import Model
from timeit import default_timer as timer
import json
import shutil

from ._messages import Messages
from ..attrs import PROB, IS_OOV, CLUSTER, LANG
from ..gold import GoldCorpus
from ..util import prints, minibatch, minibatch_by_words
from .. import util
from .. import about
from .. import displacy
from ..compat import json_dumps


@plac.annotations(
    lang=("model language", "positional", None, str),
    output_dir=("output directory to store model in", "positional", None, str),
    train_data=("location of JSON-formatted training data", "positional",
                None, str),
    dev_data=("location of JSON-formatted development data (optional)",
              "positional", None, str),
    n_iter=("number of iterations", "option", "n", int),
    n_sents=("number of sentences", "option", "ns", int),
    use_gpu=("Use GPU", "option", "g", int),
    vectors=("Model to load vectors from", "option", "v"),
    no_tagger=("Don't train tagger", "flag", "T", bool),
    no_parser=("Don't train parser", "flag", "P", bool),
    no_entities=("Don't train NER", "flag", "N", bool),
    parser_multitasks=("Side objectives for parser CNN, e.g. dep dep,tag", "option", "pt", str),
    noise_level=("Amount of corruption to add for data augmentation", "option", "nl", float),
    entity_multitasks=("Side objectives for ner CNN, e.g. dep dep,tag", "option", "et", str),
    gold_preproc=("Use gold preprocessing", "flag", "G", bool),
    version=("Model version", "option", "V", str),
    meta_path=("Optional path to meta.json. All relevant properties will be "
               "overwritten.", "option", "m", Path),
    init_tok2vec=("Path to pretrained weights for the token-to-vector parts "
        "of the models. See 'spacy pretrain'. Experimental.", "option", "t2v", Path),
    verbose=("Display more information for debug", "option", None, bool))
def train(lang, output_dir, train_data, dev_data, n_iter=30, n_sents=0,
         parser_multitasks='', entity_multitasks='', init_tok2vec=None,
          use_gpu=-1, vectors=None, no_tagger=False, noise_level=0.0,
          no_parser=False, no_entities=False, gold_preproc=False,
          version="0.0.0", meta_path=None, verbose=False):
    """
    Train a model. Expects data in spaCy's JSON format.
    """
    util.fix_random_seed()
    util.set_env_log(True)
    n_sents = n_sents or None
    output_path = util.ensure_path(output_dir)
    train_path = util.ensure_path(train_data)
    dev_path = util.ensure_path(dev_data)
    meta_path = util.ensure_path(meta_path)
    if not train_path.exists():
        prints(train_path, title=Messages.M050, exits=1)
    if dev_path and not dev_path.exists():
        prints(dev_path, title=Messages.M051, exits=1)
    if meta_path is not None and not meta_path.exists():
        prints(meta_path, title=Messages.M020, exits=1)
    meta = util.read_json(meta_path) if meta_path else {}
    if not isinstance(meta, dict):
        prints(Messages.M053.format(meta_type=type(meta)),
               title=Messages.M052, exits=1)
    meta.setdefault('lang', lang)
    meta.setdefault('name', 'unnamed')
    
    if not output_path.exists():
        output_path.mkdir()

    print("Counting training words (limit=%s" % n_sents)
    corpus = GoldCorpus(train_path, dev_path, limit=n_sents)
    n_train_words = corpus.count_train()
    print(n_train_words)
    pipeline = ['tagger', 'parser', 'ner']
    if no_tagger and 'tagger' in pipeline:
        pipeline.remove('tagger')
    if no_parser and 'parser' in pipeline:
        pipeline.remove('parser')
    if no_entities and 'ner' in pipeline:
        pipeline.remove('ner')

    # Take dropout and batch size as generators of values -- dropout
    # starts high and decays sharply, to force the optimizer to explore.
    # Batch size starts at 1 and grows, so that we make updates quickly
    # at the beginning of training.
    dropout_rates = util.decaying(util.env_opt('dropout_from', 0.2),
                                  util.env_opt('dropout_to', 0.2),
                                  util.env_opt('dropout_decay', 0.0))
    batch_sizes = util.compounding(util.env_opt('batch_from', 1000),
                                   util.env_opt('batch_to', 1000),
                                   util.env_opt('batch_compound', 1.001))
    lang_class = util.get_lang_class(lang)
    nlp = lang_class()
    meta['pipeline'] = pipeline
    nlp.meta.update(meta)
    if vectors:
        print("Load vectors model", vectors)
        util.load_model(vectors, vocab=nlp.vocab)
        for lex in nlp.vocab:
            values = {}
            for attr, func in nlp.vocab.lex_attr_getters.items():
                # These attrs are expected to be set by data. Others should
                # be set by calling the language functions.
                if attr not in (CLUSTER, PROB, IS_OOV, LANG):
                    values[lex.vocab.strings[attr]] = func(lex.orth_)
            lex.set_attrs(**values)
            lex.is_oov = False
    for name in pipeline:
        nlp.add_pipe(nlp.create_pipe(name), name=name)
    nlp.add_pipe(nlp.create_pipe('merge_subtokens'))
    if parser_multitasks:
        for objective in parser_multitasks.split(','):
            nlp.parser.add_multitask_objective(objective)
    if entity_multitasks:
        for objective in entity_multitasks.split(','):
            nlp.entity.add_multitask_objective(objective)
    optimizer = nlp.begin_training(lambda: corpus.train_tuples, device=use_gpu)
    if init_tok2vec is not None:
        loaded = _load_pretrained_tok2vec(nlp, init_tok2vec)
        print("Loaded pretrained tok2vec for:", loaded)
    nlp._optimizer = None

    print("Itn.  Dep Loss  NER Loss  UAS     NER P.  NER R.  NER F.  Tag %   Token %  CPU WPS  GPU WPS")
    try:
        for i in range(n_iter):
            train_docs = corpus.train_docs(nlp, noise_level=noise_level,
                                           gold_preproc=gold_preproc, max_length=0)
            words_seen = 0
            with tqdm.tqdm(total=n_train_words, leave=False) as pbar:
                losses = {}
                for batch in minibatch_by_words(train_docs, size=batch_sizes):
                    if not batch:
                        continue
                    docs, golds = zip(*batch)
                    nlp.update(docs, golds, sgd=optimizer,
                               drop=next(dropout_rates), losses=losses)
                    pbar.update(sum(len(doc) for doc in docs))
                    words_seen += sum(len(doc) for doc in docs)
            with nlp.use_params(optimizer.averages):
                util.set_env_log(False)
                epoch_model_path = output_path / ('model%d' % i)
                nlp.to_disk(epoch_model_path)
                nlp_loaded = util.load_model_from_path(epoch_model_path)
                dev_docs = list(corpus.dev_docs(
                                nlp_loaded,
                                gold_preproc=gold_preproc))
                nwords = sum(len(doc_gold[0]) for doc_gold in dev_docs)
                start_time = timer()
                scorer = nlp_loaded.evaluate(dev_docs, verbose)
                end_time = timer()
                if use_gpu < 0:
                    gpu_wps = None
                    cpu_wps = nwords/(end_time-start_time)
                else:
                    gpu_wps = nwords/(end_time-start_time)
                    with Model.use_device('cpu'):
                        nlp_loaded = util.load_model_from_path(epoch_model_path)
                        dev_docs = list(corpus.dev_docs(
                                        nlp_loaded, gold_preproc=gold_preproc))
                        start_time = timer()
                        scorer = nlp_loaded.evaluate(dev_docs)
                        end_time = timer()
                        cpu_wps = nwords/(end_time-start_time)
                acc_loc = (output_path / ('model%d' % i) / 'accuracy.json')
                with acc_loc.open('w') as file_:
                    file_.write(json_dumps(scorer.scores))
                meta_loc = output_path / ('model%d' % i) / 'meta.json'
                meta['accuracy'] = scorer.scores
                meta['speed'] = {'nwords': nwords, 'cpu': cpu_wps,
                                 'gpu': gpu_wps}
                meta['vectors'] = {'width': nlp.vocab.vectors_length,
                                   'vectors': len(nlp.vocab.vectors),
                                   'keys': nlp.vocab.vectors.n_keys}
                meta['lang'] = nlp.lang
                meta['pipeline'] = pipeline
                meta['spacy_version'] = '>=%s' % about.__version__
                meta.setdefault('name', 'model%d' % i)
                meta.setdefault('version', version)

                with meta_loc.open('w') as file_:
                    file_.write(json_dumps(meta))
                util.set_env_log(True)
            print_progress(i, losses, scorer.scores, cpu_wps=cpu_wps,
                           gpu_wps=gpu_wps)
    finally:
        print("Saving model...")
        with nlp.use_params(optimizer.averages):
            final_model_path = output_path / 'model-final'
            nlp.to_disk(final_model_path)
    components = []
    if not no_parser:
        components.append('parser')
    if not no_tagger:
        components.append('tagger')
    if not no_entities:
        components.append('ner')
    _collate_best_model(meta, output_path, components)


def _load_pretrained_tok2vec(nlp, loc):
    """Load pre-trained weights for the 'token-to-vector' part of the component
    models, which is typically a CNN. See 'spacy pretrain'. Experimental.
    """
    with loc.open('rb') as file_:
        weights_data = file_.read()
    loaded = []
    for name, component in nlp.pipeline:
        if hasattr(component, 'model') and hasattr(component.model, 'tok2vec'):
            component.tok2vec.from_bytes(weights_data)
            loaded.append(name)
    return loaded


def _collate_best_model(meta, output_path, components):
    bests = {}
    for component in components:
        bests[component] = _find_best(output_path, component)
    best_dest = output_path / 'model-best'
    shutil.copytree(output_path / 'model-final', best_dest)
    for component, best_component_src in bests.items():
        shutil.rmtree(best_dest / component)
        shutil.copytree(best_component_src / component, best_dest / component)
        with (best_component_src / 'accuracy.json').open() as file_:
            accs = json.load(file_)
        for metric in _get_metrics(component):
            meta['accuracy'][metric] = accs[metric]
    with (best_dest / 'meta.json').open('w') as file_:
        file_.write(json_dumps(meta))


def _find_best(experiment_dir, component):
    accuracies = []
    for epoch_model in experiment_dir.iterdir():
        if epoch_model.is_dir() and epoch_model.parts[-1] != "model-final":
            accs = json.load((epoch_model / "accuracy.json").open())
            scores = [accs.get(metric, 0.0) for metric in _get_metrics(component)]
            accuracies.append((scores, epoch_model))
    if accuracies:
        return max(accuracies)[1]
    else:
        return None

def _get_metrics(component):
    if component == "parser":
        return ("las", "uas", "token_acc")
    elif component == "tagger":
        return ("tags_acc",)
    elif component == "ner":
        return ("ents_f", "ents_p", "ents_r")
    return ("token_acc",)


def _render_parses(i, to_render):
    to_render[0].user_data['title'] = "Batch %d" % i
    with Path('/tmp/entities.html').open('w') as file_:
        html = displacy.render(to_render[:5], style='ent', page=True)
        file_.write(html)
    with Path('/tmp/parses.html').open('w') as file_:
        html = displacy.render(to_render[:5], style='dep', page=True)
        file_.write(html)


def print_progress(itn, losses, dev_scores, cpu_wps=0.0, gpu_wps=0.0):
    scores = {}
    for col in ['dep_loss', 'tag_loss', 'uas', 'tags_acc', 'token_acc',
                'ents_p', 'ents_r', 'ents_f', 'cpu_wps', 'gpu_wps']:
        scores[col] = 0.0
    scores['dep_loss'] = losses.get('parser', 0.0)
    scores['ner_loss'] = losses.get('ner', 0.0)
    scores['tag_loss'] = losses.get('tagger', 0.0)
    scores.update(dev_scores)
    scores['cpu_wps'] = cpu_wps
    scores['gpu_wps'] = gpu_wps or 0.0
    tpl = ''.join((
        '{:<6d}',
        '{dep_loss:<10.3f}',
        '{ner_loss:<10.3f}',
        '{uas:<8.3f}',
        '{ents_p:<8.3f}',
        '{ents_r:<8.3f}',
        '{ents_f:<8.3f}',
        '{tags_acc:<8.3f}',
        '{token_acc:<9.3f}',
        '{cpu_wps:<9.1f}',
        '{gpu_wps:.1f}',
    ))
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
