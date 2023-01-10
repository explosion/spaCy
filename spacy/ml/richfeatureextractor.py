from typing import List, Optional, Callable, Tuple
from thinc.types import Ints2d
from thinc.api import Model, registry, get_current_ops
from ..tokens import Doc


@registry.layers("spacy.RichFeatureExtractor.v1")
def RichFeatureExtractor(
    *,
    case_sensitive: bool,
    pref_lengths: Optional[List[int]] = None,
    suff_lengths: Optional[List[int]] = None,
) -> Model[List[Doc], List[Ints2d]]:
    return Model(
        "extract_character_combination_hashes",
        forward,
        attrs={
            "case_sensitive": case_sensitive,
            "p_lengths": bytes(pref_lengths) if pref_lengths is not None else bytes(),
            "s_lengths": bytes(suff_lengths) if suff_lengths is not None else bytes(),
        },
    )


def forward(
    model: Model[List[Doc], List[Ints2d]], docs, is_train: bool
) -> Tuple[List[Ints2d], Callable]:
    ops = model.ops
    case_sensitive: bool = model.attrs["case_sensitive"]
    p_lengths: bytes = model.attrs["p_lengths"]
    s_lengths: bytes = model.attrs["s_lengths"]
    features: List[Ints2d] = []
    for doc in docs:
        hashes = doc.get_character_combination_hashes(
            case_sensitive=case_sensitive,
            p_lengths=p_lengths,
            s_lengths=s_lengths,
        )
        features.append(ops.asarray2i(hashes, dtype="uint64"))

    backprop: Callable[[List[Ints2d]], List] = lambda d_features: []
    return features, backprop
