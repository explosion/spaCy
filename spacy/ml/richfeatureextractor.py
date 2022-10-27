from typing import List, Optional, Callable, Tuple
from spacy.util import get_search_char_byte_arrays

# from ..util import get_arrays_for_search_chars
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
        (
            ps_1byte_ch,
            ps_2byte_ch,
            ps_3byte_ch,
            ps_4byte_ch,
        ) = get_search_char_byte_arrays(pref_search_chars, case_sensitive)
    else:
        ps_1byte_ch = ps_2byte_ch = ps_3byte_ch = ps_4byte_ch = bytes()
    if suff_search_chars is not None:
        (
            ss_1byte_ch,
            ss_2byte_ch,
            ss_3byte_ch,
            ss_4byte_ch,
        ) = get_search_char_byte_arrays(suff_search_chars, case_sensitive)
    else:
        ss_1byte_ch = ss_2byte_ch = ss_3byte_ch = ss_4byte_ch = bytes()
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
            "pref_search_1_byte": ps_1byte_ch,
            "pref_search_2_bytes": ps_2byte_ch,
            "pref_search_3_bytes": ps_3byte_ch,
            "pref_search_4_bytes": ps_4byte_ch,
            "pref_search_lengths": ops.asarray1i(pref_search_lengths)
            if pref_search_lengths is not None
            else ops.asarray1i([]),
            "suff_search_1_byte": ss_1byte_ch,
            "suff_search_2_bytes": ss_2byte_ch,
            "suff_search_3_bytes": ss_3byte_ch,
            "suff_search_4_bytes": ss_4byte_ch,
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
    ps_1byte_ch: bytes = model.attrs["pref_search_1_byte"]
    ps_2byte_ch: bytes = model.attrs["pref_search_2_bytes"]
    ps_3byte_ch: bytes = model.attrs["pref_search_3_bytes"]
    ps_4byte_ch: bytes = model.attrs["pref_search_4_bytes"]
    pref_search_lengths: Ints1d = model.attrs["pref_search_lengths"]
    ss_1byte_ch: bytes = model.attrs["pref_search_1_byte"]
    ss_2byte_ch: bytes = model.attrs["pref_search_2_bytes"]
    ss_3byte_ch: bytes = model.attrs["pref_search_3_bytes"]
    ss_4byte_ch: bytes = model.attrs["pref_search_4_bytes"]
    suff_search_lengths: Ints1d = model.attrs["suff_search_lengths"]
    features: List[Ints2d] = []
    for doc in docs:
        hashes = doc.get_character_combination_hashes(
            cs=case_sensitive,
            p_lengths=pref_lengths,
            s_lengths=suff_lengths,
            ps_1byte_ch=ps_1byte_ch,
            ps_2byte_ch=ps_2byte_ch,
            ps_3byte_ch=ps_3byte_ch,
            ps_4byte_ch=ps_4byte_ch,
            ps_lengths=pref_search_lengths,
            ss_1byte_ch=ss_1byte_ch,
            ss_2byte_ch=ss_2byte_ch,
            ss_3byte_ch=ss_3byte_ch,
            ss_4byte_ch=ss_4byte_ch,
            ss_lengths=suff_search_lengths,
        )
        features.append(ops.asarray2i(hashes))

    backprop: Callable[[List[Ints2d]], List] = lambda d_features: []
    return features, backprop
