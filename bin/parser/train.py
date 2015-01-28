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
        ids = []
        words = []
        heads = []
        labels = []
        tags = []
        for i, line in enumerate(sent_str.split('\n')):
            word, pos_string, head_idx, label = _parse_line(line)
            words.append(word)
            if head_idx == -1:
                head_idx = i
            ids.append(id_)
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
        sents.append((ids_, words, heads, labels, tags))
    return sents


def read_docparse_gold(file_):
    sents = []
    for sent_str in file_.read().strip().split('\n\n'):
        words = []
        heads = []
        labels = []
        tags = []
        ids = []
        lines = sent_str.strip().split('\n')
        raw_text = lines[0]
        tok_text = lines[1]
        for i, line in enumerate(lines[2:]):
            id_, word, pos_string, head_idx, label = _parse_line(line)
            if label == 'root':
                label = 'ROOT'
            if pos_string == "``":
                word = "``"
            elif pos_string == "''":
                word = "''"
            words.append(word)
            if head_idx < 0:
                head_idx = id_
            ids.append(id_)
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
        heads = _map_indices_to_tokens(ids, heads)
        words = tok_text.replace('<SENT>', ' ').replace('<SEP>', ' ').split()
        #print words
        #print heads
        sents.append((words, heads, labels, tags))
        #sent_strings = tok_text.split('<SENT>')
        #for sent in sent_strings:
        #    sent_words = sent.replace('<SEP>', ' ').split(' ')
        #    sent_heads = []
        #    sent_labels = []
        #    sent_tags = []
        #    sent_ids = []
        #    while len(sent_heads) < len(sent_words):
        #        sent_heads.append(heads.pop(0))
        #        sent_labels.append(labels.pop(0))
        #        sent_tags.append(tags.pop(0))
        #        sent_ids.append(ids.pop(0))
        #    sent_heads = _map_indices_to_tokens(sent_ids, sent_heads)
        #    sents.append((sent_words, sent_heads, sent_labels, sent_tags))
    return sents

def _map_indices_to_tokens(ids, heads):
    return [ids.index(head) for head in heads]
    


def _parse_line(line):
    pieces = line.split()
    if len(pieces) == 4:
        return 0, pieces[0], pieces[1], int(pieces[2]) - 1, pieces[3]
    else:
        id_ = int(pieces[0])
        word = pieces[1]
        pos = pieces[3]
        head_idx = int(pieces[6])
        label = pieces[7]
        return id_, word, pos, head_idx, label

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
            try:
                heads_corr += nlp.parser.train_sent(tokens, heads, labels, force_gold=False)
            except:
                print heads
                raise
            pos_corr += nlp.tagger.train(tokens, tags)
            n_tokens += len(tokens)
        acc = float(heads_corr) / n_tokens
        pos_acc = float(pos_corr) / n_tokens
        print '%d: ' % itn, '%.3f' % acc, '%.3f' % pos_acc
        random.shuffle(sents)
    nlp.parser.model.end_training()
    nlp.tagger.model.end_training()
    return acc


def evaluate(Language, dev_loc, model_dir):
    nlp = Language()
    n_corr = 0
    total = 0
    with codecs.open(dev_loc, 'r', 'utf8') as file_:
        sents = read_docparse_gold(file_)
    for words, heads, labels, tags in sents:
        tokens = nlp.tokenizer.tokens_from_list(words)
        nlp.tagger(tokens)
        nlp.parser(tokens)
        for i, token in enumerate(tokens):
            #print i, token.orth_, token.head.orth_, tokens[heads[i]].orth_, labels[i], token.head.i == heads[i]
            if labels[i] == 'P' or labels[i] == 'punct':
                continue
            n_corr += token.head.i == heads[i]
            total += 1
    return float(n_corr) / total


PROFILE = False


def main(train_loc, dev_loc, model_dir):
    with codecs.open(train_loc, 'r', 'utf8') as file_:
        train_sents  = read_docparse_gold(file_)
    train_sents = train_sents
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
