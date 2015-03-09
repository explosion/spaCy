import numpy
import codecs
from .ner_util import iob_to_biluo

from libc.string cimport memset


def read_docparse_file(loc):
    sents = []
    for sent_str in codecs.open(loc, 'r', 'utf8').read().strip().split('\n\n'):
        words = []
        heads = []
        labels = []
        tags = []
        ids = []
        iob_ents = []
        lines = sent_str.strip().split('\n')
        raw_text = lines.pop(0).strip()
        tok_text = lines.pop(0).strip()
        for i, line in enumerate(lines):
            id_, word, pos_string, head_idx, label, iob_ent = _parse_line(line)
            if label == 'root':
                label = 'ROOT'
            words.append(word)
            if head_idx < 0:
                head_idx = id_
            ids.append(id_)
            heads.append(head_idx)
            labels.append(label)
            tags.append(pos_string)
            iob_ents.append(iob_ent)
        tokenized = [s.replace('<SEP>', ' ').split(' ')
                     for s in tok_text.split('<SENT>')]
        sents.append((raw_text, tokenized, (ids, tags, heads, labels, iob_ents)))
    return sents


cdef class GoldParse:
    def __init__(self, tokens, annot_tuples, pos_tags, dep_labels, entity_types):
        self.mem = Pool()
        self.loss = 0
        self.length = len(tokens)
        self.ids = numpy.empty(shape=(len(tokens), 1), dtype=numpy.int32)
        self.tags = numpy.empty(shape=(len(tokens), 1), dtype=numpy.int32)
        self.heads = numpy.empty(shape=(len(tokens), 1), dtype=numpy.int32)
        self.labels = numpy.empty(shape=(len(tokens), 1), dtype=numpy.int32)

        self.ids[:] = -1
        self.tags[:] = -1
        self.heads[:] = -1
        self.labels[:] = -1

        self.ner = <Transition*>self.mem.alloc(len(tokens), sizeof(Transition))
        self.c_heads = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c_labels = <int*>self.mem.alloc(len(tokens), sizeof(int))

        for i in range(len(tokens)):
            self.c_heads[i] = -1
            self.c_labels[i] = -1
        
        self.tags_ = [None] * len(tokens)
        self.labels_ = [None] * len(tokens)
        self.ner_ = [None] * len(tokens)

        idx_map = {token.idx: token.i for token in tokens}
        print idx_map
        # TODO: Fill NER moves
        print raw_text
        for idx, tag, head, label, ner in zip(*annot_tuples):
            if idx < tokens[0].idx:
                pass
            elif idx > tokens[-1].idx:
                break
            elif idx in idx_map:
                i = idx_map[idx]
                print i, idx, head, idx_map.get(head, -1)
                self.ids[i] = idx
                self.tags[i] = pos_tags.index(tag)
                self.heads[i] = idx_map.get(head, -1)
                self.labels[i] = dep_labels[label]
                self.c_heads[i] = -1
                self.c_labels[i] = -1
                self.tags_[i] = tag
                self.labels_[i] = label
                self.ner_[i] = ner

    @property
    def n_non_punct(self):
        return len([l for l in self.labels if l != 'P'])

    cdef int heads_correct(self, TokenC* tokens, bint score_punct=False) except -1:
        n = 0
        for i in range(self.length):
            if not score_punct and self.labels_[i] == 'P':
                continue
            if self.heads[i] == -1:
                continue
            n += (i + tokens[i].head) == self.heads[i]
        return n

    def is_correct(self, i, head):
        return head == self.c_heads[i]


def is_punct_label(label):
    return label == 'P' or label.lower() == 'punct'


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
        iob_ent = pieces[5]
        head_idx = int(pieces[6])
        label = pieces[7]
        return id_, word, pos, head_idx, label, iob_ent


cdef class NERAnnotation:
    def __init__(self, entities, length, entity_types):
        self.mem = Pool()
        self.starts = <int*>self.mem.alloc(length, sizeof(int))
        self.ends = <int*>self.mem.alloc(length, sizeof(int))
        self.labels = <int*>self.mem.alloc(length, sizeof(int))
        self.entities = entities
        memset(self.starts, -1, sizeof(int) * length)
        memset(self.ends, -1, sizeof(int) * length)
        memset(self.labels, -1, sizeof(int) * length)
        
        cdef int start, end, label
        for start, end, label in entities:
            for i in range(start, end):
                self.starts[i] = start
                self.ends[i] = end
                self.labels[i] = label
    @property
    def biluo_tags(self):
        pass

    @property
    def iob_tags(self):
        pass

    @classmethod
    def from_iobs(cls, iob_strs, entity_types):
        return cls.from_biluos(iob_to_biluo(iob_strs), entity_types)

    @classmethod
    def from_biluos(cls, tag_strs, entity_types):
        entities = []
        start = None
        for i, tag_str in enumerate(tag_strs):
            if tag_str == 'O' or tag_str == '-':
                continue
            move, label_str = tag_str.split('-')
            label = entity_types.index(label_str)
            if label == -1:
                label = len(entity_types)
                entity_types.append(label)
            if move == 'U':
                assert start is None
                entities.append((i, i+1, label))
            elif move == 'B':
                assert start is None
                start = i
            elif move == 'L':
                assert start is not None
                entities.append((start, i+1, label))
                start = None
        return cls(entities, len(tag_strs), entity_types)


