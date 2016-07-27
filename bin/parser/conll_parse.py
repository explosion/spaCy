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
from spacy.syntax.parser import OracleError
from spacy.syntax.util import Config


def is_punct_label(label):
    return label == 'P' or label.lower() == 'punct'


def read_gold(file_):
    """Read a standard CoNLL/MALT-style format"""
    sents = []
    for sent_str in file_.read().strip().split('\n\n'):
        ids = []
        words = []
        heads = []
        labels = []
        tags = []
        for i, line in enumerate(sent_str.split('\n')):
            id_, word, pos_string, head_idx, label = _parse_line(line)
            words.append(word)
            if head_idx == -1:
                head_idx = i
            ids.append(id_)
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
        text = ' '.join(words)
        sents.append((text, [words], ids, words, tags, heads, labels))
    return sents


def _parse_line(line):
    pieces = line.split()
    id_ = int(pieces[0])
    word = pieces[1]
    pos = pieces[3]
    head_idx = int(pieces[6])
    label = pieces[7]
    return id_, word, pos, head_idx, label

        
def iter_data(paragraphs, tokenizer, gold_preproc=False):
    for raw, tokenized, ids, words, tags, heads, labels in paragraphs:
        assert len(words) == len(heads)
        for words in tokenized:
            sent_ids = ids[:len(words)]
            sent_tags = tags[:len(words)]
            sent_heads = heads[:len(words)]
            sent_labels = labels[:len(words)]
            sent_heads = _map_indices_to_tokens(sent_ids, sent_heads)
            tokens = tokenizer.tokens_from_list(words)
            yield tokens, sent_tags, sent_heads, sent_labels
            ids = ids[len(words):]
            tags = tags[len(words):]
            heads = heads[len(words):]
            labels = labels[len(words):]


def _map_indices_to_tokens(ids, heads):
    mapped = []
    for head in heads:
        if head not in ids:
            mapped.append(None)
        else:
            mapped.append(ids.index(head))
    return mapped



def evaluate(Language, dev_loc, model_dir):
    global loss
    nlp = Language()
    n_corr = 0
    pos_corr = 0
    n_tokens = 0
    total = 0
    skipped = 0
    loss = 0
    with codecs.open(dev_loc, 'r', 'utf8') as file_:
        paragraphs = read_gold(file_)
    for tokens, tag_strs, heads, labels in iter_data(paragraphs, nlp.tokenizer):
        assert len(tokens) == len(labels)
        nlp.tagger.tag_from_strings(tokens, tag_strs)
        nlp.parser(tokens)
        for i, token in enumerate(tokens):
            try:
                pos_corr += token.tag_ == tag_strs[i]
            except:
                print i, token.orth_, token.tag
                raise
            n_tokens += 1
            if heads[i] is None:
                skipped += 1
                continue
            if is_punct_label(labels[i]):
                continue
            n_corr += token.head.i == heads[i]
            total += 1
    print loss, skipped, (loss+skipped + total)
    print pos_corr / n_tokens
    return float(n_corr) / (total + loss)


def main(dev_loc, model_dir):
    print evaluate(English, dev_loc, model_dir)
    

if __name__ == '__main__':
    plac.call(main)
