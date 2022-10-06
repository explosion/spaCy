from typing import List, Optional, Callable, Tuple
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
    return Model(
        "extract_character_combination_hashes",
        forward,
        attrs={
            "case_sensitive": case_sensitive,
            "pref_lengths": pref_lengths if pref_lengths is not None else [],
            "pref_search_chars": pref_search_chars
            if pref_search_chars is not None
            else "",
            "pref_search_lengths": pref_search_lengths
            if pref_search_lengths is not None
            else [],
            "suff_lengths": suff_lengths if suff_lengths is not None else [],
            "suff_search_chars": suff_search_chars
            if suff_search_chars is not None
            else "",
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
    pref_search_chars: str = model.attrs["pref_search_chars"]
    pref_search_lengths: List[int] = model.attrs["pref_search_lengths"]
    suff_lengths: List[int] = model.attrs["suff_lengths"]
    suff_search_chars: str = model.attrs["suff_search_chars"]
    suff_search_lengths: List[int] = model.attrs["suff_search_lengths"]
    features: List[Ints2d] = []
    for doc in docs:
        prefix_hashes = doc.get_character_combination_hashes(
            case_sensitive=case_sensitive,
            suffs_not_prefs=False,
            affix_lengths=pref_lengths,
            search_chars=pref_search_chars,
            search_lengths=pref_search_lengths,
        )
        suffix_hashes = doc.get_character_combination_hashes(
            case_sensitive=case_sensitive,
            suffs_not_prefs=True,
            affix_lengths=suff_lengths,
            search_chars=suff_search_chars,
            search_lengths=suff_search_lengths,
        )
        features.append(ops.asarray2i(ops.xp.hstack([prefix_hashes, suffix_hashes])))

    backprop: Callable[[List[Ints2d]], List] = lambda d_features: []
    return features, backprop
