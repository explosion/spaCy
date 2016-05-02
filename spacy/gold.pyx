import numpy
import io
import json
import random
import re
import os
from os import path

from libc.string cimport memset

try:
    import ujson as json
except ImportError:
    import json

from .syntax import nonproj


def tags_to_entities(tags):
    entities = []
    start = None
    for i, tag in enumerate(tags):
        if tag.startswith('O'):
            # TODO: We shouldn't be getting these malformed inputs. Fix this.
            if start is not None:
                start = None
            continue
        elif tag == '-':
            continue
        elif tag.startswith('I'):
            assert start is not None, tags[:i]
            continue
        if tag.startswith('U'):
            entities.append((tag[2:], i, i))
        elif tag.startswith('B'):
            start = i
        elif tag.startswith('L'):
            entities.append((tag[2:], start, i))
            start = None
        else:
            raise Exception(tag)
    return entities



def align(cand_words, gold_words):
    cost, edit_path = _min_edit_path(cand_words, gold_words)
    alignment = []
    i_of_gold = 0
    for move in edit_path:
        if move == 'M':
            alignment.append(i_of_gold)
            i_of_gold += 1
        elif move == 'S':
            alignment.append(None)
            i_of_gold += 1
        elif move == 'D':
            alignment.append(None)
        elif move == 'I':
            i_of_gold += 1
        else:
            raise Exception(move)
    return alignment


punct_re = re.compile(r'\W')
def _min_edit_path(cand_words, gold_words):
    cdef:
        Pool mem
        int i, j, n_cand, n_gold
        int* curr_costs
        int* prev_costs

    # TODO: Fix this --- just do it properly, make the full edit matrix and
    # then walk back over it...
    # Preprocess inputs
    cand_words = [punct_re.sub('', w) for w in cand_words] 
    gold_words = [punct_re.sub('', w) for w in gold_words] 
    
    if cand_words == gold_words:
        return 0, ''.join(['M' for _ in gold_words])
    mem = Pool()
    n_cand = len(cand_words)
    n_gold = len(gold_words)
    # Levenshtein distance, except we need the history, and we may want different
    # costs.
    # Mark operations with a string, and score the history using _edit_cost.
    previous_row = []
    prev_costs = <int*>mem.alloc(n_gold + 1, sizeof(int))
    curr_costs = <int*>mem.alloc(n_gold + 1, sizeof(int))
    for i in range(n_gold + 1):
        cell = ''
        for j in range(i):
            cell += 'I'
        previous_row.append('I' * i)
        prev_costs[i] = i
    for i, cand in enumerate(cand_words):
        current_row = ['D' * (i + 1)]
        curr_costs[0] = i+1
        for j, gold in enumerate(gold_words):
            if gold.lower() == cand.lower():
                s_cost = prev_costs[j]
                i_cost = curr_costs[j] + 1
                d_cost = prev_costs[j + 1] + 1
            else:
                s_cost = prev_costs[j] + 1
                i_cost = curr_costs[j] + 1
                d_cost = prev_costs[j + 1] + (1 if cand else 0)

            if s_cost <= i_cost and s_cost <= d_cost:
                best_cost = s_cost
                best_hist = previous_row[j] + ('M' if gold == cand else 'S')
            elif i_cost <= s_cost and i_cost <= d_cost:
                best_cost = i_cost
                best_hist = current_row[j] + 'I'
            else:
                best_cost = d_cost
                best_hist = previous_row[j + 1] + 'D'
            
            current_row.append(best_hist)
            curr_costs[j+1] = best_cost
        previous_row = current_row
        for j in range(len(gold_words) + 1):
            prev_costs[j] = curr_costs[j]
            curr_costs[j] = 0

    return prev_costs[n_gold], previous_row[-1]


