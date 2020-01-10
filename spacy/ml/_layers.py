from thinc.model import Model
from thinc.api import normal_init


def PrecomputableAffine(nO, nI, nF, nP):
    model = Model(
        "precomputable_affine",
        forward,
        init=init,
        dims={"nO": nO, "nI": nI, "nF": nF, "nP": nP},
        params={"W": None, "b": None, "pad": None},
    )
    model.initialize()
    return model


def forward(model, X, is_train):
    nF = model.get_dim("nF")
    nO = model.get_dim("nO")
    nP = model.get_dim("nP")
    nI = model.get_dim("nI")
    W = model.get_param("W")
    Yf = model.ops.gemm(
        X, W.reshape((nF * nO * nP, nI)), trans2=True
    )
    Yf = Yf.reshape((Yf.shape[0], nF, nO, nP))
    Yf = model.ops.xp.vstack((model.get_param("pad"), Yf))

    def backward(dY_ids):
        dY, ids = dY_ids
        # Backprop padding
        mask = ids < 0.0
        mask = mask.sum(axis=1)
        d_pad = dY * mask.reshape((ids.shape[0], 1, 1))

        # TODO: doesn't work - wrong dimensions
        model.set_grad("pad", d_pad)
        model.inc_grad("pad", d_pad.sum(axis=0))

        Xf = X[ids]
        Xf = Xf.reshape((Xf.shape[0], nF * nI))

        model.inc_grad("b", dY.sum(axis=0))
        dY = dY.reshape((dY.shape[0], nO * nP))

        Wopfi = W.transpose((1, 2, 0, 3))
        Wopfi = model.ops.xp.ascontiguousarray(Wopfi)
        Wopfi = Wopfi.reshape((nO * nP, nF * nI))
        dXf = model.ops.gemm(dY.reshape((dY.shape[0], nO * nP)), Wopfi)

        # Reuse the buffer
        dWopfi = Wopfi
        dWopfi.fill(0.0)
        model.ops.gemm(dY, Xf, out=dWopfi, trans1=True)
        dWopfi = dWopfi.reshape((nO, nP, nF, nI))
        # (o, p, f, i) --> (f, o, p, i)
        model.inc_grad("W", dWopfi.transpose((2, 0, 1, 3)))
        return dXf.reshape((dXf.shape[0], nF, nI))

    return Yf, backward


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
    W = model.ops.alloc_f4d(nF, nO, nP, nI)
    b = model.ops.alloc_f2d(nO, nP)
    pad = model.ops.alloc_f4d(1, nF, nO, nP)

    ops = model.ops
    xp = ops.xp
    normal_init(W, fan_in=nF*nI, inplace=True)
    model.set_param("W", W)
    model.set_param("b", b)
    model.set_param("pad", pad)

    ids = ops.alloc((5000, nF), dtype="f")
    ids += xp.random.uniform(0, 1000, ids.shape)
    ids = ops.asarray(ids, dtype="i")
    tokvecs = ops.alloc((5000, nI), dtype="f")
    tokvecs += xp.random.normal(loc=0.0, scale=1.0, size=tokvecs.size).reshape(
        tokvecs.shape
    )

    def predict(ids, tokvecs):
        # nS ids. nW tokvecs. Exclude the padding array.
        hiddens, bp = model(tokvecs[:-1])  # (nW, f, o, p)
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
