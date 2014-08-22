'''Serve pointers to Lexeme structs, given strings. Maintain a reverse index,
so that strings can be retrieved from hashes.  Use 64-bit hash values and
boldly assume no collisions.
'''
from __future__ import unicode_literals


from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t


cimport spacy

import re

# List of contractions adapted from Robert MacIntyre's tokenizer.
CONTRACTIONS2 = [re.compile(r"(?i)\b(can)(not)\b"),
                 re.compile(r"(?i)\b(d)('ye)\b"),
                 re.compile(r"(?i)\b(gim)(me)\b"),
                 re.compile(r"(?i)\b(gon)(na)\b"),
                 re.compile(r"(?i)\b(got)(ta)\b"),
                 re.compile(r"(?i)\b(lem)(me)\b"),
                 re.compile(r"(?i)\b(mor)('n)\b"),
                 re.compile(r"(?i)\b(wan)(na) ")]

CONTRACTIONS3 = [re.compile(r"(?i) ('t)(is)\b"),
                 re.compile(r"(?i) ('t)(was)\b")]

CONTRACTIONS4 = [re.compile(r"(?i)\b(whad)(dd)(ya)\b"),
                 re.compile(r"(?i)\b(wha)(t)(cha)\b")]

def nltk_regex_tokenize(text):
    # Implementation taken from NLTK 3.0, based on tokenizer.sed
    
    #starting quotes
    text = re.sub(r'^\"', r'``', text)
    text = re.sub(r'(``)', r' \1 ', text)
    text = re.sub(r'([ (\[{<])"', r'\1 `` ', text)

    #punctuation
    text = re.sub(r'([:,])([^\d])', r' \1 \2', text)
    text = re.sub(r'\.\.\.', r' ... ', text)
    text = re.sub(r'[;@#$%&]', r' \g<0> ', text)
    text = re.sub(r'([^\.])(\.)([\]\)}>"\']*)\s*$', r'\1 \2\3 ', text)
    text = re.sub(r'[?!]', r' \g<0> ', text)

    text = re.sub(r"([^'])' ", r"\1 ' ", text)

    #parens, brackets, etc.
    text = re.sub(r'[\]\[\(\)\{\}\<\>]', r' \g<0> ', text)
    text = re.sub(r'--', r' -- ', text)

    #add extra space to make things easier
    text = " " + text + " "

    #ending quotes
    text = re.sub(r'"', " '' ", text)
    text = re.sub(r'(\S)(\'\')', r'\1 \2 ', text)

    text = re.sub(r"([^' ])('[sS]|'[mM]|'[dD]|') ", r"\1 \2 ", text)
    text = re.sub(r"([^' ])('ll|'LL|'re|'RE|'ve|'VE|n't|N'T) ", r"\1 \2 ",
                  text)

    for regexp in CONTRACTIONS2:
        text = regexp.sub(r' \1 \2 ', text)
    for regexp in CONTRACTIONS3:
        text = regexp.sub(r' \1 \2 ', text)

    # We are not using CONTRACTIONS4 since
    # they are also commented out in the SED scripts
    # for regexp in self.CONTRACTIONS4:
    #     text = regexp.sub(r' \1 \2 \3 ', text)

    return text.split()


cdef class PennTreebank3(Language):
    cpdef list find_substrings(self, unicode chunk):
        strings = nltk_regex_tokenize(chunk)
        assert strings
        return strings
    

cdef PennTreebank3 PTB3 = PennTreebank3('ptb3')

cpdef Tokens tokenize(unicode string):
    return PTB3.tokenize(string)


cpdef LexID lookup(unicode string) except 0:
    return <LexID>PTB3.lookup(string)


cpdef unicode unhash(StringHash hash_value):
    return PTB3.unhash(hash_value)
