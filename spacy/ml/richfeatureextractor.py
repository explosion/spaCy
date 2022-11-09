from typing import List, Optional, Callable, Tuple
from thinc.types import Ints2d
from thinc.api import Model, registry, get_current_ops
from ..tokens import Doc
from ..util import get_search_char_byte_arrays


@registry.layers("spacy.RichFeatureExtractor.v1")
def RichFeatureExtractor(
    *,
    case_sensitive: bool,
    pref_lengths: Optional[List[int]] = None,
    suff_lengths: Optional[List[int]] = None,
    pref_search_chars: Optional[str] = None,
    pref_search_lengths: Optional[List[int]] = None,
    suff_search_chars: Optional[str] = None,
    suff_search_lengths: Optional[List[int]] = None,
) -> Model[List[Doc], List[Ints2d]]:
    ops = get_current_ops()
    if pref_search_chars is not None:
        ps_search_chars, ps_width_offsets = get_search_char_byte_arrays(
            pref_search_chars, case_sensitive
        )
    else:
        ps_search_chars = bytes()
        ps_width_offsets = bytes()
    if suff_search_chars is not None:

        ss_search_chars, ss_width_offsets = get_search_char_byte_arrays(
            suff_search_chars, case_sensitive
        )
    else:
        ss_search_chars = bytes()
        ss_width_offsets = bytes()
    return Model(
        "extract_character_combination_hashes",
        forward,
        attrs={
            "case_sensitive": case_sensitive,
            "p_lengths": bytes(pref_lengths) if pref_lengths is not None else bytes(),
            "s_lengths": bytes(suff_lengths) if suff_lengths is not None else bytes(),
            "ps_search_chars": ps_search_chars,
            "ps_width_offsets": ps_width_offsets,
            "ps_lengths": bytes(pref_search_lengths)
            if pref_search_lengths is not None
            else bytes(),
            "ss_search_chars": ss_search_chars,
            "ss_width_offsets": ss_width_offsets,
            "ss_lengths": bytes(suff_search_lengths)
            if suff_search_lengths is not None
            else bytes(),
        },
    )


def forward(
    model: Model[List[Doc], List[Ints2d]], docs, is_train: bool
) -> Tuple[List[Ints2d], Callable]:
    ops = model.ops
    case_sensitive: bool = model.attrs["case_sensitive"]
    p_lengths: bytes = model.attrs["p_lengths"]
    s_lengths: bytes = model.attrs["s_lengths"]
    ps_search_chars: bytes = model.attrs["ps_search_chars"]
    ps_width_offsets: bytes = model.attrs["ps_width_offsets"]
    ps_lengths: bytes = model.attrs["ps_lengths"]
    ss_search_chars: bytes = model.attrs["ss_search_chars"]
    ss_width_offsets: bytes = model.attrs["ss_width_offsets"]
    ss_lengths: bytes = model.attrs["ss_lengths"]
    features: List[Ints2d] = []
    for doc in docs:
        hashes = doc.get_character_combination_hashes(
            cs=case_sensitive,
            p_lengths=p_lengths,
            s_lengths=s_lengths,
            ps_search_chars=ps_search_chars,
            ps_width_offsets=ps_width_offsets,
            ps_lengths=ps_lengths,
            ss_search_chars=ss_search_chars,
            ss_width_offsets=ss_width_offsets,
            ss_lengths=ss_lengths,
        )
        features.append(ops.asarray2i(hashes, dtype="uint64"))

    backprop: Callable[[List[Ints2d]], List] = lambda d_features: []
    return features, backprop
