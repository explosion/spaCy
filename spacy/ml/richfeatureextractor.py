from typing import List, Optional, Callable, Tuple
from ..util import get_arrays_for_search_chars
from thinc.types import Ints1d, Ints2d
from thinc.api import Model, registry, get_current_ops

from ..tokens import Doc


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
        pref_search, pref_lookup = get_arrays_for_search_chars(
            pref_search_chars, case_sensitive
        )
    else:
        pref_search, pref_lookup = bytes(), bytes()
    if suff_search_chars is not None:
        suff_search, suff_lookup = get_arrays_for_search_chars(
            suff_search_chars, case_sensitive
        )
    else:
        suff_search, suff_lookup = bytes(), bytes()
    return Model(
        "extract_character_combination_hashes",
        forward,
        attrs={
            "case_sensitive": case_sensitive,
            "pref_lengths": ops.asarray1i(pref_lengths)
            if pref_lengths is not None
            else ops.asarray1i([]),
            "suff_lengths": ops.asarray1i(suff_lengths)
            if suff_lengths is not None
            else ops.asarray1i([]),
            "pref_search": pref_search,
            "pref_lookup": pref_lookup,
            "pref_search_char_len": len(pref_search) / 4
            if pref_search_chars is not None
            else 0,
            "pref_search_lengths": ops.asarray1i(pref_search_lengths)
            if pref_search_lengths is not None
            else ops.asarray1i([]),
            "suff_search": suff_search,
            "suff_lookup": suff_lookup,
            "suff_search_char_len": len(suff_search) / 4
            if suff_search_chars is not None
            else 0,
            "suff_search_lengths": ops.asarray1i(suff_search_lengths)
            if suff_search_lengths is not None
            else ops.asarray1i([]),
        },
    )


def forward(
    model: Model[List[Doc], List[Ints2d]], docs, is_train: bool
) -> Tuple[List[Ints2d], Callable]:
    ops = model.ops
    case_sensitive: bool = model.attrs["case_sensitive"]
    pref_lengths: Ints1d = model.attrs["pref_lengths"]
    suff_lengths: Ints1d = model.attrs["suff_lengths"]
    pref_search: bytes = model.attrs["pref_search"]
    pref_lookup: bytes = model.attrs["pref_lookup"]
    pref_search_char_len: int = model.attrs["pref_search_char_len"]
    pref_search_lengths: Ints1d = model.attrs["pref_search_lengths"]
    suff_search: bytes = model.attrs["suff_search"]
    suff_lookup: bytes = model.attrs["suff_lookup"]
    suff_search_char_len: int = model.attrs["suff_search_char_len"]
    suff_search_lengths: Ints1d = model.attrs["suff_search_lengths"]
    features: List[Ints2d] = []
    for doc in docs:
        hashes = doc.get_character_combination_hashes(
            cs=case_sensitive,
            p_lengths=pref_lengths,
            s_lengths=suff_lengths,
            ps_search=pref_search,
            ps_lookup=pref_lookup,
            ps_l=pref_search_char_len,
            ps_lengths=pref_search_lengths,
            ss_search=suff_search,
            ss_lookup=suff_lookup,
            ss_l=suff_search_char_len,
            ss_lengths=suff_search_lengths,
        )
        features.append(ops.asarray2i(hashes))

    backprop: Callable[[List[Ints2d]], List] = lambda d_features: []
    return features, backprop
