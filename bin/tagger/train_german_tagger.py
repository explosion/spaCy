#!/usr/bin/env python
from __future__ import division
from __future__ import unicode_literals

import os
from os import path
import shutil
import io
import random
import time
import gzip
import ujson

import plac
import cProfile
import pstats

import spacy.util
from spacy.de import German
from spacy.gold import GoldParse
from spacy.tagger import Tagger
from spacy.scorer import PRFScore

from spacy.tagger import P2_orth, P2_cluster, P2_shape, P2_prefix, P2_suffix, P2_pos, P2_lemma, P2_flags 
from spacy.tagger import P1_orth, P1_cluster, P1_shape, P1_prefix, P1_suffix, P1_pos, P1_lemma, P1_flags 
from spacy.tagger import W_orth, W_cluster, W_shape, W_prefix, W_suffix, W_pos, W_lemma, W_flags
from spacy.tagger import N1_orth, N1_cluster, N1_shape, N1_prefix, N1_suffix, N1_pos, N1_lemma, N1_flags
from spacy.tagger import N2_orth, N2_cluster, N2_shape, N2_prefix, N2_suffix, N2_pos, N2_lemma, N2_flags, N_CONTEXT_FIELDS


def default_templates():
    return spacy.tagger.Tagger.default_templates()

def default_templates_without_clusters():
    return (
        (W_orth,),
        (P1_lemma, P1_pos),
        (P2_lemma, P2_pos),
        (N1_orth,),
        (N2_orth,),

        (W_suffix,),
        (W_prefix,),

        (P1_pos,),
        (P2_pos,),
        (P1_pos, P2_pos),
        (P1_pos, W_orth),
        (P1_suffix,),
        (N1_suffix,),

        (W_shape,),

        (W_flags,),
        (N1_flags,),
        (N2_flags,),
        (P1_flags,),
        (P2_flags,),
    )


def make_tagger(vocab, templates):
    model = spacy.tagger.TaggerModel(templates)
    return spacy.tagger.Tagger(vocab,model)


def read_conll(file_):
    def sentences():
        words, tags = [], []
        for line in file_:
            line = line.strip()
            if line:
                word, tag = line.split('\t')[1::3][:2] # get column 1 and 4 (CoNLL09)
                words.append(word)
                tags.append(tag)
            elif words:
                yield words, tags
                words, tags = [], []
        if words:
            yield words, tags
    return [ s for s in sentences() ]

        
def score_model(score, nlp, words, gold_tags):
    tokens = nlp.tokenizer.tokens_from_list(words)
    assert(len(tokens) == len(gold_tags))
    nlp.tagger(tokens)

    for token, gold_tag in zip(tokens,gold_tags):
        score.score_set(set([token.tag_]),set([gold_tag]))


def train(Language, train_sents, dev_sents, model_dir, n_iter=15, seed=21):
    # make shuffling deterministic
    random.seed(seed)

    # set up directory for model
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(pos_model_dir)

    nlp = Language(data_dir=model_dir, tagger=False, parser=False, entity=False)
    nlp.tagger = make_tagger(nlp.vocab,default_templates())
     
    print("Itn.\ttrain acc %\tdev acc %")
    for itn in range(n_iter):
        # train on train set
        #train_acc = PRFScore()
        correct, total = 0., 0.
        for words, gold_tags in train_sents:
            tokens = nlp.tokenizer.tokens_from_list(words)
            correct += nlp.tagger.train(tokens, gold_tags)
            total += len(words)
        train_acc = correct/total

        # test on dev set
        dev_acc = PRFScore()
        for words, gold_tags in dev_sents:
            score_model(dev_acc, nlp, words, gold_tags)

        random.shuffle(train_sents)
        print('%d:\t%6.2f\t%6.2f' % (itn, 100*train_acc, 100*dev_acc.precision))


    print('end training')
    nlp.end_training(model_dir)
    print('done')


@plac.annotations(
    train_loc=("Location of CoNLL 09 formatted training file"),
    dev_loc=("Location of CoNLL 09 formatted development file"),
    model_dir=("Location of output model directory"),
    eval_only=("Skip training, and only evaluate", "flag", "e", bool),
    n_iter=("Number of training iterations", "option", "i", int),
)
def main(train_loc, dev_loc, model_dir, eval_only=False, n_iter=15):
    # training
    if not eval_only:
        with io.open(train_loc, 'r', encoding='utf8') as trainfile_, \
             io.open(dev_loc, 'r', encoding='utf8') as devfile_:
            train_sents = read_conll(trainfile_)
            dev_sents = read_conll(devfile_)
        train(German, train_sents, dev_sents, model_dir, n_iter=n_iter)

    # testing
    with io.open(dev_loc, 'r', encoding='utf8') as file_:
        dev_sents = read_conll(file_)
        nlp = German(data_dir=model_dir)

        dev_acc = PRFScore()
        for words, gold_tags in dev_sents:
            score_model(dev_acc, nlp, words, gold_tags)                
        
        print('POS: %6.2f %%' % (100*dev_acc.precision))


if __name__ == '__main__':
    plac.call(main)
