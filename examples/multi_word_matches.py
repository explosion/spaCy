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
import codecs

import plac

from preshed.maps import PreshMap
from preshed.counter import PreshCounter
from spacy.strings import hash_string
from spacy.en import English
from spacy.matcher import PhraseMatcher


def read_gazetteer(tokenizer, loc, n=-1):
    for i, line in enumerate(open(loc)):
        phrase = literal_eval('u' + line.strip())
        if ' (' in phrase and phrase.endswith(')'):
            phrase = phrase.split(' (', 1)[0]
        if i >= n:
            break
        phrase = tokenizer(phrase)
        if all((t.is_lower and t.prob >= -10) for t in phrase):
            continue
        if len(phrase) >= 2:
            yield phrase


def read_text(bz2_loc):
    with BZ2File(bz2_loc) as file_:
        for line in file_:
            yield line.decode('utf8')


def get_matches(tokenizer, phrases, texts, max_length=6):
    matcher = PhraseMatcher(tokenizer.vocab, phrases, max_length=max_length)
    print("Match")
    for text in texts:
        doc = tokenizer(text)
        matches = matcher(doc)
        for mwe in doc.ents:
            yield mwe


def main(patterns_loc, text_loc, counts_loc, n=10000000):
    nlp = English(parser=False, tagger=False, entity=False)
    print("Make matcher")
    phrases = read_gazetteer(nlp.tokenizer, patterns_loc, n=n)
    counts = PreshCounter()
    t1 = time.time()
    for mwe in get_matches(nlp.tokenizer, phrases, read_text(text_loc)):
        counts.inc(hash_string(mwe.text), 1)
    t2 = time.time()
    print("10m tokens in %d s" % (t2 - t1))
    
    with codecs.open(counts_loc, 'w', 'utf8') as file_:
        for phrase in read_gazetteer(nlp.tokenizer, patterns_loc, n=n):
            text = phrase.string
            key = hash_string(text)
            count = counts[key]
            if count != 0:
                file_.write('%d\t%s\n' % (count, text))
    

if __name__ == '__main__':
    if False:
        import cProfile
        import pstats
        cProfile.runctx("plac.call(main)", globals(), locals(), "Profile.prof")
        s = pstats.Stats("Profile.prof")
        s.strip_dirs().sort_stats("time").print_stats()
    else:
        plac.call(main)
