from __future__ import unicode_literals
from thinc.api import layerize, wrap, noop, chain, concatenate
from thinc.v2v import Model


def concatenate_lists(*layers, **kwargs):  # pragma: no cover
    """Compose two or more models `f`, `g`, etc, such that their outputs are
    concatenated, i.e. `concatenate(f, g)(x)` computes `hstack(f(x), g(x))`
    """
    if not layers:
        return layerize(noop())
    drop_factor = kwargs.get("drop_factor", 1.0)
    ops = layers[0].ops
    layers = [chain(layer, flatten) for layer in layers]
    concat = concatenate(*layers)

    def concatenate_lists_fwd(Xs, drop=0.0):
        if drop is not None:
            drop *= drop_factor
        lengths = ops.asarray([len(X) for X in Xs], dtype="i")
        flat_y, bp_flat_y = concat.begin_update(Xs, drop=drop)
        ys = ops.unflatten(flat_y, lengths)

        def concatenate_lists_bwd(d_ys, sgd=None):
            return bp_flat_y(ops.flatten(d_ys), sgd=sgd)

        return ys, concatenate_lists_bwd

    model = wrap(concatenate_lists_fwd, concat)
    return model


@layerize
def flatten(seqs, drop=0.0):
    ops = Model.ops
    lengths = ops.asarray([len(seq) for seq in seqs], dtype="i")

    def finish_update(d_X, sgd=None):
        return ops.unflatten(d_X, lengths, pad=0)

    X = ops.flatten(seqs, pad=0)
    return X, finish_update
