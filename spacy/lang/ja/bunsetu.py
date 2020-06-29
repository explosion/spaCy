# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS


POS_PHRASE_MAP = {
    "NOUN": "NP",
    "NUM": "NP",
    "PRON": "NP",
    "PROPN": "NP",

    "VERB": "VP",

    "ADJ": "ADJP",

    "ADV": "ADVP",

    "CCONJ": "CCONJP",
}


# return value: [(bunsetu_tokens, phrase_type={'NP', 'VP', 'ADJP', 'ADVP'}, phrase_tokens)]
def yield_bunsetu(doc, debug=False):
    bunsetu = []
    bunsetu_may_end = False
    phrase_type = None
    phrase = None
    prev = None
    prev_tag = None
    prev_dep = None
    prev_head = None
    for t in doc:
        pos = t.pos_
        pos_type = POS_PHRASE_MAP.get(pos, None)
        tag = t.tag_
        dep = t.dep_
        head = t.head.i
        if debug:
            print(t.i, t.orth_, pos, pos_type, dep, head, bunsetu_may_end, phrase_type, phrase, bunsetu)

        # DET is always an individual bunsetu
        if pos == "DET":
            if bunsetu:
                yield bunsetu, phrase_type, phrase
            yield [t], None, None
            bunsetu = []
            bunsetu_may_end = False
            phrase_type = None
            phrase = None

        # PRON or Open PUNCT always splits bunsetu
        elif tag == "補助記号-括弧開":
            if bunsetu:
                yield bunsetu, phrase_type, phrase
            bunsetu = [t]
            bunsetu_may_end = True
            phrase_type = None
            phrase = None

        # bunsetu head not appeared
        elif phrase_type is None:
            if bunsetu and prev_tag == "補助記号-読点":
                yield bunsetu, phrase_type, phrase
                bunsetu = []
                bunsetu_may_end = False
                phrase_type = None
                phrase = None
            bunsetu.append(t)
            if pos_type:  # begin phrase
                phrase = [t]
                phrase_type = pos_type
                if pos_type in {"ADVP", "CCONJP"}:
                    bunsetu_may_end = True

        # entering new bunsetu
        elif pos_type and (
            pos_type != phrase_type or  # different phrase type arises
            bunsetu_may_end  # same phrase type but bunsetu already ended
        ):
            # exceptional case: NOUN to VERB
            if phrase_type == "NP" and pos_type == "VP" and prev_dep == 'compound' and prev_head == t.i:
                bunsetu.append(t)
                phrase_type = "VP"
                phrase.append(t)
            # exceptional case: VERB to NOUN
            elif phrase_type == "VP" and pos_type == "NP" and (
                    prev_dep == 'compound' and prev_head == t.i or
                    dep == 'compound' and prev == head or
                    prev_dep == 'nmod' and prev_head == t.i
            ):
                bunsetu.append(t)
                phrase_type = "NP"
                phrase.append(t)
            else:
                yield bunsetu, phrase_type, phrase
                bunsetu = [t]
                bunsetu_may_end = False
                phrase_type = pos_type
                phrase = [t]

        # NOUN bunsetu
        elif phrase_type == "NP":
            bunsetu.append(t)
            if not bunsetu_may_end and ((
                (pos_type == "NP" or pos == "SYM") and (prev_head == t.i or prev_head == head) and prev_dep in {'compound', 'nummod'}
            ) or (
                pos == "PART" and (prev == head or prev_head == head) and dep == 'mark'
            )):
                phrase.append(t)
            else:
                bunsetu_may_end = True

        # VERB bunsetu
        elif phrase_type == "VP":
            bunsetu.append(t)
            if not bunsetu_may_end and pos == "VERB" and prev_head == t.i and prev_dep == 'compound':
                phrase.append(t)
            else:
                bunsetu_may_end = True

        # ADJ bunsetu
        elif phrase_type == "ADJP" and tag != '連体詞':
            bunsetu.append(t)
            if not bunsetu_may_end and ((
                pos == "NOUN" and (prev_head == t.i or prev_head == head) and prev_dep in {'amod', 'compound'}
            ) or (
                pos == "PART" and (prev == head or prev_head == head) and dep == 'mark'
            )):
                phrase.append(t)
            else:
                bunsetu_may_end = True

        # other bunsetu
        else:
            bunsetu.append(t)

        prev = t.i
        prev_tag = t.tag_
        prev_dep = t.dep_
        prev_head = head

    if bunsetu:
        yield bunsetu, phrase_type, phrase
