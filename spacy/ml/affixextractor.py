from typing import List, Optional, Callable, Tuple
from thinc.types import Ints2d
from thinc.api import Model, registry, get_current_ops

from ..tokens import Doc


@registry.layers("spacy.AffixExtractor.v1")
def AffixExtractor(
    *,
    suffs_not_prefs: bool,
    case_sensitive: bool,
    len_start: Optional[int],
    len_end: Optional[int],
    special_chars: Optional[str],
    sc_len_start: Optional[int],
    sc_len_end: Optional[int],
) -> Model[List[Doc], List[Ints2d]]:
    return Model(
        "extract_affixes",
        forward,
        attrs={
            "suffs_not_prefs": suffs_not_prefs,
            "case_sensitive": case_sensitive,
            "len_start": len_start if len_start is not None else 0,
            "len_end": len_end if len_end is not None else 0,
            "special_chars": special_chars if special_chars is not None else "",
            "sc_len_start": sc_len_start if sc_len_start is not None else 0,
            "sc_len_end": sc_len_end if sc_len_end is not None else 0,
        },
    )


def forward(
    model: Model[List[Doc], List[Ints2d]], docs, is_train: bool
) -> Tuple[List[Ints2d], Callable]:
    suffs_not_prefs: bool = model.attrs["suffs_not_prefs"]
    case_sensitive: bool = model.attrs["case_sensitive"]
    len_start: int = model.attrs["len_start"]
    len_end: int = model.attrs["len_end"]
    special_chars: str = model.attrs["special_chars"]
    sc_len_start: int = model.attrs["sc_len_start"]
    sc_len_end: int = model.attrs["sc_len_end"]
    features: List[Ints2d] = []
    for doc in docs:
        features.append(
            model.ops.asarray2i(
                doc.get_affix_hashes(
                    suffs_not_prefs,
                    case_sensitive,
                    len_start,
                    len_end,
                    special_chars,
                    sc_len_start,
                    sc_len_end,
                )
            )
        )

    backprop: Callable[[List[Ints2d]], List] = lambda d_features: []
    return features, backprop
