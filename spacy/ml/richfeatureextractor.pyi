from ..tokens import Doc

def get_character_combination_hashes(
    *,
    doc: Doc,
    case_sensitive: bool, 
    p_lengths: bytes,
    s_lengths: bytes,
):