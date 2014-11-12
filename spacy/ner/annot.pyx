from libc.string cimport memset


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

    @classmethod
    def from_bilous(cls, tag_strs, entity_types):
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



def read_iob(file_, entity_types, create_tokens):
    sent_strs = file_.read().strip().split('\n\n')
    sents = []
    for sent_str in sent_strs:
        if sent_str.startswith('-DOCSTART-'):
            continue
        words = []
        iob = []
        for token_str in sent_str.split('\n'):
            word, pos, chunk, ner = token_str.split()
            words.append(word)
            iob.append(ner)
        bilou = iob_to_bilou(iob)
        tokens = create_tokens(words)
        sents.append((tokens, NERAnnotation.from_bilous(bilou, entity_types)))
    return sents


def iob_to_bilou(tags):
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
