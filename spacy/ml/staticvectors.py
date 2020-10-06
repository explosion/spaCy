from typing import List, Tuple, Callable, Optional, cast
from thinc.initializers import glorot_uniform_init
from thinc.util import partial
from thinc.types import Ragged, Floats2d, Floats1d
from thinc.api import Model, Ops, registry

from ..tokens import Doc
from ..errors import Errors


@registry.layers("spacy.StaticVectors.v1")
def StaticVectors(
    nO: Optional[int] = None,
    nM: Optional[int] = None,
    *,
    dropout: Optional[float] = None,
    init_W: Callable = glorot_uniform_init,
    key_attr: str = "ORTH"
) -> Model[List[Doc], Ragged]:
    """Embed Doc objects with their vocab's vectors table, applying a learned
    linear projection to control the dimensionality. If a dropout rate is
    specified, the dropout is applied per dimension over the whole batch.
    """
    return Model(
        "static_vectors",
        forward,
        init=partial(init, init_W),
        params={"W": None},
        attrs={"key_attr": key_attr, "dropout_rate": dropout},
        dims={"nO": nO, "nM": nM},
    )


def forward(
    model: Model[List[Doc], Ragged], docs: List[Doc], is_train: bool
) -> Tuple[Ragged, Callable]:
    if not sum(len(doc) for doc in docs):
        return _handle_empty(model.ops, model.get_dim("nO"))
    key_attr = model.attrs["key_attr"]
    W = cast(Floats2d, model.ops.as_contig(model.get_param("W")))
    V = cast(Floats2d, docs[0].vocab.vectors.data)
    mask = _get_drop_mask(model.ops, W.shape[0], model.attrs.get("dropout_rate"))
    rows = model.ops.flatten(
        [doc.vocab.vectors.find(keys=doc.to_array(key_attr)) for doc in docs]
    )
    output = Ragged(
        model.ops.gemm(model.ops.as_contig(V[rows]), W, trans2=True),
        model.ops.asarray([len(doc) for doc in docs], dtype="i"),
    )
    if mask is not None:
        output.data *= mask

    def backprop(d_output: Ragged) -> List[Doc]:
        if mask is not None:
            d_output.data *= mask
        model.inc_grad(
            "W",
            model.ops.gemm(d_output.data, model.ops.as_contig(V[rows]), trans1=True),
        )
        return []

    return output, backprop


def init(
    init_W: Callable,
    model: Model[List[Doc], Ragged],
    X: Optional[List[Doc]] = None,
    Y: Optional[Ragged] = None,
) -> Model[List[Doc], Ragged]:
    nM = model.get_dim("nM") if model.has_dim("nM") else None
    nO = model.get_dim("nO") if model.has_dim("nO") else None
    if X is not None and len(X):
        nM = X[0].vocab.vectors.data.shape[1]
    if Y is not None:
        nO = Y.data.shape[1]

    if nM is None:
        raise ValueError(Errors.E905)
    if nO is None:
        raise ValueError(Errors.E904)
    model.set_dim("nM", nM)
    model.set_dim("nO", nO)
    model.set_param("W", init_W(model.ops, (nO, nM)))
    return model


def _handle_empty(ops: Ops, nO: int):
    return Ragged(ops.alloc2f(0, nO), ops.alloc1i(0)), lambda d_ragged: []


def _get_drop_mask(ops: Ops, nO: int, rate: Optional[float]) -> Optional[Floats1d]:
    return ops.get_dropout_mask((nO,), rate) if rate is not None else None
