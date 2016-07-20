#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
from os import path
import shutil
import io
import random
import time
import gzip
import re
import numpy

import plac
import cProfile
import pstats

import spacy.util
from spacy.en import English
from spacy.gold import GoldParse

from spacy.syntax.util import Config
from spacy.syntax.arc_eager import ArcEager
from spacy.syntax.parser import Parser, get_templates
from spacy.syntax.beam_parser import BeamParser
from spacy.scorer import Scorer
from spacy.tagger import Tagger
from spacy.syntax.nonproj import PseudoProjectivity
from spacy.syntax import _parse_features as pf

# Last updated for spaCy v0.97


def read_conll(file_, n=0):
    """Read a standard CoNLL/MALT-style format"""
    text = file_.read().strip()
    sent_strs = re.split(r'\n\s*\n', text)
    for sent_id, sent_str in enumerate(sent_strs):
        if not sent_str.strip():
            continue
        ids = []
        words = []
        heads = []
        labels = []
        tags = []
        for i, line in enumerate(sent_str.strip().split('\n')):
            word, pos_string, head_idx, label = _parse_line(line)
            words.append(word)
            if head_idx < 0:
                head_idx = i
            ids.append(i)
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
        annot = (ids, words, tags, heads, labels, ['O'] * len(ids))
        yield (None, [(annot, None)])
        if n and sent_id >= n:
            break


def _parse_line(line):
    pieces = line.split()
    if len(pieces) == 4:
        word, pos, head_idx, label = pieces
        head_idx = int(head_idx)
    elif len(pieces) == 15:
        id_ = int(pieces[0].split('_')[-1])
        word = pieces[1]
        pos = pieces[4]
        head_idx = int(pieces[8])-1
        label = pieces[10]
    else:
        id_ = int(pieces[0].split('_')[-1])
        word = pieces[1]
        pos = pieces[4]
        head_idx = int(pieces[6])-1
        label = pieces[7]
    if head_idx < 0:
        label = 'ROOT'
    return word, pos, head_idx, label


def print_words(strings, words, embeddings):
    ids = {strings[word]: word for word in words}
    vectors = {}
    for key, values in embeddings[5]:
        if key in ids:
            vectors[strings[key]] = values
    for word in words:
        if word in vectors:
            print(word, vectors[word])

        
def score_model(scorer, nlp, raw_text, annot_tuples, verbose=False):
    tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
    nlp.tagger.tag_from_strings(tokens, annot_tuples[2])
    nlp.parser(tokens)
    gold = GoldParse(tokens, annot_tuples, make_projective=False)
    scorer.score(tokens, gold, verbose=verbose, punct_labels=('--', 'p', 'punct'))


