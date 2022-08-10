from thinc.api import Model, normal_init

from ..util import registry


@registry.layers("spacy.PrecomputableAffine.v1")
def PrecomputableAffine(nO, nI, nF, nP, dropout=0.1):
    model = Model(
        "precomputable_affine",
        forward,
        init=init,
        dims={"nO": nO, "nI": nI, "nF": nF, "nP": nP},
        params={"W": None, "b": None, "pad": None},
        attrs={"dropout_rate": dropout},
    )
    return model


def forward(model, X, is_train):
    nF = model.get_dim("nF")
    nO = model.get_dim("nO")
    nP = model.get_dim("nP")
    nI = model.get_dim("nI")
    W = model.get_param("W")
    # Preallocate array for layer output, including padding.
    Yf = model.ops.alloc2f(X.shape[0] + 1, nF * nO * nP, zeros=False)
    model.ops.gemm(X, W.reshape((nF * nO * nP, nI)), trans2=True, out=Yf[1:])
    Yf = Yf.reshape((Yf.shape[0], nF, nO, nP))

    # Set padding. Padding has shape (1, nF, nO, nP). Unfortunately, we cannot
    # change its shape to (nF, nO, nP) without breaking existing models. So
    # we'll squeeze the first dimension here.
    Yf[0] = model.ops.xp.squeeze(model.get_param("pad"), 0)

    def backward(dY_ids):
        # This backprop is particularly tricky, because we get back a different
        # thing from what we put out. We put out an array of shape:
        # (nB, nF, nO, nP), and get back:
        # (nB, nO, nP) and ids (nB, nF)
        # The ids tell us the values of nF, so we would have:
        #
        # dYf = zeros((nB, nF, nO, nP))
        # for b in range(nB):
        #     for f in range(nF):
        #         dYf[b, ids[b, f]] += dY[b]
        #
        # However, we avoid building that array for efficiency -- and just pass
        # in the indices.
        dY, ids = dY_ids
        assert dY.ndim == 3
        assert dY.shape[1] == nO, dY.shape
        assert dY.shape[2] == nP, dY.shape
        # nB = dY.shape[0]
        model.inc_grad("pad", _backprop_precomputable_affine_padding(model, dY, ids))
        Xf = X[ids]
        Xf = Xf.reshape((Xf.shape[0], nF * nI))

        model.inc_grad("b", dY.sum(axis=0))
        dY = dY.reshape((dY.shape[0], nO * nP))

        Wopfi = W.transpose((1, 2, 0, 3))
        Wopfi = Wopfi.reshape((nO * nP, nF * nI))
        dXf = model.ops.gemm(dY.reshape((dY.shape[0], nO * nP)), Wopfi)

        dWopfi = model.ops.gemm(dY, Xf, trans1=True)
        dWopfi = dWopfi.reshape((nO, nP, nF, nI))
        # (o, p, f, i) --> (f, o, p, i)
        dWopfi = dWopfi.transpose((2, 0, 1, 3))
        model.inc_grad("W", dWopfi)
        return dXf.reshape((dXf.shape[0], nF, nI))

    return Yf, backward


def _backprop_precomputable_affine_padding(model, dY, ids):
    nB = dY.shape[0]
    nF = model.get_dim("nF")
    nP = model.get_dim("nP")
    nO = model.get_dim("nO")
    # Backprop the "padding", used as a filler for missing values.
    # Values that are missing are set to -1, and each state vector could
    # have multiple missing values. The padding has different values for
    # different missing features. The gradient of the padding vector is:
    #
    # for b in range(nB):
    #     for f in range(nF):
    #         if ids[b, f] < 0:
    #             d_pad[f] += dY[b]
    #
    # Which can be rewritten as:
    #
    # (ids < 0).T @ dY
    mask = model.ops.asarray(ids < 0, dtype="f")
    d_pad = model.ops.gemm(mask, dY.reshape(nB, nO * nP), trans1=True)
    return d_pad.reshape((1, nF, nO, nP))


def init(model, X=None, Y=None):
    """This is like the 'layer sequential unit variance', but instead
    of taking the actual inputs, we randomly generate whitened data.

    Why's this all so complicated? We have a huge number of inputs,
    and the maxout unit makes guessing the dynamics tricky. Instead
    we set the maxout weights to values that empirically result in
    whitened outputs given whitened inputs.
    """
    if model.has_param("W") and model.get_param("W").any():
        return

    nF = model.get_dim("nF")
    nO = model.get_dim("nO")
    nP = model.get_dim("nP")
    nI = model.get_dim("nI")
    W = model.ops.alloc4f(nF, nO, nP, nI)
    b = model.ops.alloc2f(nO, nP)
    pad = model.ops.alloc4f(1, nF, nO, nP)

    ops = model.ops
    W = normal_init(ops, W.shape, mean=float(ops.xp.sqrt(1.0 / nF * nI)))
    pad = normal_init(ops, pad.shape, mean=1.0)
    model.set_param("W", W)
    model.set_param("b", b)
    model.set_param("pad", pad)

    ids = ops.alloc((5000, nF), dtype="f")
    ids += ops.xp.random.uniform(0, 1000, ids.shape)
    ids = ops.asarray(ids, dtype="i")
    tokvecs = ops.alloc((5000, nI), dtype="f")
    tokvecs += ops.xp.random.normal(loc=0.0, scale=1.0, size=tokvecs.size).reshape(
        tokvecs.shape
    )

    def predict(ids, tokvecs):
        # nS ids. nW tokvecs. Exclude the padding array.
        hiddens = model.predict(tokvecs[:-1])  # (nW, f, o, p)
        vectors = model.ops.alloc((ids.shape[0], nO * nP), dtype="f")
        # need nS vectors
        hiddens = hiddens.reshape((hiddens.shape[0] * nF, nO * nP))
        model.ops.scatter_add(vectors, ids.flatten(), hiddens)
        vectors = vectors.reshape((vectors.shape[0], nO, nP))
        vectors += b
        vectors = model.ops.asarray(vectors)
        if nP >= 2:
            return model.ops.maxout(vectors)[0]
        else:
            return vectors * (vectors >= 0)

    tol_var = 0.01
    tol_mean = 0.01
    t_max = 10
    W = model.get_param("W").copy()
    b = model.get_param("b").copy()
    for t_i in range(t_max):
        acts1 = predict(ids, tokvecs)
        var = model.ops.xp.var(acts1)
        mean = model.ops.xp.mean(acts1)
        if abs(var - 1.0) >= tol_var:
            W /= model.ops.xp.sqrt(var)
            model.set_param("W", W)
        elif abs(mean) >= tol_mean:
            b -= mean
            model.set_param("b", b)
        else:
            break
