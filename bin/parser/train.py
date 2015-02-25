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


def read_docparse_gold(file_):
    paragraphs = []
    for sent_str in file_.read().strip().split('\n\n'):
        if not sent_str.strip():
            continue
        words = []
        heads = []
        labels = []
        tags = []
        ids = []
        lines = sent_str.strip().split('\n')
        raw_text = lines.pop(0)
        tok_text = lines.pop(0)
        for i, line in enumerate(lines):
            id_, word, pos_string, head_idx, label = _parse_line(line)
            if label == 'root':
                label = 'ROOT'
            words.append(word)
            if head_idx < 0:
                head_idx = id_
            ids.append(id_)
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
        tokenized = [sent_str.replace('<SEP>', ' ').split(' ')
                     for sent_str in tok_text.split('<SENT>')]
        paragraphs.append((raw_text, tokenized, ids, words, tags, heads, labels))
    return paragraphs


def _map_indices_to_tokens(ids, heads):
    mapped = []
    for head in heads:
        if head not in ids:
            mapped.append(None)
        else:
            mapped.append(ids.index(head))
    return mapped


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


loss = 0
def _align_annotations_to_non_gold_tokens(tokens, words, annot):
    global loss
    tags = []
    heads = []
    labels = []
    orig_words = list(words)
    missed = []
    for token in tokens:
        while annot and token.idx > annot[0][0]:
            miss_id, miss_tag, miss_head, miss_label = annot.pop(0)
            miss_w = words.pop(0)
            if not is_punct_label(miss_label):
                missed.append(miss_w)
                loss += 1
        if not annot:
            tags.append(None)
            heads.append(None)
            labels.append(None)
            continue
        id_, tag, head, label = annot[0]
        if token.idx == id_:
            tags.append(tag)
            heads.append(head)
            labels.append(label)
            annot.pop(0)
            words.pop(0)
        elif token.idx < id_:
            tags.append(None)
            heads.append(None)
            labels.append(None)
        else:
            raise StandardError
    #if missed:
    #    print orig_words
    #    print missed
    #    for t in tokens:
    #        print t.idx, t.orth_
    return loss, tags, heads, labels

        
def iter_data(paragraphs, tokenizer, gold_preproc=False):
    for raw, tokenized, ids, words, tags, heads, labels in paragraphs:
        if not gold_preproc:
            tokens = tokenizer(raw)
            loss, tags, heads, labels = _align_annotations_to_non_gold_tokens(
                                            tokens, list(words),
                                            zip(ids, tags, heads, labels))
            ids = [t.idx for t in tokens]
            heads = _map_indices_to_tokens(ids, heads)
            yield tokens, tags, heads, labels
        else:
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


def get_labels(sents):
    left_labels = set()
    right_labels = set()
    for raw, tokenized, ids, words, tags, heads, labels in sents:
        for child, (head, label) in enumerate(zip(heads, labels)):
            if head > child:
                left_labels.add(label)
            elif head < child:
                right_labels.add(label)
    return list(sorted(left_labels)), list(sorted(right_labels))


def train(Language, paragraphs, model_dir, n_iter=15, feat_set=u'basic', seed=0,
          gold_preproc=False, force_gold=False):
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

    left_labels, right_labels = get_labels(paragraphs)
    Config.write(dep_model_dir, 'config', features=feat_set, seed=seed,
                 left_labels=left_labels, right_labels=right_labels)

    nlp = Language()
    
    for itn in range(n_iter):
        heads_corr = 0
        pos_corr = 0
        n_tokens = 0
        for tokens, tag_strs, heads, labels in iter_data(paragraphs, nlp.tokenizer,
                                                         gold_preproc=gold_preproc):
            nlp.tagger(tokens)
            try:
                heads_corr += nlp.parser.train_sent(tokens, heads, labels, force_gold=force_gold)
            except OracleError:
                continue
            pos_corr += nlp.tagger.train(tokens, tag_strs)
            n_tokens += len(tokens)
        acc = float(heads_corr) / n_tokens
        pos_acc = float(pos_corr) / n_tokens
        print '%d: ' % itn, '%.3f' % acc, '%.3f' % pos_acc
        random.shuffle(paragraphs)
    nlp.parser.model.end_training()
    nlp.tagger.model.end_training()
    return acc


def evaluate(Language, dev_loc, model_dir, gold_preproc=False):
    global loss
    nlp = Language()
    n_corr = 0
    pos_corr = 0
    n_tokens = 0
    total = 0
    skipped = 0
    loss = 0
    with codecs.open(dev_loc, 'r', 'utf8') as file_:
        paragraphs = read_docparse_gold(file_)
    for tokens, tag_strs, heads, labels in iter_data(paragraphs, nlp.tokenizer,
                                                     gold_preproc=gold_preproc):
        assert len(tokens) == len(labels)
        nlp.tagger(tokens)
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


def main(train_loc, dev_loc, model_dir):
    with codecs.open(train_loc, 'r', 'utf8') as file_:
        train_sents  = read_docparse_gold(file_)
    train(English, train_sents, model_dir, gold_preproc=False, force_gold=False)
    print evaluate(English, dev_loc, model_dir, gold_preproc=False)
    

if __name__ == '__main__':
    plac.call(main)
