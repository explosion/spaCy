# encoding: utf8

__all__ = [
    'ex_attr',
    'JapaneseCorrector',
    'correct_dep',
    'set_bunsetu_bi_type',
]


def ex_attr(token):
    return token._


class JapaneseCorrector:
    def __init__(self, nlp, **cfg):
        self.nlp = nlp

    def __call__(self, doc):
        correct_dep(doc)
        set_bunsetu_bi_type(doc)
        return doc


def merge_range(doc, token):
    if token.i == token.head.i:
        return None
    else:
        for i in range(token.i + 1, token.head.i) if token.i < token.head.i else range(token.head.i + 1, token.i):
            t = doc[i]
            if t.head.i < token.i or token.head.i < t.head.i or not t.dep == token.dep:
                return None
        head = token.head
        while token.i <= head.head.i <= token.head.i:
            head = head.head
        return (token.i, token.head.i + 1, head) if token.i < token.head.i else (token.head.i, token.i + 1, head)


def correct_dep(doc):
    with doc.retokenize() as retokenizer:
        for i in range(len(doc)):
            token = doc[i]
            label = token.dep_
            p = label.rfind('_as_')
            if p >= 0:
                corrected_pos = label[p + 4:]
                if len(corrected_pos) > 0:
                    token.pos_ = corrected_pos
                token.dep_ = label[0:p]
            elif label.startswith('as_'):
                corrected_pos = label[3:]
                m = merge_range(doc, token)
                if m is not None:
                    begin, end, head = m
                    tag = head.tag_
                    inf = ex_attr(head).inf
                    try:
                        retokenizer.merge(doc[begin:begin + 2], attrs={'POS': corrected_pos, 'TAG': tag})
                        ex_attr(doc[begin]).inf = inf
                        continue
                    except ValueError:
                        pass
                token.head.pos_ = corrected_pos
                token.pos_ = corrected_pos
                token.dep_ = 'dep'


FUNC_POS = {
    'AUX', 'ADP', 'SCONJ', 'CCONJ', 'PART',
}


FUNC_DEP = {
    'compound', 'case', 'mark', 'cc', 'aux', 'cop', 'nummod', 'amod', 'nmod', 'advmod', 'dep',
}


def set_bunsetu_bi_type(doc):
    if len(doc) == 0:
        ex_attr(doc).clauses = []
        return doc

    continuous = [None] * len(doc)
    head = None
    for t in doc:
        # backward dependencies with functional relation labels
        if head is not None and (
                head == t.head.i or t.i == t.head.i + 1
        ) and (
                t.pos_ in FUNC_POS or
                t.dep_ in FUNC_DEP or
                t.dep_ == 'punct' and t.tag_.find('括弧開') < 0  # except open parenthesis
        ):
            if head < t.head.i:
                head = t.head.i
            continuous[head] = head
            continuous[t.i] = head
        else:
            head = t.i
    # print(continuous)
    head = None
    for t in reversed(doc):
        # backward dependencies with functional relation labels
        if head is not None and continuous[t.i] is None and head == t.head.i and(t.dep_ in {
            'compound', 'nummod', 'amod', 'aux',
        } or (
            t.dep_ == 'punct' and t.tag_.find('括弧開') >= 0  # open parenthesis
        )):
            continuous[t.i] = head
        else:
            head = t.i
    # print(continuous)
    head = None
    for t in doc:
        if continuous[t.i] is None:
            if head is None or t.pos_ in {'VERB', 'ADJ', 'ADV', 'INTJ'}:
                head = t.i
            continuous[t.i] = head
        else:
            head = None
    # print(continuous)

    '''
    for ne in doc.ents:  # NE spans should not be divided
        start = ne.start
        c = continuous[ne.start]
        for i in reversed(range(ne.start)):
            if continuous[i] == c:
                start = i
            else:
                break
        end = ne.end
        c = continuous[ne.end - 1]
        for i in range(ne.end, len(doc)):
            if continuous[i] == c:
                end = i + 1
            else:
                break
        outer_head = None
        for i in range(start, end):
            t = doc[i]
            if i == t.head.i or not (start <= t.head.i < end):
                if outer_head is None:
                    outer_head = i
                else:
                    break
        else:
            for i in range(start, end):
                continuous[i] = outer_head
    # print(continuous)
    '''

    for t, bi in zip(doc, ['B'] + [
        'I' if continuous[i - 1] == continuous[i] else 'B' for i in range(1, len(continuous))
    ]):
        ex_attr(t).bunsetu_bi_label = bi

    position_type = [
        'ROOT' if t.i == t.head.i else
        ('NO_HEAD' if t.dep_ == 'punct' else 'SEM_HEAD') if t.i == c else
        'FUNC' if t.i > c and t.pos_ in FUNC_POS else
        'CONT' for t, c in zip(doc, continuous)
    ]
    prev_c = None
    for t, pt, c in zip(reversed(doc), reversed(position_type), reversed(continuous)):
        if pt == 'FUNC':
            if prev_c is None or prev_c != c:
                ex_attr(t).bunsetu_position_type = 'SYN_HEAD'
                prev_c = c
            else:
                ex_attr(t).bunsetu_position_type = pt
        else:
            ex_attr(t).bunsetu_position_type = pt
            prev_c = None
