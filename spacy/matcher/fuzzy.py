from .levenshtein import levenshtein

def fuzzy_match(input_string: str, rule_string: str, distance: int=0) -> bool:
    """Define in pure Python outside Matcher to allow patching.

    Patch with e.g.:
        import wrapt
        from spacy.matcher import fuzzy
        @wrapt.patch_function_wrapper('spacy.matcher.fuzzy', 'fuzzy_match')
    *before* import spacy
    """
    min_length = min(len(input_string), len(rule_string))
    if distance: # FUZZYn operators with explicit distance
        threshold = min(distance, min_length - 1)
    else: # FUZZY operator with default distance
        threshold = min(5, min_length - 2)
    if threshold > 0:
        return levenshtein(input_string, rule_string) <= threshold
    return False
