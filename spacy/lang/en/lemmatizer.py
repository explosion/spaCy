from typing import Optional

from ...morphology import Morphology


def is_base_form(univ_pos: str, morphology: Optional[Morphology] = None) -> bool:
    """
    Check whether we're dealing with an uninflected paradigm, so we can
    avoid lemmatization entirely.

    univ_pos (unicode / int): The token's universal part-of-speech tag.
    morphology (dict): The token's morphological features following the
        Universal Dependencies scheme.
    """
    if morphology is None:
        morphology = {}
    if univ_pos == "noun" and morphology.get("Number") == "sing":
        return True
    elif univ_pos == "verb" and morphology.get("VerbForm") == "inf":
        return True
    # This maps 'VBP' to base form -- probably just need 'IS_BASE'
    # morphology
    elif univ_pos == "verb" and (
        morphology.get("VerbForm") == "fin"
        and morphology.get("Tense") == "pres"
        and morphology.get("Number") is None
    ):
        return True
    elif univ_pos == "adj" and morphology.get("Degree") == "pos":
        return True
    elif morphology.get("VerbForm") == "inf":
        return True
    elif morphology.get("VerbForm") == "none":
        return True
    elif morphology.get("Degree") == "pos":
        return True
    else:
        return False
