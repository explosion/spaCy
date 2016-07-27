#!/usr/bin/env python
from __future__ import division
from __future__ import unicode_literals

import os
from os import path
import shutil
import codecs
import random

import plac
import cProfile
import pstats
import re

import spacy.util
from spacy.en import English
from spacy.en.pos import POS_TEMPLATES, POS_TAGS, setup_model_dir

from spacy.syntax.util import Config
from spacy.gold import read_json_file
from spacy.gold import GoldParse

from spacy.scorer import Scorer

from spacy.syntax.parser import Parser, get_templates
from spacy._theano import TheanoModel

import theano
import theano.tensor as T

from theano.printing import Print

import numpy
from collections import OrderedDict, defaultdict


theano.config.profile = False
theano.config.floatX = 'float32'
floatX = theano.config.floatX


def L1(L1_reg, *weights):
    return L1_reg * sum(abs(w).sum() for w in weights)


def L2(L2_reg, *weights):
    return L2_reg * sum((w ** 2).sum() for w in weights)


def rms_prop(loss, params, eta=1.0, rho=0.9, eps=1e-6):
    updates = OrderedDict()
    for param in params:
        value = param.get_value(borrow=True)
        accu = theano.shared(np.zeros(value.shape, dtype=value.dtype),
                             broadcastable=param.broadcastable)

        grad = T.grad(loss, param)
        accu_new = rho * accu + (1 - rho) * grad ** 2
        updates[accu] = accu_new
        updates[param] = param - (eta * grad / T.sqrt(accu_new + eps))
    return updates


def relu(x):
    return x * (x > 0)


def feed_layer(activation, weights, bias, input_):
    return activation(T.dot(input_, weights) + bias)


def init_weights(n_in, n_out):
    rng = numpy.random.RandomState(1235)
    
    weights = numpy.asarray(
        rng.standard_normal(size=(n_in, n_out)) * numpy.sqrt(2.0 / n_in),
        dtype=theano.config.floatX
    )
    bias = numpy.zeros((n_out,), dtype=theano.config.floatX)
    return [wrapper(weights, name='W'), wrapper(bias, name='b')]


def compile_model(n_classes, n_hidden, n_in, optimizer):
    x = T.vector('x') 
    costs = T.ivector('costs')
    loss = T.scalar('loss')

    maxent_W, maxent_b = init_weights(n_hidden, n_classes)
    hidden_W, hidden_b = init_weights(n_in, n_hidden)

    # Feed the inputs forward through the network
    p_y_given_x = feed_layer(
                    T.nnet.softmax,
                    maxent_W,
                    maxent_b,
                      feed_layer(
                        relu,
                        hidden_W,
                        hidden_b,
                        x))

    loss = -T.log(T.sum(p_y_given_x[0] * T.eq(costs, 0)) + 1e-8)

    train_model = theano.function(
        name='train_model',
        inputs=[x, costs],
        outputs=[p_y_given_x[0], T.grad(loss, x), loss],
        updates=optimizer(loss, [maxent_W, maxent_b, hidden_W, hidden_b]),
        on_unused_input='warn'
    )

    evaluate_model = theano.function(
        name='evaluate_model',
        inputs=[x],
        outputs=[
            feed_layer(
              T.nnet.softmax,
              maxent_W,
              maxent_b,
              feed_layer(
                relu,
                hidden_W,
                hidden_b,
                x
              )
            )[0]
        ]
    )
    return train_model, evaluate_model


def score_model(scorer, nlp, annot_tuples, verbose=False):
    tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
    nlp.tagger(tokens)
    nlp.parser(tokens)
    gold = GoldParse(tokens, annot_tuples)
    scorer.score(tokens, gold, verbose=verbose)


