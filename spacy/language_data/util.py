# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *

try:
    unicode
except:
    unicode = str


PRON_LEMMA = "-PRON-"
DET_LEMMA = "-DET-"
ENT_ID = "ent_id"


def update_exc(exc, additions):
    for orth, token_attrs in additions.items():
        if not all(isinstance(attr[ORTH], unicode) for attr in token_attrs):
            msg = "Invalid value for ORTH in exception: key='%s', orths='%s'"
            raise ValueError(msg % (orth, token_attrs))
        described_orth = ''.join(attr[ORTH] for attr in token_attrs)
        if orth != described_orth:
            # TODO: Better error
            msg = "Invalid tokenizer exception: key='%s', orths='%s'"
            raise ValueError(msg % (orth, described_orth))
    overlap = set(exc.keys()).intersection(set(additions))
    assert not overlap, overlap
    exc.update(additions)


def strings_to_exc(orths):
    return {orth: [{ORTH: orth}] for orth in orths}


def expand_exc(excs, search, replace):
    updates = {}

    for token_string, tokens in excs.items():
        if search in token_string:
            new_key = token_string.replace(search, replace)
            new_value = [_fix_token(t, search, replace) for t in tokens]

            updates[new_key] = new_value

    return updates


def _fix_token(token, search, replace):
    fixed = dict(token)
    fixed[ORTH] = fixed[ORTH].replace(search, replace)
    return fixed
