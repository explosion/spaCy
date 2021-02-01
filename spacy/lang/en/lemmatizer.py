from ...pipeline import Lemmatizer
from ...tokens import Token


class EnglishLemmatizer(Lemmatizer):
    """English lemmatizer. Only overrides is_base_form."""

    def is_base_form(self, token: Token) -> bool:
        """
        Check whether we're dealing with an uninflected paradigm, so we can
        avoid lemmatization entirely.

        univ_pos (unicode / int): The token's universal part-of-speech tag.
        morphology (dict): The token's morphological features following the
            Universal Dependencies scheme.
        """
        univ_pos = token.pos_.lower()
        morphology = token.morph.to_dict()
        if univ_pos == "noun" and morphology.get("Number") == "Sing":
            return True
        elif univ_pos == "verb" and morphology.get("VerbForm") == "Inf":
            return True
        # This maps 'VBP' to base form -- probably just need 'IS_BASE'
        # morphology
        elif univ_pos == "verb" and (
            morphology.get("VerbForm") == "Fin"
            and morphology.get("Tense") == "Pres"
            and morphology.get("Number") is None
        ):
            return True
        elif univ_pos == "adj" and morphology.get("Degree") == "Pos":
            return True
        elif morphology.get("VerbForm") == "Inf":
            return True
        elif morphology.get("VerbForm") == "None":
            return True
        elif morphology.get("Degree") == "Pos":
            return True
        else:
            return False