def train(Language, gold_tuples, model_dir, n_iter=15, feat_set=u'basic',
          eta=0.01, mu=0.9, nv_hidden=100, nv_word=10, nv_tag=10, nv_label=10,
          seed=0, n_sents=0,  verbose=False):

    dep_model_dir = path.join(model_dir, 'deps')
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(dep_model_dir):
        shutil.rmtree(dep_model_dir)
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(dep_model_dir)
    os.mkdir(pos_model_dir)
    setup_model_dir(sorted(POS_TAGS.keys()), POS_TAGS, POS_TEMPLATES, pos_model_dir)

    Config.write(dep_model_dir, 'config',
        seed=seed,
        templates=tuple(),
        labels=Language.ParserTransitionSystem.get_labels(gold_tuples),
        vector_lengths=(nv_word, nv_tag, nv_label),
        hidden_nodes=nv_hidden,
        eta=eta,
        mu=mu
    )
  
    # Bake-in hyper-parameters
    optimizer = lambda loss, params: rms_prop(loss, params, eta=eta, rho=rho, eps=eps)
    nlp = Language(data_dir=model_dir)
    n_classes = nlp.parser.model.n_classes
    train, predict = compile_model(n_classes, nv_hidden, n_in, optimizer)
    nlp.parser.model = TheanoModel(n_classes, input_spec, train,
                                   predict, model_loc)
 
    if n_sents > 0:
        gold_tuples = gold_tuples[:n_sents]
    print "Itn.\tP.Loss\tUAS\tTag %\tToken %"
    log_loc = path.join(model_dir, 'job.log')
    for itn in range(n_iter):
        scorer = Scorer()
        loss = 0
        for _, sents in gold_tuples:
            for annot_tuples, ctnt in sents:
                if len(annot_tuples[1]) == 1:
                    continue
                score_model(scorer, nlp, annot_tuples)
                tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
                nlp.tagger(tokens)
                gold = GoldParse(tokens, annot_tuples, make_projective=True)
                assert gold.is_projective
                loss += nlp.parser.train(tokens, gold)
                nlp.tagger.train(tokens, gold.tags)
        random.shuffle(gold_tuples)
        logline = '%d:\t%d\t%.3f\t%.3f\t%.3f' % (itn, loss, scorer.uas,
                                                 scorer.tags_acc,
                                                 scorer.token_acc)
        print logline
        with open(log_loc, 'aw') as file_:
            file_.write(logline + '\n')
    nlp.parser.model.end_training()
    nlp.tagger.model.end_training()
    nlp.vocab.strings.dump(path.join(model_dir, 'vocab', 'strings.txt'))
    return nlp


def evaluate(nlp, gold_tuples, gold_preproc=True):
    scorer = Scorer()
    for raw_text, sents in gold_tuples:
        for annot_tuples, brackets in sents:
            tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
            nlp.tagger(tokens)
            nlp.parser(tokens)
            gold = GoldParse(tokens, annot_tuples)
            scorer.score(tokens, gold)
    return scorer


@plac.annotations(
    train_loc=("Location of training file or directory"),
    dev_loc=("Location of development file or directory"),
    model_dir=("Location of output model directory",),
    eval_only=("Skip training, and only evaluate", "flag", "e", bool),
    n_sents=("Number of training sentences", "option", "n", int),
    n_iter=("Number of training iterations", "option", "i", int),
    verbose=("Verbose error reporting", "flag", "v", bool),

    nv_word=("Word vector length", "option", "W", int),
    nv_tag=("Tag vector length", "option", "T", int),
    nv_label=("Label vector length", "option", "L", int),
    nv_hidden=("Hidden nodes length", "option", "H", int),
    eta=("Learning rate", "option", "E", float),
    mu=("Momentum", "option", "M", float),
)
def main(train_loc, dev_loc, model_dir, n_sents=0, n_iter=15, verbose=False,
         nv_word=10, nv_tag=10, nv_label=10, nv_hidden=10,
         eta=0.1, mu=0.9, eval_only=False):




    gold_train = list(read_json_file(train_loc, lambda doc: 'wsj' in doc['id']))

    nlp = train(English, gold_train, model_dir,
               feat_set='embed',
               eta=eta, mu=mu,
               nv_word=nv_word, nv_tag=nv_tag, nv_label=nv_label, nv_hidden=nv_hidden,
               n_sents=n_sents, n_iter=n_iter,
               verbose=verbose)

    scorer = evaluate(nlp, list(read_json_file(dev_loc)))
    
    print 'TOK', 100-scorer.token_acc
    print 'POS', scorer.tags_acc
    print 'UAS', scorer.uas
    print 'LAS', scorer.las

    print 'NER P', scorer.ents_p
    print 'NER R', scorer.ents_r
    print 'NER F', scorer.ents_f


if __name__ == '__main__':
    plac.call(main)
