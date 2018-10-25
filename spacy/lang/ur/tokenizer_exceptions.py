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

}

# To keep things clean and readable, it's recommended to only declare the
# TOKENIZER_EXCEPTIONS at the bottom:

TOKENIZER_EXCEPTIONS = _exc
