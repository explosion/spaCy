"""Match a large set of multi-word expressions in O(1) time.

The idea is to associate each word in the vocabulary with a tag, noting whether
they begin, end, or are inside at least one pattern. An additional tag is used
for single-word patterns. Complete patterns are also stored in a hash set.

When we process a document, we look up the words in the vocabulary, to associate
the words with the tags.  We then search for tag-sequences that correspond to
valid candidates. Finally, we look up the candidates in the hash set.

For instance, to search for the phrases "Barack Hussein Obama" and "Hilary Clinton", we
would associate "Barack" and "Hilary" with the B tag, Hussein with the I tag,
and Obama and Clinton with the L tag.

The document "Barack Clinton and Hilary Clinton" would have the tag sequence
[{B}, {L}, {}, {B}, {L}], so we'd get two matches. However, only the second candidate
is in the phrase dictionary, so only one is returned as a match.

The algorithm is O(n) at run-time for document of length n because we're only ever
matching over the tag patterns. So no matter how many phrases we're looking for,
our pattern set stays very small (exact size depends on the maximum length we're
looking for, as the query language currently has no quantifiers)
"""
from __future__ import print_function, unicode_literals, division

import plac

from preshed.maps import PreshMap
from spacy.strings import hash_string
from spacy.en import English
from spacy.matcher import Matcher

from spacy.attrs import FLAG63 as U_ENT
from spacy.attrs import FLAG62 as L_ENT
from spacy.attrs import FLAG61 as I_ENT
from spacy.attrs import FLAG60 as B_ENT


def get_bilou(length):
    if length == 1:
        return [U_ENT]
    else:
        return [B_ENT] + [I_ENT] * (length - 2) + [L_ENT]


def make_matcher(vocab, max_length):
    abstract_patterns = []
    for length in range(1, max_length+1):
        abstract_patterns.append([{tag: True} for tag in get_bilou(length)])
    return Matcher(vocab, {'Candidate': ('CAND', {}, abstract_patterns)})


def get_matches(matcher, pattern_ids, doc):
    matches = []
    for label, start, end in matcher(doc):
        candidate = doc[start : end]
        if pattern_ids[hash_string(candidate.text)] == True:
            start = candidate[0].idx
            end = candidate[-1].idx + len(candidate[-1])
            matches.append((start, end, candidate.root.tag_, candidate.text))
    return matches


def merge_matches(doc, matches):
    for start, end, tag, text in matches:
        doc.merge(start, end, tag, text, 'MWE')


def main():
    nlp = English(parser=False, tagger=False, entity=False)

    gazetteer = [u'M.I.A.', 'Shiny Happy People', 'James E. Jones']
    example_text = u'The artist M.I.A. did a cover of Shiny Happy People. People is not an entity.'
    pattern_ids = PreshMap()
    max_length = 0
    for pattern_str in gazetteer:
        pattern = nlp.tokenizer(pattern_str)
        bilou_tags = get_bilou(len(pattern))
        for word, tag in zip(pattern, bilou_tags):
            lexeme = nlp.vocab[word.orth]
            lexeme.set_flag(tag, True)
        pattern_ids[hash_string(pattern.text)] = True
        max_length = max(max_length, len(pattern))

    matcher = make_matcher(nlp.vocab, max_length)

    doc = nlp(example_text)
    matches = get_matches(matcher, pattern_ids, doc)
    merge_matches(doc, matches)
    for token in doc:
        print(token.text, token.ent_type_)
    

if __name__ == '__main__':
    plac.call(main)
