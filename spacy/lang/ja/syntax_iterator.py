# coding: utf8
from __future__ import unicode_literals

from ...symbols import ADJ, ADV, DET, NOUN, PART, PROPN, PRON, SCONJ, VERB


def noun_chunks(obj):
    doc = obj.doc  # Ensure works on both Doc and Span.
    phrases = []
    phrase_type = None
    phrase = None
    prev = None
    prev_dep = None
    prev_head = None
    for t in doc:
        pos = t.pos
        tag = t.tag_
        dep = t.dep_
        head = t.head.i
        while True:
            if phrase_type is None:
                if pos in {NOUN, VERB, ADJ}:
                    phrase = [t]
                    phrase_type = pos
                elif pos in {VERB}:
                    phrases[ADV].append([t])
                break
            if phrase_type == NOUN:  # TODO refinement needed
                if (
                    pos == NOUN and (prev_head == t.i or prev_head == head) and prev_dep == 'compound'
                ) or (
                    pos == PART and (prev == head or prev_head == head) and dep == 'mark'
                ):
                    phrase.append(t)
                    break
            elif phrase_type == VERB:  # TODO refinement needed
                if pos in {SCONJ}:
                    phrase.append(t)
                    break
            elif phrase_type == ADJ and tag != '連体詞':
                if (
                    pos == NOUN and (prev_head == t.i or prev_head == head) and prev_dep in {'amod', 'compound'}
                ) or (
                    pos == PART and (prev == head or prev_head == head) and dep == 'mark'
                ):
                    phrase.append(t)
                    break
            if phrase:
                phrases.append((phrase_type, phrase))
                phrase_type = None
                phrase = None
        prev = t.i
        prev_dep = t.dep_
        prev_head = head

    # TODO Is this correct way to yield non-NP phrases?
    phrase_labels = {
        NOUN: doc.vocab.strings.add("NP"),
        VERB: doc.vocab.strings.add("VP"),
        ADV: doc.vocab.strings.add("ADVP"),
        ADJ: doc.vocab.strings.add("ADJP"),
    }
    print(phrases)
    for phrase_type, phrase in phrases:
        yield phrase[0].i, phrase[-1].i + 1, phrase_labels[phrase_type]


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
