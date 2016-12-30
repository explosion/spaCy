# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA


TOKENIZER_EXCEPTIONS = {
    "and/or": [
        {ORTH: "and/or", LEMMA: "and/or", TAG: "CC"}
    ],

    "Theydve": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "shouldn't've": [
        {ORTH: "should"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "There'll": [
        {ORTH: "There"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "howll": [
        {ORTH: "how"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "Hadn't've": [
        {ORTH: "Had", LEMMA: "have", TAG: "VBD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "who'll": [
        {ORTH: "who"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "aint": [
        {ORTH: "ai", TAG: "VBP", "number": 2, LEMMA: "be"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    " ": [
        {TAG: "SP", ORTH: " "}
    ],

    "Shouldnt": [
        {ORTH: "Should"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "when's": [
        {ORTH: "when"},
        {ORTH: "'s", LEMMA: "be"}
    ],

    "Didnt": [
        {ORTH: "Did", LEMMA: "do", TAG: "VBD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "itll": [
        {ORTH: "it", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "Who're": [
        {ORTH: "Who"},
        {ORTH: "'re", LEMMA: "be"}
    ],

    "Ain't": [
        {ORTH: "Ai", TAG: "VBP", "number": 2, LEMMA: "be"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Can't": [
        {ORTH: "Ca", LEMMA: "can", TAG: "MD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Whyre": [
        {ORTH: "Why"},
        {ORTH: "re"}
    ],

    "Aren't": [
        {ORTH: "Are", TAG: "VBP", "number": 2, LEMMA: "be"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Neednt": [
        {ORTH: "Need"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "should've": [
        {ORTH: "should"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "shouldn't": [
        {ORTH: "should"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Idve": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "weve": [
        {ORTH: "we"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Ive": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "they'd": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "Youdve": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "theyve": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Weren't": [
        {ORTH: "Were"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "werent": [
        {ORTH: "were"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "whyre": [
        {ORTH: "why"},
        {ORTH: "re"}
    ],

    "I'm": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'m", TAG: "VBP", "tenspect": 1, "number": 1, LEMMA: "be"}
    ],

    "She'd've": [
        {ORTH: "She", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "not've": [
        {ORTH: "not", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "we'll": [
        {ORTH: "we"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "Don't": [
        {ORTH: "Do", LEMMA: "do"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Whyll": [
        {ORTH: "Why"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "they've": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "wasn't": [
        {ORTH: "was"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "could've": [
        {ORTH: "could", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "what've": [
        {ORTH: "what"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "havent": [
        {ORTH: "have", TAG: "VB"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Who've": [
        {ORTH: "Who"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Shan't": [
        {ORTH: "Sha", LEMMA: "shall"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "i'll": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "you'd": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "whens": [
        {ORTH: "when"},
        {ORTH: "s", LEMMA: "be"}
    ],

    "whys": [
        {ORTH: "why"},
        {ORTH: "s"}
    ],

    "Whereve": [
        {ORTH: "Where"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "\u00a0": [
        {ORTH: "\u00a0", TAG: "SP", LEMMA: "  "}
    ],

    "there'd": [
        {ORTH: "there"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "hadn't've": [
        {ORTH: "had", LEMMA: "have", TAG: "VBD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "whatll": [
        {ORTH: "what"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "wouldn't've": [
        {ORTH: "would"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "there's": [
        {ORTH: "there"},
        {ORTH: "'s"}
    ],

    "Who'll": [
        {ORTH: "Who"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "youll": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "wouldve": [
        {ORTH: "would"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Wouldnt": [
        {ORTH: "Would"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Thered": [
        {ORTH: "There"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "Youre": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "re", LEMMA: "be"}
    ],

    "Couldn't've": [
        {ORTH: "Could", TAG: "MD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "who're": [
        {ORTH: "who"},
        {ORTH: "'re", LEMMA: "be"}
    ],

    "Whys": [
        {ORTH: "Why"},
        {ORTH: "s"}
    ],

    "mightn't've": [
        {ORTH: "might"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Wholl": [
        {ORTH: "Who"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "hadn't": [
        {ORTH: "had", LEMMA: "have", TAG: "VBD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Havent": [
        {ORTH: "Have", TAG: "VB"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Whatve": [
        {ORTH: "What"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Thats": [
        {ORTH: "That"},
        {ORTH: "s"}
    ],

    "Howll": [
        {ORTH: "How"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "wouldn't": [
        {ORTH: "would"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "You'll": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "Cant": [
        {ORTH: "Ca", LEMMA: "can", TAG: "MD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "i'd": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "weren't": [
        {ORTH: "were"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "would've": [
        {ORTH: "would"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "i'm": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'m", TAG: "VBP", "tenspect": 1, "number": 1, LEMMA: "be"}
    ],

    "why'll": [
        {ORTH: "why"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "we'd've": [
        {ORTH: "we"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Shouldve": [
        {ORTH: "Should"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "can't": [
        {ORTH: "ca", LEMMA: "can", TAG: "MD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "thats": [
        {ORTH: "that"},
        {ORTH: "s"}
    ],

    "Hes": [
        {ORTH: "He", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "s"}
    ],

    "Needn't": [
        {ORTH: "Need"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "It's": [
        {ORTH: "It", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'s"}
    ],

    "Why're": [
        {ORTH: "Why"},
        {ORTH: "'re", LEMMA: "be"}
    ],

    "Hed": [
        {ORTH: "He", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "Mt.": [
        {ORTH: "Mt.", LEMMA: "Mount"}
    ],

    "couldn't": [
        {ORTH: "could", TAG: "MD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "What've": [
        {ORTH: "What"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "It'd": [
        {ORTH: "It", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "theydve": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "aren't": [
        {ORTH: "are", TAG: "VBP", "number": 2, LEMMA: "be"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Mightn't": [
        {ORTH: "Might"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "'S": [
        {ORTH: "'S", LEMMA: "'s"}
    ],

    "I've": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Whered": [
        {ORTH: "Where"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "Itdve": [
        {ORTH: "It", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "I'ma": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ma"}
    ],

    "whos": [
        {ORTH: "who"},
        {ORTH: "s"}
    ],

    "They'd": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "What'll": [
        {ORTH: "What"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "You've": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Mustve": [
        {ORTH: "Must"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "whod": [
        {ORTH: "who"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "mightntve": [
        {ORTH: "might"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "I'd've": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Must've": [
        {ORTH: "Must"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "it'd": [
        {ORTH: "it", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "what're": [
        {ORTH: "what"},
        {ORTH: "'re", LEMMA: "be", NORM: "are"}
    ],

    "Wasn't": [
        {ORTH: "Was"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "what's": [
        {ORTH: "what"},
        {ORTH: "'s"}
    ],

    "he'd've": [
        {ORTH: "he", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "She'd": [
        {ORTH: "She", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "shedve": [
        {ORTH: "she", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "ain't": [
        {ORTH: "ai", TAG: "VBP", "number": 2, LEMMA: "be"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "She's": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'s"}
    ],

    "i'd've": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "We'd've": [
        {ORTH: "We"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "must've": [
        {ORTH: "must"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "That's": [
        {ORTH: "That"},
        {ORTH: "'s"}
    ],

    "whatre": [
        {ORTH: "what"},
        {ORTH: "re"}
    ],

    "you'd've": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Dont": [
        {ORTH: "Do", LEMMA: "do"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "thered": [
        {ORTH: "there"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "Youd": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "couldn't've": [
        {ORTH: "could", TAG: "MD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Whens": [
        {ORTH: "When"},
        {ORTH: "s"}
    ],

    "Isnt": [
        {ORTH: "Is", LEMMA: "be", TAG: "VBZ"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "mightve": [
        {ORTH: "might"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "didnt": [
        {ORTH: "did", LEMMA: "do", TAG: "VBD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "ive": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "It'd've": [
        {ORTH: "It", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "\t": [
        {ORTH: "\t", TAG: "SP"}
    ],

    "Itll": [
        {ORTH: "It", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "didn't": [
        {ORTH: "did", LEMMA: "do", TAG: "VBD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "cant": [
        {ORTH: "ca", LEMMA: "can", TAG: "MD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "im": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "m", TAG: "VBP", "tenspect": 1, "number": 1, LEMMA: "be"}
    ],

    "they'd've": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Hadntve": [
        {ORTH: "Had", LEMMA: "have", TAG: "VBD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Weve": [
        {ORTH: "We"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Mightnt": [
        {ORTH: "Might"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "youdve": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Shedve": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "theyd": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "Cannot": [
        {ORTH: "Can", LEMMA: "can", TAG: "MD"},
        {ORTH: "not", LEMMA: "not", TAG: "RB"}
    ],

    "Hadn't": [
        {ORTH: "Had", LEMMA: "have", TAG: "VBD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "What're": [
        {ORTH: "What"},
        {ORTH: "'re", LEMMA: "be", NORM: "are"}
    ],

    "He'll": [
        {ORTH: "He", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "wholl": [
        {ORTH: "who"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "They're": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'re", LEMMA: "be", NORM: "are"}
    ],

    "shouldnt": [
        {ORTH: "should"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "\n": [
        {ORTH: "\n", TAG: "SP"}
    ],

    "whered": [
        {ORTH: "where"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "youve": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "notve": [
        {ORTH: "not", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "couldve": [
        {ORTH: "could", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "mustve": [
        {ORTH: "must"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Youve": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "therell": [
        {ORTH: "there"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "might've": [
        {ORTH: "might"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Mustn't": [
        {ORTH: "Must"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "wheres": [
        {ORTH: "where"},
        {ORTH: "s"}
    ],

    "they're": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'re", LEMMA: "be", NORM: "are"}
    ],

    "idve": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "hows": [
        {ORTH: "how"},
        {ORTH: "s"}
    ],

    "youre": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "re", LEMMA: "be", NORM: "are"}
    ],

    "Didn't": [
        {ORTH: "Did", LEMMA: "do", TAG: "VBD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Couldve": [
        {ORTH: "Could", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "cannot": [
        {ORTH: "can", LEMMA: "can", TAG: "MD"},
        {ORTH: "not", LEMMA: "not", TAG: "RB"}
    ],

    "Im": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "m", TAG: "VBP", "tenspect": 1, "number": 1, LEMMA: "be", NORM: "am"}
    ],

    "howd": [
        {ORTH: "how"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "you've": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "You're": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'re", LEMMA: "be", NORM: "are"}
    ],

    "she'll": [
        {ORTH: "she", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "Theyll": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "don't": [
        {ORTH: "do", LEMMA: "do"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "itd": [
        {ORTH: "it", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "Hedve": [
        {ORTH: "He", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "isnt": [
        {ORTH: "is", LEMMA: "be", TAG: "VBZ"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "won't": [
        {ORTH: "wo", LEMMA: "will"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "We're": [
        {ORTH: "We", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'re", LEMMA: "be", NORM: "are"}
    ],

    "\u2018S": [
        {ORTH: "\u2018S", LEMMA: "'s"}
    ],

    "\u2018s": [
        {ORTH: "\u2018s", LEMMA: "'s"}
    ],

    "dont": [
        {ORTH: "do", LEMMA: "do"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "ima": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ma"}
    ],

    "Let's": [
        {ORTH: "Let"},
        {ORTH: "'s", LEMMA: "us"}
    ],

    "he's": [
        {ORTH: "he", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'s"}
    ],

    "we've": [
        {ORTH: "we"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "What's": [
        {ORTH: "What"},
        {ORTH: "'s"}
    ],

    "Who's": [
        {ORTH: "Who"},
        {ORTH: "'s"}
    ],

    "hedve": [
        {ORTH: "he", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "he'd": [
        {ORTH: "he", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "When's": [
        {ORTH: "When"},
        {ORTH: "'s"}
    ],

    "Mightn't've": [
        {ORTH: "Might"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "We've": [
        {ORTH: "We"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Couldntve": [
        {ORTH: "Could", TAG: "MD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Who'd": [
        {ORTH: "Who"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "haven't": [
        {ORTH: "have", TAG: "VB"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "arent": [
        {ORTH: "are", TAG: "VBP", "number": 2, LEMMA: "be"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "You'd've": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Wouldn't": [
        {ORTH: "Would"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "who's": [
        {ORTH: "who"},
        {ORTH: "'s"}
    ],

    "Mightve": [
        {ORTH: "Might"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Theredve": [
        {ORTH: "There"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "theredve": [
        {ORTH: "there"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "who'd": [
        {ORTH: "who"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "Where's": [
        {ORTH: "Where"},
        {ORTH: "'s"}
    ],

    "wont": [
        {ORTH: "wo", LEMMA: "will"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "she'd've": [
        {ORTH: "she", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Should've": [
        {ORTH: "Should"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "theyre": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "re"}
    ],

    "Wouldntve": [
        {ORTH: "Would"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Where've": [
        {ORTH: "Where"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "mustn't": [
        {ORTH: "must"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "isn't": [
        {ORTH: "is", LEMMA: "be", TAG: "VBZ"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Aint": [
        {ORTH: "Ai", TAG: "VBP", "number": 2, LEMMA: "be"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "why's": [
        {ORTH: "why"},
        {ORTH: "'s"}
    ],

    "There'd": [
        {ORTH: "There"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "They'll": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "how'll": [
        {ORTH: "how"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "Wedve": [
        {ORTH: "We", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "couldntve": [
        {ORTH: "could", TAG: "MD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "There's": [
        {ORTH: "There"},
        {ORTH: "'s"}
    ],

    "we'd": [
        {ORTH: "we", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "Whod": [
        {ORTH: "Who"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "whatve": [
        {ORTH: "what"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Wouldve": [
        {ORTH: "Would"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "there'll": [
        {ORTH: "there"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "needn't": [
        {ORTH: "need"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "shouldntve": [
        {ORTH: "should"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "why're": [
        {ORTH: "why"},
        {ORTH: "'re", LEMMA: "be", NORM: "are"}
    ],

    "Doesnt": [
        {ORTH: "Does", LEMMA: "do", TAG: "VBZ"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "whereve": [
        {ORTH: "where"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "they'll": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "I'd": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "Might've": [
        {ORTH: "Might"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "mightnt": [
        {ORTH: "might"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Not've": [
        {ORTH: "Not", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "mightn't": [
        {ORTH: "might"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "you're": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'re", LEMMA: "be", NORM: "are"}
    ],

    "They've": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "what'll": [
        {ORTH: "what"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "Could've": [
        {ORTH: "Could", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Would've": [
        {ORTH: "Would"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Isn't": [
        {ORTH: "Is", LEMMA: "be", TAG: "VBZ"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "let's": [
        {ORTH: "let"},
        {ORTH: "'s", LEMMA: "us"}
    ],

    "She'll": [
        {ORTH: "She", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "You'd": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "wouldnt": [
        {ORTH: "would"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Why'll": [
        {ORTH: "Why"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "Where'd": [
        {ORTH: "Where"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "Theyre": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "re", LEMMA: "be", NORM: "are"}
    ],

    "Won't": [
        {ORTH: "Wo", LEMMA: "will"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Couldn't": [
        {ORTH: "Could", TAG: "MD"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "it's": [
        {ORTH: "it", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'s"}
    ],

    "it'll": [
        {ORTH: "it", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "They'd've": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Ima": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ma"}
    ],

    "gonna": [
        {ORTH: "gon", LEMMA: "go", NORM: "going"},
        {ORTH: "na", LEMMA: "to"}
    ],

    "Gonna": [
        {ORTH: "Gon", LEMMA: "go", NORM: "going"},
        {ORTH: "na", LEMMA: "to"}
    ],

    "whats": [
        {ORTH: "what"},
        {ORTH: "s"}
    ],

    "How's": [
        {ORTH: "How"},
        {ORTH: "'s"}
    ],

    "Shouldntve": [
        {ORTH: "Should"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "youd": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "Whatll": [
        {ORTH: "What"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "Wouldn't've": [
        {ORTH: "Would"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "How'd": [
        {ORTH: "How"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "doesnt": [
        {ORTH: "does", LEMMA: "do", TAG: "VBZ"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Shouldn't": [
        {ORTH: "Should"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "He'd've": [
        {ORTH: "He", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Mightntve": [
        {ORTH: "Might"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "couldnt": [
        {ORTH: "could", TAG: "MD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Haven't": [
        {ORTH: "Have", TAG: "VB"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "doesn't": [
        {ORTH: "does", LEMMA: "do", TAG: "VBZ"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Hasn't": [
        {ORTH: "Has"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "how's": [
        {ORTH: "how"},
        {ORTH: "'s"}
    ],

    "hes": [
        {ORTH: "he", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "s"}
    ],

    "he'll": [
        {ORTH: "he", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "hed": [
        {ORTH: "he", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "how'd": [
        {ORTH: "how"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "we're": [
        {ORTH: "we", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'re", LEMMA: "be", NORM :"are"}
    ],

    "Hadnt": [
        {ORTH: "Had", LEMMA: "have", TAG: "VBD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Shant": [
        {ORTH: "Sha", LEMMA: "shall"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Theyve": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Hows": [
        {ORTH: "How"},
        {ORTH: "s"}
    ],

    "We'll": [
        {ORTH: "We"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "i've": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Whove": [
        {ORTH: "Who"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "i'ma": [
        {ORTH: "i", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ma"}
    ],

    "Howd": [
        {ORTH: "How"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "hadnt": [
        {ORTH: "had", LEMMA: "have", TAG: "VBD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "shant": [
        {ORTH: "sha", LEMMA: "shall"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "There'd've": [
        {ORTH: "There"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "I'll": [
        {ORTH: "I", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "Why's": [
        {ORTH: "Why"},
        {ORTH: "'s"}
    ],

    "Shouldn't've": [
        {ORTH: "Should"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Wasnt": [
        {ORTH: "Was"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "whove": [
        {ORTH: "who"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "hasn't": [
        {ORTH: "has"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "wouldntve": [
        {ORTH: "would"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Wheres": [
        {ORTH: "Where"},
        {ORTH: "s"}
    ],

    "How'll": [
        {ORTH: "How"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "there'd've": [
        {ORTH: "there"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Whos": [
        {ORTH: "Who"},
        {ORTH: "s"}
    ],

    "shes": [
        {ORTH: "she", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "s"}
    ],

    "Doesn't": [
        {ORTH: "Does", LEMMA: "do", TAG: "VBZ"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Arent": [
        {ORTH: "Are", TAG: "VBP", "number": 2, LEMMA: "be"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Hasnt": [
        {ORTH: "Has", LEMMA: "have"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "He's": [
        {ORTH: "He", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'s"}
    ],

    "wasnt": [
        {ORTH: "was"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "whyll": [
        {ORTH: "why"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "mustnt": [
        {ORTH: "must"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "He'd": [
        {ORTH: "He", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "Shes": [
        {ORTH: "She", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "s"}
    ],

    "where've": [
        {ORTH: "where"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Youll": [
        {ORTH: "You", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "hasnt": [
        {ORTH: "has"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "theyll": [
        {ORTH: "they", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "it'd've": [
        {ORTH: "it", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "itdve": [
        {ORTH: "it", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "wedve": [
        {ORTH: "we"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Werent": [
        {ORTH: "Were"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Therell": [
        {ORTH: "There"},
        {ORTH: "ll", LEMMA: "will", TAG: "MD"}
    ],

    "shan't": [
        {ORTH: "sha", LEMMA: "shall"},
        {ORTH: "n't", LEMMA: "not", TAG: "RB"}
    ],

    "Wont": [
        {ORTH: "Wo", LEMMA: "will"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "hadntve": [
        {ORTH: "had", LEMMA: "have", TAG: "VBD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "who've": [
        {ORTH: "who"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Whatre": [
        {ORTH: "What"},
        {ORTH: "re", LEMMA: "be", NORM: "are"}
    ],

    "'s": [
        {ORTH: "'s", LEMMA: "'s"}
    ],

    "where'd": [
        {ORTH: "where"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "shouldve": [
        {ORTH: "should"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "where's": [
        {ORTH: "where"},
        {ORTH: "'s"}
    ],

    "neednt": [
        {ORTH: "need"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "It'll": [
        {ORTH: "It", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "We'd": [
        {ORTH: "We", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "Whats": [
        {ORTH: "What"},
        {ORTH: "s"}
    ],

    "\u2014": [
        {ORTH: "\u2014", TAG: ":", LEMMA: "--"}
    ],

    "Itd": [
        {ORTH: "It", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "she'd": [
        {ORTH: "she", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'d", LEMMA: "would", TAG: "MD"}
    ],

    "Mustnt": [
        {ORTH: "Must"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "Notve": [
        {ORTH: "Not", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "you'll": [
        {ORTH: "you", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
    ],

    "Theyd": [
        {ORTH: "They", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "d", LEMMA: "would", TAG: "MD"}
    ],

    "she's": [
        {ORTH: "she", LEMMA: PRON_LEMMA, TAG: "PRP"},
        {ORTH: "'s"}
    ],

    "Couldnt": [
        {ORTH: "Could", TAG: "MD"},
        {ORTH: "nt", LEMMA: "not", TAG: "RB"}
    ],

    "that's": [
        {ORTH: "that"},
        {ORTH: "'s"}
    ],

    "'em": [
        {ORTH: "'em", LEMMA: PRON_LEMMA, NORM: "them"}
    ],

    "ol'": [
        {ORTH: "ol'", LEMMA: "old"}
    ],

    "Ak.": [
        {ORTH: "Ak.", LEMMA: "Alaska"}
    ],

    "Ala.": [
        {ORTH: "Ala.", LEMMA: "Alabama"}
    ],

    "Apr.": [
        {ORTH: "Apr.", LEMMA: "April"}
    ],

    "Ariz.": [
        {ORTH: "Ariz.", LEMMA: "Arizona"}
    ],

    "Ark.": [
        {ORTH: "Ark.", LEMMA: "Arkansas"}
    ],

    "Aug.": [
        {ORTH: "Aug.", LEMMA: "August"}
    ],

    "Calif.": [
        {ORTH: "Calif.", LEMMA: "California"}
    ],

    "Colo.": [
        {ORTH: "Colo.", LEMMA: "Colorado"}
    ],

    "Conn.": [
        {ORTH: "Conn.", LEMMA: "Connecticut"}
    ],

    "Dec.": [
        {ORTH: "Dec.", LEMMA: "December"}
    ],

    "Del.": [
        {ORTH: "Del.", LEMMA: "Delaware"}
    ],

    "Feb.": [
        {ORTH: "Feb.", LEMMA: "February"}
    ],

    "Fla.": [
        {ORTH: "Fla.", LEMMA: "Florida"}
    ],

    "Ga.": [
        {ORTH: "Ga.", LEMMA: "Georgia"}
    ],

    "Ia.": [
        {ORTH: "Ia.", LEMMA: "Iowa"}
    ],

    "Id.": [
        {ORTH: "Id.", LEMMA: "Idaho"}
    ],

    "Ill.": [
        {ORTH: "Ill.", LEMMA: "Illinois"}
    ],

    "Ind.": [
        {ORTH: "Ind.", LEMMA: "Indiana"}
    ],

    "Jan.": [
        {ORTH: "Jan.", LEMMA: "January"}
    ],

    "Jul.": [
        {ORTH: "Jul.", LEMMA: "July"}
    ],

    "Jun.": [
        {ORTH: "Jun.", LEMMA: "June"}
    ],

    "Kan.": [
        {ORTH: "Kan.", LEMMA: "Kansas"}
    ],

    "Kans.": [
        {ORTH: "Kans.", LEMMA: "Kansas"}
    ],

    "Ky.": [
        {ORTH: "Ky.", LEMMA: "Kentucky"}
    ],

    "La.": [
        {ORTH: "La.", LEMMA: "Louisiana"}
    ],

    "Mar.": [
        {ORTH: "Mar.", LEMMA: "March"}
    ],

    "Mass.": [
        {ORTH: "Mass.", LEMMA: "Massachusetts"}
    ],

    "May.": [
        {ORTH: "May.", LEMMA: "May"}
    ],

    "Mich.": [
        {ORTH: "Mich.", LEMMA: "Michigan"}
    ],

    "Minn.": [
        {ORTH: "Minn.", LEMMA: "Minnesota"}
    ],

    "Miss.": [
        {ORTH: "Miss.", LEMMA: "Mississippi"}
    ],

    "N.C.": [
        {ORTH: "N.C.", LEMMA: "North Carolina"}
    ],

    "N.D.": [
        {ORTH: "N.D.", LEMMA: "North Dakota"}
    ],

    "N.H.": [
        {ORTH: "N.H.", LEMMA: "New Hampshire"}
    ],

    "N.J.": [
        {ORTH: "N.J.", LEMMA: "New Jersey"}
    ],

    "N.M.": [
        {ORTH: "N.M.", LEMMA: "New Mexico"}
    ],

    "N.Y.": [
        {ORTH: "N.Y.", LEMMA: "New York"}
    ],

    "Neb.": [
        {ORTH: "Neb.", LEMMA: "Nebraska"}
    ],

    "Nebr.": [
        {ORTH: "Nebr.", LEMMA: "Nebraska"}
    ],

    "Nev.": [
        {ORTH: "Nev.", LEMMA: "Nevada"}
    ],

    "Nov.": [
        {ORTH: "Nov.", LEMMA: "November"}
    ],

    "Oct.": [
        {ORTH: "Oct.", LEMMA: "October"}
    ],

    "Okla.": [
        {ORTH: "Okla.", LEMMA: "Oklahoma"}
    ],

    "Ore.": [
        {ORTH: "Ore.", LEMMA: "Oregon"}
    ],

    "Pa.": [
        {ORTH: "Pa.", LEMMA: "Pennsylvania"}
    ],

    "S.C.": [
        {ORTH: "S.C.", LEMMA: "South Carolina"}
    ],

    "Sep.": [
        {ORTH: "Sep.", LEMMA: "September"}
    ],

    "Sept.": [
        {ORTH: "Sept.", LEMMA: "September"}
    ],

    "Tenn.": [
        {ORTH: "Tenn.", LEMMA: "Tennessee"}
    ],

    "Va.": [
        {ORTH: "Va.", LEMMA: "Virginia"}
    ],

    "Wash.": [
        {ORTH: "Wash.", LEMMA: "Washington"}
    ],

    "Wis.": [
        {ORTH: "Wis.", LEMMA: "Wisconsin"}
    ]
}


ORTH_ONLY = [
    "''",
    "\")",
    "a.",
    "a.m.",
    "Adm.",
    "b.",
    "Bros.",
    "c.",
    "co.",
    "Co.",
    "Corp.",
    "d.",
    "D.C.",
    "Dr.",
    "e.",
    "e.g.",
    "E.g.",
    "E.G.",
    "f.",
    "g.",
    "Gen.",
    "Gov.",
    "h.",
    "i.",
    "i.e.",
    "I.e.",
    "I.E.",
    "Inc.",
    "j.",
    "Jr.",
    "k.",
    "l.",
    "Ltd.",
    "m.",
    "Md.",
    "Messrs.",
    "Mo.",
    "Mont.",
    "Mr.",
    "Mrs.",
    "Ms.",
    "n.",
    "o.",
    "p.",
    "p.m.",
    "Ph.D.",
    "q.",
    "r.",
    "Rep.",
    "Rev.",
    "s.",
    "Sen.",
    "St.",
    "t.",
    "u.",
    "v.",
    "vs.",
    "w.",
    "x.",
    "y.",
    "z."
]
