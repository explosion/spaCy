import numpy
import codecs
import json
import random
from .munge.alignment import align

from libc.string cimport memset


def read_json_file(loc):
    paragraphs = []
    for doc in json.load(open(loc)):
        for paragraph in doc['paragraphs']:
            words = []
            ids = []
            tags = []
            heads = []
            labels = []
            iob_ents = []
            for token in paragraph['tokens']:
                words.append(token['orth'])
                ids.append(token['id'])
                tags.append(token['tag'])
                heads.append(token['head'] if token['head'] >= 0 else token['id'])
                labels.append(token['dep'])
                iob_ents.append(token.get('iob_ent', '-'))

            brackets = []
            paragraphs.append((paragraph['raw'],
                (ids, words, tags, heads, labels, _iob_to_biluo(iob_ents)),
                paragraph.get('brackets', [])))
    return paragraphs


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
    def __init__(self, tokens, annot_tuples, brackets=tuple()):
        self.mem = Pool()
        self.loss = 0
        self.length = len(tokens)

        # These are filled by the tagger/parser/entity recogniser
        self.c_tags = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c_heads = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c_labels = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c_ner = <Transition*>self.mem.alloc(len(tokens), sizeof(Transition))
        self.c_brackets = <int**>self.mem.alloc(len(tokens), sizeof(int*))
        for i in range(len(tokens)):
            self.c_brackets[i] = <int*>self.mem.alloc(len(tokens), sizeof(int))

        self.tags = [None] * len(tokens)
        self.heads = [None] * len(tokens)
        self.labels = [''] * len(tokens)
        self.ner = ['-'] * len(tokens)

        self.cand_to_gold = align([t.orth_ for t in tokens], annot_tuples[1])
        self.gold_to_cand = align(annot_tuples[1], [t.orth_ for t in tokens])

        self.orig_annot = zip(*annot_tuples)

        self.ents = []

        for i, gold_i in enumerate(self.cand_to_gold):
            if gold_i is None:
                # TODO: What do we do for missing values again?
                pass
            else:
                self.tags[i] = annot_tuples[2][gold_i]
                self.heads[i] = self.gold_to_cand[annot_tuples[3][gold_i]]
                self.labels[i] = annot_tuples[4][gold_i]
        # TODO: Declare NER information MISSING if tokenization incorrect
        for start, end, label in self.ents:
            if start == (end - 1):
                self.ner[start] = 'U-%s' % label
            else:
                self.ner[start] = 'B-%s' % label
                for i in range(start+1, end-1):
                    self.ner[i] = 'I-%s' % label
                self.ner[end-1] = 'L-%s' % label

        self.brackets = {}
        for (gold_start, gold_end, label_str) in brackets:
            start = self.gold_to_cand[gold_start]
            end = self.gold_to_cand[gold_end]
            if start is not None and end is not None:
                self.brackets.setdefault(start, {}).setdefault(end, set())
                self.brackets[end][start].add(label)

    def __len__(self):
        return self.length


def is_punct_label(label):
    return label == 'P' or label.lower() == 'punct'
