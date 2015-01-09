#!/usr/bin/env python
from __future__ import division
from __future__ import unicode_literals

import os
from os import path
import shutil
import codecs
import random
import time
import gzip

import plac
import cProfile
import pstats

import spacy.util
from spacy.en import English
from spacy.en.pos import POS_TEMPLATES, POS_TAGS, setup_model_dir

from spacy.syntax.parser import GreedyParser
from spacy.syntax.util import Config


def read_tokenized_gold(file_):
    """Read a standard CoNLL/MALT-style format"""
    sents = []
    for sent_str in file_.read().strip().split('\n\n'):
        words = []
        heads = []
        labels = []
        tags = []
        for i, line in enumerate(sent_str.split('\n')):
            word, pos_string, head_idx, label = _parse_line(line)
            words.append(word)
            if head_idx == -1:
                head_idx = i
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
        sents.append((words, heads, labels, tags))
    return sents


def read_docparse_gold(file_):
    sents = []
    for sent_str in file_.read().strip().split('\n\n'):
        words = []
        heads = []
        labels = []
        tags = []
        lines = sent_str.strip().split('\n')
        raw_text = lines[0]
        tok_text = lines[1]
        for i, line in enumerate(lines[2:]):
            word, pos_string, head_idx, label = _parse_line(line)
            words.append(word)
            if head_idx == -1:
                head_idx = i
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
        words = tok_text.replace('<SEP>', ' ').replace('<SENT>', ' ').split(' ')
        sents.append((words, heads, labels, tags))
    return sents

def _parse_line(line):
    pieces = line.split()
    if len(pieces) == 4:
        return pieces[0], pieces[1], int(pieces[2]) - 1, pieces[3]
    else:
        word = pieces[1]
        pos = pieces[3]
        head_idx = int(pieces[6]) - 1
        label = pieces[7]
        return word, pos, head_idx, label

def get_labels(sents):
    left_labels = set()
    right_labels = set()
    for _, heads, labels, _ in sents:
        for child, (head, label) in enumerate(zip(heads, labels)):
            if head > child:
                left_labels.add(label)
            elif head < child:
                right_labels.add(label)
    return list(sorted(left_labels)), list(sorted(right_labels))


def train(Language, sents, model_dir, n_iter=15, feat_set=u'basic', seed=0):
    dep_model_dir = path.join(model_dir, 'deps')
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(dep_model_dir):
        shutil.rmtree(dep_model_dir)
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(dep_model_dir)
    os.mkdir(pos_model_dir)
    setup_model_dir(sorted(POS_TAGS.keys()), POS_TAGS, POS_TEMPLATES,
                    pos_model_dir)

    left_labels, right_labels = get_labels(sents)
    Config.write(dep_model_dir, 'config', features=feat_set, seed=seed,
                 left_labels=left_labels, right_labels=right_labels)

    nlp = Language()
    
    for itn in range(n_iter):
        heads_corr = 0
        pos_corr = 0
        n_tokens = 0
        for words, heads, labels, tags in sents:
            tags = [nlp.tagger.tag_names.index(tag) for tag in tags]
            tokens = nlp.tokenizer.tokens_from_list(words)
            nlp.tagger(tokens)
            heads_corr += nlp.parser.train_sent(tokens, heads, labels)
            pos_corr += nlp.tagger.train(tokens, tags)
            n_tokens += len(tokens)
        acc = float(heads_corr) / n_tokens
        pos_acc = float(pos_corr) / n_tokens
        print '%d: ' % itn, '%.3f' % acc, '%.3f' % pos_acc
        random.shuffle(sents)
    nlp.parser.model.end_training()
    nlp.tagger.model.end_training()
    #nlp.parser.model.dump(path.join(dep_model_dir, 'model'), freq_thresh=0)
    return acc


def evaluate(Language, dev_loc, model_dir):
    nlp = Language()
    n_corr = 0
    total = 0
    with codecs.open(dev_loc, 'r', 'utf8') as file_:
        sents = read_tokenized_gold(file_)
    for words, heads, labels, tags in sents:
        tokens = nlp.tokenizer.tokens_from_list(words)
        nlp.tagger(tokens)
        nlp.parser.parse(tokens)
        for i, token in enumerate(tokens):
            #print i, token.string, i + token.head, heads[i], labels[i]
            if labels[i] == 'P' or labels[i] == 'punct':
                continue
            n_corr += token.head.i == heads[i]
            total += 1
    return float(n_corr) / total


PROFILE = False


def main(train_loc, dev_loc, model_dir):
    with codecs.open(train_loc, 'r', 'utf8') as file_:
        train_sents  = read_tokenized_gold(file_)
    if PROFILE:
        import cProfile
        import pstats
        cmd = "train(EN, train_sents, tag_names, model_dir, n_iter=2)"
        cProfile.runctx(cmd, globals(), locals(), "Profile.prof")
        s = pstats.Stats("Profile.prof")
        s.strip_dirs().sort_stats("time").print_stats()
    else:
        train(English, train_sents, model_dir)
        print evaluate(English, dev_loc, model_dir)
    

if __name__ == '__main__':
    plac.call(main)
