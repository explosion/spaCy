# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *


PRON_LEMMA = "-PRON-"
DET_LEMMA = "-DET-"
ENT_ID = "ent_id"


def update_exc(exc, additions):
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
