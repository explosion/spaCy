USE_PYTOKENIZATIONS = False

try:
    import tokenizations

    USE_PYTOKENIZATIONS = True
except:
    raise ImportError(
        "`_align_with_pytokenizations` requires `pytokenizations`. https://github.com/tamuhey/tokenizations"
    )

_ALIGNMENT_NORM_MAP = dict([("``", "'"), ("''", "'"), ('"', "'"), ("`", "'")])


def _norm(text):
    for k, v in _ALIGNMENT_NORM_MAP.items():
        text = text.replace(k, v)
    return text


def _normalize_for_alignment(tokens):
    return [_norm(token) for token in tokens]


def _get_multialign(pytokenizations_b2a):
    result = {}
    for i, vs in enumerate(pytokenizations_b2a):
        if len(vs) > 1:
            result.update({v: i for v in vs})
    return result


def _get_cost(pytokenizations_a2b, pytokenizations_b2a):
    return sum(
        1
        for a in pytokenizations_a2b
        if len(a) != 1 or len(pytokenizations_b2a[a[0]]) != 1
    )


def _get_single_align(pytokenizations_a2b, pytokenizations_b2a):
    return [
        a[0] if len(a) == 1 and len(pytokenizations_b2a[a[0]]) == 1 else -1
        for a in pytokenizations_a2b
    ]


def align_with_pytokenizations(tokens_a, tokens_b):
    tokens_a = _normalize_for_alignment(tokens_a)
    tokens_b = _normalize_for_alignment(tokens_b)
    ta2b, tb2a = tokenizations.get_alignments(tokens_a, tokens_b)
    a2b = _get_single_align(ta2b, tb2a)
    b2a = _get_single_align(tb2a, ta2b)
    a2b_multi = _get_multialign(tb2a)
    b2a_multi = _get_multialign(ta2b)
    cost = _get_cost(ta2b, tb2a) + _get_cost(tb2a, ta2b)
    return cost, a2b, b2a, a2b_multi, b2a_multi
