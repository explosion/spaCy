IDS = {
    "": NULL_ATTR,
    "IS_ALPHA": IS_ALPHA,
    "IS_ASCII": IS_ASCII,
    "IS_DIGIT": IS_DIGIT,
    "IS_LOWER": IS_LOWER,
    "IS_PUNCT": IS_PUNCT,
    "IS_SPACE": IS_SPACE,
    "IS_TITLE": IS_TITLE,
    "IS_UPPER": IS_UPPER,
    "LIKE_URL": LIKE_URL,
    "LIKE_NUM": LIKE_NUM,
    "LIKE_EMAIL": LIKE_EMAIL,
    "IS_STOP": IS_STOP,
    "IS_OOV": IS_OOV,
    "IS_BRACKET": IS_BRACKET,
    "IS_QUOTE": IS_QUOTE,
    "IS_LEFT_PUNCT": IS_LEFT_PUNCT,
    "IS_RIGHT_PUNCT": IS_RIGHT_PUNCT,
    "FLAG18": FLAG18,
    "FLAG19": FLAG19,
    "FLAG20": FLAG20,
    "FLAG21": FLAG21,
    "FLAG22": FLAG22,
    "FLAG23": FLAG23,
    "FLAG24": FLAG24,
    "FLAG25": FLAG25,
    "FLAG26": FLAG26,
    "FLAG27": FLAG27,
    "FLAG28": FLAG28,
    "FLAG29": FLAG29,
    "FLAG30": FLAG30,
    "FLAG31": FLAG31,
    "FLAG32": FLAG32,
    "FLAG33": FLAG33,
    "FLAG34": FLAG34,
    "FLAG35": FLAG35,
    "FLAG36": FLAG36,
    "FLAG37": FLAG37,
    "FLAG38": FLAG38,
    "FLAG39": FLAG39,
    "FLAG40": FLAG40,
    "FLAG41": FLAG41,
    "FLAG42": FLAG42,
    "FLAG43": FLAG43,
    "FLAG44": FLAG44,
    "FLAG45": FLAG45,
    "FLAG46": FLAG46,
    "FLAG47": FLAG47,
    "FLAG48": FLAG48,
    "FLAG49": FLAG49,
    "FLAG50": FLAG50,
    "FLAG51": FLAG51,
    "FLAG52": FLAG52,
    "FLAG53": FLAG53,
    "FLAG54": FLAG54,
    "FLAG55": FLAG55,
    "FLAG56": FLAG56,
    "FLAG57": FLAG57,
    "FLAG58": FLAG58,
    "FLAG59": FLAG59,
    "FLAG60": FLAG60,
    "FLAG61": FLAG61,
    "FLAG62": FLAG62,
    "FLAG63": FLAG63,

    "ID": ID,
    "ORTH": ORTH,
    "LOWER": LOWER,
    "NORM": NORM,
    "SHAPE": SHAPE,
    "PREFIX": PREFIX,
    "SUFFIX": SUFFIX,

    "LENGTH": LENGTH,
    "CLUSTER": CLUSTER,
    "LEMMA": LEMMA,
    "POS": POS,
    "TAG": TAG,
    "DEP": DEP,
    "ENT_IOB": ENT_IOB,
    "ENT_TYPE": ENT_TYPE,
    "HEAD": HEAD,
    "SPACY": SPACY,
    "PROB": PROB,
    "LANG": LANG,
}


# ATTR IDs, in order of the symbol
NAMES = [key for key, value in sorted(IDS.items(), key=lambda item: item[1])]


def intify_attrs(stringy_attrs, strings_map=None, _do_deprecated=False):
    '''Normalize a dictionary of attributes, converting them to ints.
    
    Arguments:
        stringy_attrs (dict):
            Dictionary keyed by attribute string names. Values can be ints or strings.

        strings_map (StringStore):
            Defaults to None. If provided, encodes string values into ints.

    Returns:
        inty_attrs (dict):
            Attributes dictionary with keys and optionally values converted to
            ints.
    '''
    inty_attrs = {}
    if _do_deprecated:
        if 'F' in stringy_attrs:
            stringy_attrs["ORTH"] = stringy_attrs.pop("F")
        if 'L' in stringy_attrs:
            stringy_attrs["LEMMA"] = stringy_attrs.pop("L")
        if 'pos' in stringy_attrs:
            stringy_attrs["TAG"] = stringy_attrs.pop("pos")
        if 'morph' in stringy_attrs:
            morphs = stringy_attrs.pop('morph')
        if 'number' in stringy_attrs:
            stringy_attrs.pop('number')
        if 'tenspect' in stringy_attrs:
            stringy_attrs.pop('tenspect')
        morph_keys = [
            'PunctType', 'PunctSide', 'Other', 'Degree', 'AdvType', 'Number',
            'VerbForm', 'PronType', 'Aspect', 'Tense', 'PartType', 'Poss',
            'Hyph', 'ConjType', 'NumType', 'Foreign', 'VerbType', 'NounType',
            'Number', 'PronType', 'AdjType', 'Person', 'Variant', 'AdpType',
            'Reflex', 'Negative', 'Mood', 'Aspect', 'Case']
        for key in morph_keys:
            if key in stringy_attrs:
                stringy_attrs.pop(key)
            elif key.lower() in stringy_attrs:
                stringy_attrs.pop(key.lower())
            elif key.upper() in stringy_attrs:
                stringy_attrs.pop(key.upper())
    for name, value in stringy_attrs.items():
        if isinstance(name, int):
            int_key = name
        else:
            int_key = IDS[name.upper()]
        if strings_map is not None and isinstance(value, basestring):
            value = strings_map[value]
        inty_attrs[int_key] = value
    return inty_attrs
