# coding: utf8
from __future__ import unicode_literals

# import symbols – if you need to use more, add them here
from ...symbols import ORTH, LEMMA, TAG, NORM, ADP, DET


# Add tokenizer exceptions
# Documentation: https://spacy.io/docs/usage/adding-languages#tokenizer-exceptions
# Feel free to use custom logic to generate repetitive exceptions more efficiently.
# If an exception is split into more than one token, the ORTH values combined always
# need to match the original string.

# Exceptions should be added in the following format:

_exc = {
    "tayo'y": [
        {ORTH: "tayo", LEMMA: "tayo"},
        {ORTH: "'y", LEMMA: "ay"}],
    "isa'y": [
        {ORTH: "isa", LEMMA: "isa"},
        {ORTH: "'y", LEMMA: "ay"}],
    "baya'y": [
        {ORTH: "baya", LEMMA: "bayan"},
        {ORTH: "'y", LEMMA: "ay"}],
    "sa'yo": [
        {ORTH: "sa", LEMMA: "sa"},
        {ORTH: "'yo", LEMMA: "iyo"}],
    "ano'ng": [
        {ORTH: "ano", LEMMA: "ano"},
        {ORTH: "'ng", LEMMA: "ang"}],
    "siya'y": [
        {ORTH: "siya", LEMMA: "siya"},
        {ORTH: "'y", LEMMA: "ay"}],
    "nawa'y": [
        {ORTH: "nawa", LEMMA: "nawa"},
        {ORTH: "'y", LEMMA: "ay"}],
    "papa'no": [
        {ORTH: "papa'no", LEMMA: "papaano"}],
    "'di": [
        {ORTH: "'di", LEMMA: "hindi"}]
}


# To keep things clean and readable, it's recommended to only declare the
# TOKENIZER_EXCEPTIONS at the bottom:

TOKENIZER_EXCEPTIONS = _exc
