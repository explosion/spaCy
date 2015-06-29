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

from spacy.syntax.parser import Parser
from spacy._theano import TheanoModel

import theano
import theano.tensor as T

from theano.printing import Print

import numpy
from collections import OrderedDict, defaultdict


theano.config.profile = False
theano.config.floatX = 'float32'
floatX = theano.config.floatX


def th_share(w, name=''):
    return theano.shared(value=w, borrow=True, name=name)

class Param(object):
    def __init__(self, numpy_data, name='?', wrapper=th_share):
        self.curr = wrapper(numpy_data, name=name+'_curr')
        self.step = wrapper(numpy.zeros(numpy_data.shape, numpy_data.dtype),
                            name=name+'_step')

    def updates(self, cost, timestep, eta, mu):
        step = (mu * self.step) - T.grad(cost, self.curr)
        curr = self.curr + (eta * step)
        return [(self.curr, curr), (self.step, step)]


class AdadeltaParam(object):
    def __init__(self, numpy_data, name='?', wrapper=th_share):
        self.curr = wrapper(numpy_data, name=name+'_curr')
        # accu: accumulate gradient magnitudes
        self.accu = wrapper(numpy.zeros(numpy_data.shape, dtype=numpy_data.dtype))
        # delta_accu: accumulate update magnitudes (recursively!)
        self.delta_accu = wrapper(numpy.zeros(numpy_data.shape, dtype=numpy_data.dtype))

    def updates(self, cost, timestep, eps, rho):
        # update accu (as in rmsprop)
        grad = T.grad(cost, self.curr)
        accu_new = rho * self.accu + (1 - rho) * grad ** 2

        # compute parameter update, using the 'old' delta_accu
        update = (grad * T.sqrt(self.delta_accu + eps) /
                  T.sqrt(accu_new + eps))
        # update delta_accu (as accu, but accumulating updates)
        delta_accu_new = rho * self.delta_accu + (1 - rho) * update ** 2
        return [(self.curr, self.curr - update), (self.accu, accu_new),
                (self.delta_accu, delta_accu_new)]


class AvgParam(object):
    def __init__(self, numpy_data, name='?', wrapper=th_share):
        self.curr = wrapper(numpy_data, name=name+'_curr')
        self.avg = self.curr
        self.avg = wrapper(numpy_data.copy(), name=name+'_avg')
        self.step = wrapper(numpy.zeros(numpy_data.shape, numpy_data.dtype),
                            name=name+'_step')

    def updates(self, cost, timestep, eta=0.001, mu=0.9):
        step = (mu * self.step) - T.grad(cost, self.curr)
        curr = self.curr + (eta * step)
        alpha = (1 / timestep).clip(0.001, 0.9).astype(floatX)
        avg = ((1 - alpha) * self.avg) + (alpha * curr)
        return [(self.curr, curr), (self.step, step), (self.avg, avg)]


def feed_layer(activation, weights, bias, input_):
    return activation(T.dot(input_, weights) + bias)


def L2(L2_reg, *weights):
    return L2_reg * sum((w ** 2).sum() for w in weights)


def L1(L1_reg, *weights):
    return L1_reg * sum(abs(w).sum() for w in weights)


def relu(x):
    return x * (x > 0)


def _init_weights(n_in, n_out):
    rng = numpy.random.RandomState(1234)
    
    weights = numpy.asarray(
        rng.standard_normal(size=(n_in, n_out)) * numpy.sqrt(2.0 / n_in),
        dtype=theano.config.floatX
    )
    bias = numpy.zeros((n_out,), dtype=theano.config.floatX)
    return [AvgParam(weights, name='W'), AvgParam(bias, name='b')]


def compile_theano_model(n_classes, n_hidden, n_in, L1_reg, L2_reg):
    costs = T.ivector('costs')
    is_gold = T.ivector('is_gold')
    x = T.vector('x') 
    y = T.scalar('y')
    timestep = theano.shared(1)
    eta = T.scalar('eta').astype(floatX)
    mu = T.scalar('mu').astype(floatX)

    maxent_W, maxent_b = _init_weights(n_hidden, n_classes)
    hidden_W, hidden_b = _init_weights(n_in, n_hidden)

    # Feed the inputs forward through the network
    p_y_given_x = feed_layer(
                    T.nnet.softmax,
                    maxent_W.curr,
                    maxent_b.curr,
                      feed_layer(
                        relu,
                        hidden_W.curr,
                        hidden_b.curr,
                        x))
    stabilizer = 1e-8

    cost = (
        -T.log(T.sum((p_y_given_x[0] + stabilizer) * T.eq(costs, 0)))
        + L2(L2_reg, maxent_W.curr, hidden_W.curr)
    )

    debug = theano.function(
        name='debug',
        inputs=[x, costs],
        outputs=[p_y_given_x, T.eq(costs, 0), p_y_given_x[0] * T.eq(costs, 0)],
    )

    train_model = theano.function(
        name='train_model',
        inputs=[x, costs, eta, mu],
        outputs=[p_y_given_x[0], T.grad(cost, x), T.argmax(p_y_given_x, axis=1),
                 cost],
        updates=(
            [(timestep, timestep + 1)] + 
             maxent_W.updates(cost, timestep, eta=eta, mu=mu) + 
             maxent_b.updates(cost, timestep, eta=eta, mu=mu) +
             hidden_W.updates(cost, timestep, eta=eta, mu=mu) +
             hidden_b.updates(cost, timestep, eta=eta, mu=mu)
        ),
        on_unused_input='warn'
    )

    evaluate_model = theano.function(
        name='evaluate_model',
        inputs=[x],
        outputs=[
            feed_layer(
              T.nnet.softmax,
              maxent_W.avg,
              maxent_b.avg,
              feed_layer(
                relu,
                hidden_W.avg,
                hidden_b.avg,
                x
              )
            )[0]
        ]
    )
    return debug, train_model, evaluate_model


def score_model(scorer, nlp, annot_tuples, verbose=False):
    tokens = nlp.tokenizer.tokens_from_list(annot_tuples[1])
    nlp.tagger(tokens)
    nlp.parser(tokens)
    gold = GoldParse(tokens, annot_tuples)
    scorer.score(tokens, gold, verbose=verbose)


def train(Language, gold_tuples, model_dir, n_iter=15, feat_set=u'basic',
          seed=0, n_sents=0, 
          verbose=False,
          eta=0.01, mu=0.9, nv_hidden=100,
          nv_word=10, nv_tag=10, nv_label=10):
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
        features=feat_set,
        labels=Language.ParserTransitionSystem.get_labels(gold_tuples),
        vector_lengths=(nv_word, nv_tag, nv_label),
        hidden_nodes=nv_hidden,
        eta=eta,
        mu=mu
    )
    
    if n_sents > 0:
        gold_tuples = gold_tuples[:n_sents]
    
    nlp = Language(data_dir=model_dir)

    def make_model(n_classes, (words, tags, labels), model_dir):
        n_in = (nv_word  * len(words)) + \
               (nv_tag   * len(tags)) + \
               (nv_label * len(labels))
        debug, train_func, predict_func = compile_theano_model(n_classes, nv_hidden,
                                                        n_in, 0.0, 0.00)
        return TheanoModel(
            n_classes,
            ((nv_word, words), (nv_tag, tags), (nv_label, labels)),
            train_func,
            predict_func,
            model_loc=model_dir, 
            eta=eta, mu=mu,
            debug=debug)

    nlp._parser = Parser(nlp.vocab.strings, dep_model_dir, nlp.ParserTransitionSystem,
                         make_model)

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
