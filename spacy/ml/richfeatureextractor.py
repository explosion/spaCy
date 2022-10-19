from typing import List, Optional, Callable, Tuple
from ..util import get_byte_arrays_for_search_chars
from thinc.types import Ints2d
from thinc.api import Model, registry

from ..tokens import Doc


@registry.layers("spacy.RichFeatureExtractor.v1")
def RichFeatureExtractor(
    *,
    case_sensitive: bool,
    pref_lengths: Optional[List[int]] = None,
    pref_search_chars: Optional[str] = None,
    pref_search_lengths: Optional[List[int]] = None,
    suff_lengths: Optional[List[int]] = None,
    suff_search_chars: Optional[str] = None,
    suff_search_lengths: Optional[List[int]] = None,
) -> Model[List[Doc], List[Ints2d]]:
    if pref_search_chars is not None:
        pref_search, pref_ref = get_byte_arrays_for_search_chars(pref_search_chars, case_sensitive)
    else:
        pref_search, pref_ref = bytes(), bytes()
    if suff_search_chars is not None:
        suff_search, suff_ref = get_byte_arrays_for_search_chars(suff_search_chars, case_sensitive)
    else:
        suff_search, suff_ref = bytes(), bytes()
    return Model(
        "extract_character_combination_hashes",
        forward,
        attrs={
            "case_sensitive": case_sensitive,
            "pref_lengths": pref_lengths if pref_lengths is not None else [],
            "suff_lengths": suff_lengths if suff_lengths is not None else [],
            "pref_search": pref_search,
            "pref_ref": pref_ref,
            "pref_s_char_l": len(pref_search) / 4 if pref_search_chars is not None else 0,
            "pref_search_lengths": pref_search_lengths
            if pref_search_lengths is not None
            else [],
            "suff_search": suff_search,
            "suff_ref": suff_ref,
            "suff_s_char_l": len(suff_search) / 4 if suff_search_chars is not None else 0,
            "suff_search_lengths": suff_search_lengths
            if suff_search_lengths is not None
            else [],
        },
    )


def forward(
    model: Model[List[Doc], List[Ints2d]], docs, is_train: bool
) -> Tuple[List[Ints2d], Callable]:
    ops = model.ops
    case_sensitive: bool = model.attrs["case_sensitive"]
    pref_lengths: List[int] = model.attrs["pref_lengths"]
    suff_lengths: List[int] = model.attrs["suff_lengths"]
    pref_search: bytes = model.attrs["pref_search"]
    pref_ref: bytes = model.attrs["pref_ref"]
    pref_s_char_l: int = model.attr["pref_s_char_l"]
    pref_search_lengths: List[int] = model.attrs["pref_search_lengths"]
    suff_search: bytes = model.attrs["suff_search"]
    suff_ref: bytes = model.attrs["suff_ref"]
    suff_s_char_l: int = model.attr["suff_s_char_l"]
    suff_search_lengths: List[int] = model.attrs["suff_search_lengths"]
    features: List[Ints2d] = []
    for doc in docs:
        hashes = doc.get_character_combination_hashes(
            case_sensitive=case_sensitive,
            pref_lengths=pref_lengths,
            suff_lengths=suff_lengths,
            pref_search=pref_search,
            pref_ref=pref_ref,
            pref_s_char_l=pref_s_char_l,
            pref_search_lengths=pref_search_lengths,
            suff_search=suff_search,
            suff_ref=suff_ref,
            suff_s_char_l=suff_s_char_l,
            suff_search_lengths=suff_search_lengths,
        )
        features.append(ops.asarray2i(hashes))

    backprop: Callable[[List[Ints2d]], List] = lambda d_features: []
    return features, backprop