def train(Language, gold_tuples, model_dir, dev_loc, n_iter=15, feat_set=u'basic',
          learn_rate=0.001, update_step='sgd_cm', 
          batch_norm=False, seed=0, gold_preproc=False, force_gold=False):
    dep_model_dir = path.join(model_dir, 'deps')
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(dep_model_dir):
        shutil.rmtree(dep_model_dir)
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(dep_model_dir)
    os.mkdir(pos_model_dir)

    if feat_set != 'neural':
        Config.write(dep_model_dir, 'config', features=feat_set, seed=seed,
            labels=ArcEager.get_labels(gold_tuples))

    else:
        feat_groups = [
            (pf.core_words, 8),
            (pf.core_tags, 4),
            (pf.core_labels, 4),
            (pf.core_shapes, 4),
            ([f[0] for f in pf.valencies], 2)
        ]
        slots = []
        vector_widths = []
        feat_set = []
        input_length = 0
        for i, (feat_group, width) in enumerate(feat_groups):
            feat_set.extend((f,) for f in feat_group)
            slots += [i] * len(feat_group)
            vector_widths.append(width)
            input_length += width * len(feat_group)
        hidden_layers = [128] * 5
        rho = 1e-4
        Config.write(dep_model_dir, 'config',
                     model='neural',
                     seed=seed,
                     labels=ArcEager.get_labels(gold_tuples),
                     feat_set=feat_set,
                     vector_widths=vector_widths,
                     slots=slots,
                     hidden_layers=hidden_layers,
                     update_step=update_step,
                     batch_norm=batch_norm,
                     eta=learn_rate,
                     mu=0.9,
                     ensemble_size=1,
                     rho=rho)

    nlp = Language(data_dir=model_dir, tagger=False, parser=False, entity=False)
    nlp.tagger = Tagger.blank(nlp.vocab, Tagger.default_templates())
    nlp.parser = Parser.from_dir(dep_model_dir, nlp.vocab.strings, ArcEager)
    for word in nlp.vocab:
        word.norm = word.orth
    words = list(nlp.vocab)
    top5k = numpy.ndarray(shape=(10000, len(word.vector)), dtype='float32')
    norms = numpy.ndarray(shape=(10000,), dtype='float32')
    for i in range(10000):
        if i >= 400 and words[i].has_vector:
            top5k[i] = words[i].vector
            norms[i] = numpy.sqrt(sum(top5k[i] ** 2))
        else:
            # Make these way off values, to make big distance.
            top5k[i] = 100.0
            norms[i] = 100.0
    print("Setting vectors")
    for word in words[10000:]:
        if word.has_vector:
            cosines = numpy.dot(top5k, word.vector)
            cosines /= norms * numpy.sqrt(sum(word.vector ** 2))
            most_similar = words[numpy.argmax(cosines)]
            word.norm = most_similar.norm
        else:
            word.norm = word.shape
    
    print(nlp.parser.model.widths)
 
    print("Itn.\tP.Loss\tPruned\tTrain\tDev\tSize")
    last_score = 0.0
    nr_trimmed = 0
    eg_seen = 0
    loss = 0
    for itn in range(n_iter):
        random.shuffle(gold_tuples)
        for _, sents in gold_tuples:
            for annot_tuples, _ in sents:
                tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
                nlp.tagger.tag_from_strings(tokens, annot_tuples[2])
                gold = GoldParse(tokens, annot_tuples)
                loss += nlp.parser.train(tokens, gold)
                eg_seen += 1
                if eg_seen % 10000 == 0:
                    scorer = Scorer()
                    with io.open(dev_loc, 'r', encoding='utf8') as file_:
                        for _, sents in read_conll(file_):
                            for annot_tuples, _ in sents:
                                score_model(scorer, nlp, None, annot_tuples)
                    train_scorer = Scorer()
                    for _, sents in gold_tuples[:1000]:
                        for annot_tuples, _ in sents:
                            score_model(train_scorer, nlp, None, annot_tuples)
                    print('%d:\t%d\t%.3f\t%.3f\t%.3f\t%d' % (itn, int(loss), nr_trimmed,
                                                             train_scorer.uas, scorer.uas,
                                                             nlp.parser.model.mem.size))
                    loss = 0
        if feat_set != 'basic':
            nlp.parser.model.eta *= 0.99
            threshold = 0.05 * (1.05 ** itn)
            nr_trimmed = nlp.parser.model.sparsify_embeddings(threshold, True) 
    nlp.end_training(model_dir)
    return nlp


@plac.annotations(
    train_loc=("Location of CoNLL 09 formatted training file"),
    dev_loc=("Location of CoNLL 09 formatted development file"),
    model_dir=("Location of output model directory"),
    n_iter=("Number of training iterations", "option", "i", int),
    batch_norm=("Use batch normalization and residual connections", "flag", "b"),
    update_step=("Update step", "option", "u", str),
    learn_rate=("Learn rate", "option", "e", float),
    neural=("Use neural network?", "flag", "N")
)
def main(train_loc, dev_loc, model_dir, n_iter=15, neural=False, batch_norm=False,
         learn_rate=0.001, update_step='sgd_cm'):
    with io.open(train_loc, 'r', encoding='utf8') as file_:
        train_sents = list(read_conll(file_))
    # preprocess training data here before ArcEager.get_labels() is called
    train_sents = PseudoProjectivity.preprocess_training_data(train_sents)

    nlp = train(English, train_sents, model_dir, dev_loc, n_iter=n_iter,
                feat_set='neural' if neural else 'basic',
                batch_norm=batch_norm,
                learn_rate=learn_rate,
                update_step=update_step)
    scorer = Scorer()
    with io.open(dev_loc, 'r', encoding='utf8') as file_:
        for _, sents in read_conll(file_):
            for annot_tuples, _ in sents:
                score_model(scorer, nlp, None, annot_tuples)
    print('TOK', scorer.token_acc)
    print('POS', scorer.tags_acc)
    print('UAS', scorer.uas)
    print('LAS', scorer.las)



if __name__ == '__main__':
    plac.call(main)
