import numpy
from thinc.api import Model

from ..attrs import LOWER


def extract_ngrams(ngram_size: int, attr: int = LOWER) -> Model:
    model = Model("extract_ngrams", forward)
    model.attrs["ngram_size"] = ngram_size
    model.attrs["attr"] = attr
    return model


def forward(model: Model, docs, is_train: bool):
    batch_keys = []
    batch_vals = []
    for doc in docs:
        unigrams = model.ops.asarray(doc.to_array([model.attrs["attr"]]))
        ngrams = [unigrams]
        for n in range(2, model.attrs["ngram_size"] + 1):
            ngrams.append(model.ops.ngrams(n, unigrams))
        keys = model.ops.xp.concatenate(ngrams)
        keys, vals = model.ops.xp.unique(keys, return_counts=True)
        batch_keys.append(keys)
        batch_vals.append(vals)
    # The dtype here matches what thinc is expecting -- which differs per
    # platform (by int definition). This should be fixed once the problem
    # is fixed on Thinc's side.
    lengths = model.ops.asarray([arr.shape[0] for arr in batch_keys], dtype=numpy.int_)
    batch_keys = model.ops.xp.concatenate(batch_keys)
    batch_vals = model.ops.asarray(model.ops.xp.concatenate(batch_vals), dtype="f")

    def backprop(dY):
        return []

    return (batch_keys, batch_vals, lengths), backprop
