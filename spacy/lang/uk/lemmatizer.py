# coding: utf8
from ...symbols import ADJ, DET, NOUN, NUM, PRON, PROPN, PUNCT, VERB, POS
from ...lemmatizer import Lemmatizer


class UkrainianLemmatizer(Lemmatizer):
    _morph = None

    def __init__(self, lookups=None):
        super(UkrainianLemmatizer, self).__init__(lookups)
        try:
            from pymorphy2 import MorphAnalyzer

            if UkrainianLemmatizer._morph is None:
                UkrainianLemmatizer._morph = MorphAnalyzer(lang="uk")
        except (ImportError, TypeError):
            raise ImportError(
                "The Ukrainian lemmatizer requires the pymorphy2 library and "
                'dictionaries: try to fix it with "pip uninstall pymorphy2" and'
                '"pip install git+https://github.com/kmike/pymorphy2.git pymorphy2-dicts-uk"'
            )

    def __call__(self, string, univ_pos, morphology=None):
        univ_pos = self.normalize_univ_pos(univ_pos)
        if univ_pos == "PUNCT":
            return [PUNCT_RULES.get(string, string)]

        if univ_pos not in ("ADJ", "DET", "NOUN", "NUM", "PRON", "PROPN", "VERB"):
            # Skip unchangeable pos
            return [string.lower()]

        analyses = self._morph.parse(string)
        filtered_analyses = []
        for analysis in analyses:
            if not analysis.is_known:
                # Skip suggested parse variant for unknown word for pymorphy
                continue
            analysis_pos, _ = oc2ud(str(analysis.tag))
            if analysis_pos == univ_pos or (
                analysis_pos in ("NOUN", "PROPN") and univ_pos in ("NOUN", "PROPN")
            ):
                filtered_analyses.append(analysis)

        if not len(filtered_analyses):
            return [string.lower()]
        if morphology is None or (len(morphology) == 1 and POS in morphology):
            return list(set([analysis.normal_form for analysis in filtered_analyses]))

        if univ_pos in ("ADJ", "DET", "NOUN", "PROPN"):
            features_to_compare = ["Case", "Number", "Gender"]
        elif univ_pos == "NUM":
            features_to_compare = ["Case", "Gender"]
        elif univ_pos == "PRON":
            features_to_compare = ["Case", "Number", "Gender", "Person"]
        else:  # VERB
            features_to_compare = [
                "Aspect",
                "Gender",
                "Mood",
                "Number",
                "Tense",
                "VerbForm",
                "Voice",
            ]

        analyses, filtered_analyses = filtered_analyses, []
        for analysis in analyses:
            _, analysis_morph = oc2ud(str(analysis.tag))
            for feature in features_to_compare:
                if (
                    feature in morphology
                    and feature in analysis_morph
                    and morphology[feature].lower() != analysis_morph[feature].lower()
                ):
                    break
            else:
                filtered_analyses.append(analysis)

        if not len(filtered_analyses):
            return [string.lower()]
        return list(set([analysis.normal_form for analysis in filtered_analyses]))

    @staticmethod
    def normalize_univ_pos(univ_pos):
        if isinstance(univ_pos, str):
            return univ_pos.upper()

        symbols_to_str = {
            ADJ: "ADJ",
            DET: "DET",
            NOUN: "NOUN",
            NUM: "NUM",
            PRON: "PRON",
            PROPN: "PROPN",
            PUNCT: "PUNCT",
            VERB: "VERB",
        }
        if univ_pos in symbols_to_str:
            return symbols_to_str[univ_pos]
        return None

    def lookup(self, string, orth=None):
        analyses = self._morph.parse(string)
        if len(analyses) == 1:
            return analyses[0].normal_form
        return string


def oc2ud(oc_tag):
    gram_map = {
        "_POS": {
            "ADJF": "ADJ",
            "ADJS": "ADJ",
            "ADVB": "ADV",
            "Apro": "DET",
            "COMP": "ADJ",  # Can also be an ADV - unchangeable
            "CONJ": "CCONJ",  # Can also be a SCONJ - both unchangeable ones
            "GRND": "VERB",
            "INFN": "VERB",
            "INTJ": "INTJ",
            "NOUN": "NOUN",
            "NPRO": "PRON",
            "NUMR": "NUM",
            "NUMB": "NUM",
            "PNCT": "PUNCT",
            "PRCL": "PART",
            "PREP": "ADP",
            "PRTF": "VERB",
            "PRTS": "VERB",
            "VERB": "VERB",
        },
        "Animacy": {"anim": "Anim", "inan": "Inan"},
        "Aspect": {"impf": "Imp", "perf": "Perf"},
        "Case": {
            "ablt": "Ins",
            "accs": "Acc",
            "datv": "Dat",
            "gen1": "Gen",
            "gen2": "Gen",
            "gent": "Gen",
            "loc2": "Loc",
            "loct": "Loc",
            "nomn": "Nom",
            "voct": "Voc",
        },
        "Degree": {"COMP": "Cmp", "Supr": "Sup"},
        "Gender": {"femn": "Fem", "masc": "Masc", "neut": "Neut"},
        "Mood": {"impr": "Imp", "indc": "Ind"},
        "Number": {"plur": "Plur", "sing": "Sing"},
        "NumForm": {"NUMB": "Digit"},
        "Person": {"1per": "1", "2per": "2", "3per": "3", "excl": "2", "incl": "1"},
        "Tense": {"futr": "Fut", "past": "Past", "pres": "Pres"},
        "Variant": {"ADJS": "Brev", "PRTS": "Brev"},
        "VerbForm": {
            "GRND": "Conv",
            "INFN": "Inf",
            "PRTF": "Part",
            "PRTS": "Part",
            "VERB": "Fin",
        },
        "Voice": {"actv": "Act", "pssv": "Pass"},
        "Abbr": {"Abbr": "Yes"},
    }

    pos = "X"
    morphology = dict()
    unmatched = set()

    grams = oc_tag.replace(" ", ",").split(",")
    for gram in grams:
        match = False
        for categ, gmap in sorted(gram_map.items()):
            if gram in gmap:
                match = True
                if categ == "_POS":
                    pos = gmap[gram]
                else:
                    morphology[categ] = gmap[gram]
        if not match:
            unmatched.add(gram)

    while len(unmatched) > 0:
        gram = unmatched.pop()
        if gram in ("Name", "Patr", "Surn", "Geox", "Orgn"):
            pos = "PROPN"
        elif gram == "Auxt":
            pos = "AUX"
        elif gram == "Pltm":
            morphology["Number"] = "Ptan"

    return pos, morphology


PUNCT_RULES = {"«": '"', "»": '"'}
