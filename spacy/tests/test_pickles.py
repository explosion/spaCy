from __future__ import unicode_literals

import io
import pickle

from ..strings import StringStore


def test_pickle_string_store():
    sstore = StringStore()
    hello = sstore['hello']
    bye = sstore['bye']
    bdata = pickle.dumps(sstore, protocol=-1)
    unpickled = pickle.loads(bdata)
    assert unpickled['hello'] == hello
    assert unpickled['bye'] == bye

