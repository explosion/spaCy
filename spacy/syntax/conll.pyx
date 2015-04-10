import numpy
import codecs

from libc.string cimport memset


def read_conll03_file(loc):
    sents = []
    text = codecs.open(loc, 'r', 'utf8').read().strip()
    for doc in text.split('-DOCSTART- -X- O O'):
        doc = doc.strip()
        if not doc:
            continue
        for sent_str in doc.split('\n\n'):
            words = []
            tags = []
            iob_ents = []
            ids = []
            lines = sent_str.strip().split('\n')
            idx = 0
            for line in lines:
                word, tag, chunk, iob = line.split()
                if tag == '"':
                    tag = '``'
                if '|' in tag:
                    tag = tag.split('|')[0]
                words.append(word)
                tags.append(tag)
                iob_ents.append(iob)
                ids.append(idx)
                idx += len(word) + 1
            heads = [-1] * len(words)
            labels = ['ROOT'] * len(words)
            sents.append((' '.join(words), [words],
                         (ids, words, tags, heads, labels, _iob_to_biluo(iob_ents))))
    return sents


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
        sents.append((raw_text, tokenized, (ids, words, tags, heads, labels, iob_ents)))
    return sents


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


cdef class GoldParse:
    def __init__(self, tokens, annot_tuples):
        self.mem = Pool()
        self.loss = 0
        self.length = len(tokens)

        # These are filled by the tagger/parser/entity recogniser
        self.c_tags = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c_heads = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c_labels = <int*>self.mem.alloc(len(tokens), sizeof(int))
        self.c_ner = <Transition*>self.mem.alloc(len(tokens), sizeof(Transition))

        self.tags = [None] * len(tokens)
        self.heads = [-1] * len(tokens)
        self.labels = ['MISSING'] * len(tokens)
        self.ner = ['O'] * len(tokens)
        self.orths = {}

        idx_map = {token.idx: token.i for token in tokens}
        self.ents = []
        ent_start = None
        ent_label = None
        for idx, orth, tag, head, label, ner in zip(*annot_tuples):
            self.orths[idx] = orth
            if idx < tokens[0].idx:
                pass
            elif idx > tokens[-1].idx:
                break
            elif idx in idx_map:
                i = idx_map[idx]
                self.tags[i] = tag
                self.heads[i] = idx_map.get(head, -1)
                self.labels[i] = label
                self.tags[i] = tag
                if ner == '-':
                    self.ner[i] = '-'
                # Deal with inconsistencies in BILUO arising from tokenization
                if ner[0] in ('B', 'U', 'O') and ent_start is not None:
                    self.ents.append((ent_start, i, ent_label))
                    ent_start = None
                    ent_label = None
                if ner[0] in ('B', 'U'):
                    ent_start = i
                    ent_label = ner[2:]
        if ent_start is not None:
            self.ents.append((ent_start, self.length, ent_label))
        for start, end, label in self.ents:
            if start == (end - 1):
                self.ner[start] = 'U-%s' % label
            else:
                self.ner[start] = 'B-%s' % label
                for i in range(start+1, end-1):
                    self.ner[i] = 'I-%s' % label
                self.ner[end-1] = 'L-%s' % label

    def __len__(self):
        return self.length

    @property
    def n_non_punct(self):
        return len([l for l in self.labels if l not in ('P', 'punct')])

    cdef int heads_correct(self, TokenC* tokens, bint score_punct=False) except -1:
        n = 0
        for i in range(self.length):
            if not score_punct and self.labels_[i] not in ('P', 'punct'):
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
