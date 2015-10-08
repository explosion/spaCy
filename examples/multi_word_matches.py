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
from ast import literal_eval
from bz2 import BZ2File
import time
import math

import plac

from preshed.maps import PreshMap
from spacy.strings import hash_string
from spacy.en import English
from spacy.matcher import Matcher

from spacy.attrs import FLAG63 as B_ENT
from spacy.attrs import FLAG62 as L_ENT
from spacy.attrs import FLAG61 as I_ENT

from spacy.attrs import FLAG60 as B2_ENT
from spacy.attrs import FLAG59 as B3_ENT
from spacy.attrs import FLAG58 as B4_ENT
from spacy.attrs import FLAG57 as B5_ENT
from spacy.attrs import FLAG56 as B6_ENT
from spacy.attrs import FLAG55 as B7_ENT
from spacy.attrs import FLAG54 as B8_ENT
from spacy.attrs import FLAG53 as B9_ENT
from spacy.attrs import FLAG52 as B10_ENT

from spacy.attrs import FLAG51 as I3_ENT
from spacy.attrs import FLAG50 as I4_ENT
from spacy.attrs import FLAG49 as I5_ENT
from spacy.attrs import FLAG48 as I6_ENT
from spacy.attrs import FLAG47 as I7_ENT
from spacy.attrs import FLAG46 as I8_ENT
from spacy.attrs import FLAG45 as I9_ENT
from spacy.attrs import FLAG44 as I10_ENT

from spacy.attrs import FLAG43 as L2_ENT
from spacy.attrs import FLAG42 as L3_ENT
from spacy.attrs import FLAG41 as L4_ENT
from spacy.attrs import FLAG40 as L5_ENT
from spacy.attrs import FLAG39 as L6_ENT
from spacy.attrs import FLAG38 as L7_ENT
from spacy.attrs import FLAG37 as L8_ENT
from spacy.attrs import FLAG36 as L9_ENT
from spacy.attrs import FLAG35 as L10_ENT


def get_bilou(length):
    if length == 1:
        return [U_ENT]
    elif length == 2:
        return [B2_ENT, L2_ENT]
    elif length == 3:
        return [B3_ENT, I3_ENT, L3_ENT]
    elif length == 4:
        return [B4_ENT, I4_ENT, I4_ENT, L4_ENT]
    elif length == 5:
        return [B5_ENT, I5_ENT, I5_ENT, L5_ENT]
    elif length == 6:
        return [B6_ENT, I6_ENT, I6_ENT, I6_ENT, I6_ENT, L6_ENT]
    elif length == 7:
        return [B7_ENT, I7_ENT, I7_ENT, I7_ENT, I7_ENT, I7_ENT, L7_ENT]
    elif length == 8:
        return [B8_ENT, I8_ENT, I8_ENT, I8_ENT, I8_ENT, I8_ENT, I8_ENT, L8_ENT]
    elif length == 9:
        return [B9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, L9_ENT]
    elif length == 10:
        return [B10_ENT, I10_ENT, I10_ENT, I10_ENT, I10_ENT, I10_ENT, I10_ENT, L10_ENT]


def make_matcher(vocab, max_length):
    abstract_patterns = []
    for length in range(2, max_length):
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


def read_gazetteer(loc):
    for line in open(loc):
        phrase = literal_eval('u' + line.strip())
        if ' (' in phrase and phrase.endswith(')'):
            phrase = phrase.split(' (', 1)[0]
        yield phrase

def read_text(bz2_loc):
    with BZ2File(bz2_loc) as file_:
        for line in file_:
            yield line.decode('utf8')

def main(patterns_loc, text_loc):
    nlp = English(parser=False, tagger=False, entity=False)
    
    pattern_ids = PreshMap()
    max_length = 10
    i = 0
    for pattern_str in read_gazetteer(patterns_loc):
        pattern = nlp.tokenizer(pattern_str)
        if len(pattern) < 2 or len(pattern) >= max_length:
            continue
        bilou_tags = get_bilou(len(pattern))
        for word, tag in zip(pattern, bilou_tags):
            lexeme = nlp.vocab[word.orth]
            lexeme.set_flag(tag, True)
        pattern_ids[hash_string(pattern.text)] = True
        i += 1
        if i >= 10000001:
            break

    matcher = make_matcher(nlp.vocab, max_length)

    t1 = time.time()
        
    for text in read_text(text_loc):
        doc = nlp.tokenizer(text)
        matches = get_matches(matcher, pattern_ids, doc)
        merge_matches(doc, matches)
    t2 = time.time()
    print('10 ^ %d patterns took %d s' % (round(math.log(i, 10)), t2-t1))

    

if __name__ == '__main__':
    plac.call(main)
