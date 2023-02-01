from typing import List, Optional
from thinc.types import Ints2d
from thinc.api import Model
from ..tokens import Doc

def RichFeatureExtractor(
    *,
    case_sensitive: bool,
    pref_lengths: Optional[List[int]] = None,
    suff_lengths: Optional[List[int]] = None,
) -> Model[List[Doc], List[Ints2d]]: ...
def get_character_combination_hashes(
    *,
    doc: Doc,
    case_sensitive: bool,
    p_lengths: bytes,
    s_lengths: bytes,
): ...
