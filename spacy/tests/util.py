# coding: utf-8
from __future__ import unicode_literals

from ..tokens import Doc
from ..attrs import ORTH, POS, HEAD, DEP


def get_doc(vocab, words=[], pos=None, heads=None, deps=None, tags=None, ents=None):
    """Create Doc object from given vocab, words and annotations."""
    pos = pos or [''] * len(words)
    heads = heads or [0] * len(words)
    deps = deps or [''] * len(words)

    doc = Doc(vocab, words=words)
    attrs = doc.to_array([POS, HEAD, DEP])
    for i, (p, head, dep) in enumerate(zip(pos, heads, deps)):
        attrs[i, 0] = doc.vocab.strings[p]
        attrs[i, 1] = head
        attrs[i, 2] = doc.vocab.strings[dep]
    doc.from_array([POS, HEAD, DEP], attrs)
    if ents:
        doc.ents = [(ent_id, doc.vocab.strings[label], start, end) for ent_id, label, start, end in ents]
    if tags:
        for token in doc:
            token.tag_ = tags[token.i]
    return doc


def apply_transition_sequence(parser, doc, sequence):
    """Perform a series of pre-specified transitions, to put the parser in a
    desired state."""
    for action_name in sequence:
        if '-' in action_name:
            move, label = action_name.split('-')
            parser.add_label(label)
    with parser.step_through(doc) as stepwise:
        for transition in sequence:
            stepwise.transition(transition)
