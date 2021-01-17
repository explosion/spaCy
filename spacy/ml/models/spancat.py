from typing import List
from thinc.api import Model, with_getitem, chain
from thinc.types import Ragged, Floats2d


def spancat_model(
    tok2vec: Model[List[Doc], List[Floats2d]],
    scorer: Model[Ragged, Floats2d]
) -> Model[Tuple[List[Doc], Ragged], Ragged]:
    model = chain(
        with_getitem(0, tok2vec),
        SubSpanner(),
        list2ragged(),
        scorer
    )
    model.add_ref("tok2vec", tok2vec)
    model.add_ref("scorer", scorer)
    return model


def SubSpanner() -> Model[Tuple[List[Floats2d], Ragged], List[Floats2d]]:
    return Model(
        "subspanner",
        forward,
        layers=[],
        refs={},
        attrs={},
        dims={"nO": None},
        initialize=init
    )


def init(model, X=None, Y=None):
    if X is None and Y is None:
        return
    elif Y is not None:
        model.set_dim("nO", Y.dataXd.shape[1])
    elif X is not None and len(X[0]):
        model.set_dim("nO", X[0][0].shape[1])


def forward(
    model: Model,
    source_spans: Tuple[List[Floats2d], Ragged],
    is_train: bool
) -> List[Floats2d]:
    """Get subsequences from source vectors."""
    Xs, spans = source_spans
    Ys = []
    for i, x in enumerate(Xs):
        for start, end in spans[i].dataXd:
            Ys.append(x[start:end])
    x_shapes = [x.shape for x in Xs]

    def backprop_windows(dYs: List[Floats2d]) -> Tuple[Floats2d, Ints2d]:
        dXs = []
        for dY, x_shape in enumerate(zip(dYs, x_shapes)):
            dX = model.ops.alloc2f(*x_shape)
            for i, (start, end) in enumerate(spans):
                dX[start:end] += dY[i]
            dXs.append(dX)
        return (dXs, spans)

    return Ys, backprop_windows