def read_json_file(loc, docs_filter=None):
    print loc
    if path.isdir(loc):
        for filename in os.listdir(loc):
            yield from read_json_file(path.join(loc, filename))
    else:
        with open(loc) as file_:
            docs = json.load(file_)
        for doc in docs:
            if docs_filter is not None and not docs_filter(doc):
                continue
            paragraphs = []
            for paragraph in doc['paragraphs']:
                sents = []
                for sent in paragraph['sentences']:
                    words = []
                    ids = []
                    tags = []
                    heads = []
                    labels = []
                    ner = []
                    for i, token in enumerate(sent['tokens']):
                        words.append(token['orth'])
                        ids.append(i)
                        tags.append(token.get('tag','-'))
                        heads.append(token.get('head',0) + i)
                        labels.append(token.get('dep',''))
                        # Ensure ROOT label is case-insensitive
                        if labels[-1].lower() == 'root':
                            labels[-1] = 'ROOT'
                        ner.append(token.get('ner', '-'))
                    sents.append((
                        (ids, words, tags, heads, labels, ner),
                        sent.get('brackets', [])))
                if sents:
                    yield (paragraph.get('raw', None), sents)


def _iob_to_biluo(tags):
    out = []
    curr_label = None
    tags = list(tags)
    while tags:
        out.extend(_consume_os(tags))
        out.extend(_consume_ent(tags))
    return out


def _consume_os(tags):
    while tags and tags[0] == 'O':
        yield tags.pop(0)


def _consume_ent(tags):
    if not tags:
        return []
    target = tags.pop(0).replace('B', 'I')
    length = 1
    while tags and tags[0] == target:
        length += 1
        tags.pop(0)
    label = target[2:]
    if length == 1:
        return ['U-' + label]
    else:
        start = 'B-' + label
        end = 'L-' + label
        middle = ['I-%s' % label for _ in range(1, length - 1)]
        return [start] + middle + [end]


cdef class GoldParse:
    def __init__(self, tokens, annot_tuples, brackets=tuple(), make_projective=False):
        self.mem = Pool()
        self.loss = 0
        self.length = len(tokens)

        # These are filled by the tagger/parser/entity recogniser
        self.c.tags = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c.heads = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c.labels = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c.ner = <Transition*>self.mem.alloc(len(tokens), sizeof(Transition))
        self.c.brackets = <int**>self.mem.alloc(len(tokens), sizeof(int*))
        for i in range(len(tokens)):
            self.c.brackets[i] = <int*>self.mem.alloc(len(tokens), sizeof(int))

        self.tags = [None] * len(tokens)
        self.heads = [None] * len(tokens)
        self.labels = [''] * len(tokens)
        self.ner = ['-'] * len(tokens)

        self.cand_to_gold = align([t.orth_ for t in tokens], annot_tuples[1])
        self.gold_to_cand = align(annot_tuples[1], [t.orth_ for t in tokens])

        self.orig_annot = list(zip(*annot_tuples))

        words = [w.orth_ for w in tokens]
        for i, gold_i in enumerate(self.cand_to_gold):
            if words[i].isspace():
                self.tags[i] = 'SP'
                self.heads[i] = None
                self.labels[i] = None
                self.ner[i] = 'O'
            if gold_i is None:
                pass
            else:
                self.tags[i] = annot_tuples[2][gold_i]
                self.heads[i] = self.gold_to_cand[annot_tuples[3][gold_i]]
                self.labels[i] = annot_tuples[4][gold_i]
                self.ner[i] = annot_tuples[5][gold_i]

        cycle = nonproj.contains_cycle(self.heads)
        if cycle != None:
            raise Exception("Cycle found: %s" % cycle)

        if make_projective:
            proj_heads,_ = nonproj.PseudoProjectivity.projectivize(self.heads,self.labels)
            self.heads = proj_heads

        self.brackets = {}
        for (gold_start, gold_end, label_str) in brackets:
            start = self.gold_to_cand[gold_start]
            end = self.gold_to_cand[gold_end]
            if start is not None and end is not None:
                self.brackets.setdefault(start, {}).setdefault(end, set())
                self.brackets[end][start].add(label_str)

    def __len__(self):
        return self.length

    @property
    def is_projective(self):
        return not nonproj.is_nonproj_tree(self.heads)


def is_punct_label(label):
    return label == 'P' or label.lower() == 'punct'










