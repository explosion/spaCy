# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher


def test_issue615(en_tokenizer):
    def merge_phrases(matcher, doc, i, matches):
        """Merge a phrase. We have to be careful here because we'll change the
        token indices. To avoid problems, merge all the phrases once we're called
        on the last match."""

        if i != len(matches)-1:
            return None
        # Get Span objects
        spans = [(ent_id, ent_id, doc[start : end]) for ent_id, start, end in matches]
        for ent_id, label, span in spans:
            span.merge(tag='NNP' if label else span.root.tag_, lemma=span.text,
                label=label)
            doc.ents = doc.ents + ((label, span.start, span.end),)

    text = "The golf club is broken"
    pattern = [{'ORTH': "golf"}, {'ORTH': "club"}]
    label = "Sport_Equipment"

    doc = en_tokenizer(text)
    matcher = Matcher(doc.vocab)
    matcher.add(label, merge_phrases, pattern)
    match = matcher(doc)
    entities = list(doc.ents)

    assert entities != [] #assertion 1
    assert entities[0].label != 0 #assertion 2
