'''Serve pointers to Lexeme structs, given strings. Maintain a reverse index,
so that strings can be retrieved from hashes.  Use 64-bit hash values and
boldly assume no collisions.
'''
from __future__ import unicode_literals


from libc.stdint cimport uint64_t


cimport spacy

import re

from spacy import orth

TAG_THRESH = 0.5
UPPER_THRESH = 0.2
LOWER_THRESH = 0.5
TITLE_THRESH = 0.7

NR_FLAGS = 0

OFT_UPPER = NR_FLAGS; NR_FLAGS += 1
OFT_LOWER = NR_FLAGS; NR_FLAGS += 1
OFT_TITLE = NR_FLAGS; NR_FLAGS += 1

IS_ALPHA = NR_FLAGS; NR_FLAGS += 1
IS_DIGIT = NR_FLAGS; NR_FLAGS += 1
IS_PUNCT = NR_FLAGS; NR_FLAGS += 1
IS_SPACE = NR_FLAGS; NR_FLAGS += 1
IS_ASCII = NR_FLAGS; NR_FLAGS += 1
IS_TITLE = NR_FLAGS; NR_FLAGS += 1
IS_LOWER = NR_FLAGS; NR_FLAGS += 1
IS_UPPER = NR_FLAGS; NR_FLAGS += 1

CAN_PUNCT = NR_FLAGS; NR_FLAGS += 1
CAN_CONJ = NR_FLAGS; NR_FLAGS += 1
CAN_NUM = NR_FLAGS; NR_FLAGS += 1
CAN_DET = NR_FLAGS; NR_FLAGS += 1
CAN_ADP = NR_FLAGS; NR_FLAGS += 1
CAN_ADJ = NR_FLAGS; NR_FLAGS += 1
CAN_ADV = NR_FLAGS; NR_FLAGS += 1
CAN_VERB = NR_FLAGS; NR_FLAGS += 1
CAN_NOUN = NR_FLAGS; NR_FLAGS += 1
CAN_PDT = NR_FLAGS; NR_FLAGS += 1
CAN_POS = NR_FLAGS; NR_FLAGS += 1
CAN_PRON = NR_FLAGS; NR_FLAGS += 1
CAN_PRT = NR_FLAGS; NR_FLAGS += 1


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
    """Fully PTB compatible English tokenizer, tightly coupled to lexicon.

    Attributes:
        name (unicode): The two letter code used by Wikipedia for the language.
        lexicon (Lexicon): The lexicon. Exposes the lookup method.
    """


    def __cinit__(self, name):
        flag_funcs = [0 for _ in range(NR_FLAGS)]
        
        flag_funcs[OFT_UPPER] = orth.oft_case('upper', UPPER_THRESH)
        flag_funcs[OFT_LOWER] = orth.oft_case('lower', LOWER_THRESH)
        flag_funcs[OFT_TITLE] = orth.oft_case('title', TITLE_THRESH)
        
        flag_funcs[IS_ALPHA] = orth.is_alpha
        flag_funcs[IS_DIGIT] = orth.is_digit
        flag_funcs[IS_PUNCT] = orth.is_punct
        flag_funcs[IS_SPACE] = orth.is_space
        flag_funcs[IS_TITLE] = orth.is_title
        flag_funcs[IS_LOWER] = orth.is_lower
        flag_funcs[IS_UPPER] = orth.is_upper
        
        flag_funcs[CAN_PUNCT] = orth.can_tag('PUNCT', TAG_THRESH)
        flag_funcs[CAN_CONJ] = orth.can_tag('CONJ', TAG_THRESH)
        flag_funcs[CAN_NUM] = orth.can_tag('NUM', TAG_THRESH)
        flag_funcs[CAN_DET] = orth.can_tag('DET', TAG_THRESH)
        flag_funcs[CAN_ADP] = orth.can_tag('ADP', TAG_THRESH)
        flag_funcs[CAN_ADJ] = orth.can_tag('ADJ', TAG_THRESH)
        flag_funcs[CAN_VERB] = orth.can_tag('VERB', TAG_THRESH)
        flag_funcs[CAN_NOUN] = orth.can_tag('NOUN', TAG_THRESH)
        flag_funcs[CAN_PDT] = orth.can_tag('PDT', TAG_THRESH)
        flag_funcs[CAN_POS] = orth.can_tag('POS', TAG_THRESH)
        flag_funcs[CAN_PRT] = orth.can_tag('PRT', TAG_THRESH)
        
        Language.__init__(self, name, flag_funcs)


    cdef list _split(self, unicode chunk):
        strings = nltk_regex_tokenize(chunk)
        if strings[-1] == '.':
            strings.pop()
            strings[-1] += '.'
        assert strings
        return strings
    

PTB3 = PennTreebank3('ptb3')
