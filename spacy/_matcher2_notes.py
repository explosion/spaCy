import pytest


class Vocab(object):
    pass


class Doc(list):
    def __init__(self, vocab, words=None):
        list.__init__(self)
        self.extend([Token(i, w) for i, w in enumerate(words)])


class Token(object):
    def __init__(self, i, word):
        self.i = i
        self.text = word


def find_matches(patterns, doc):
    init_states = [(pattern, 0, None) for pattern in patterns]
    curr_states = []
    matches = []
    for token in doc:
        nexts = []
        for state in (curr_states + init_states):
            matches, nexts = transition(state, token, matches, nexts)
        curr_states = nexts
    return matches
 

def transition(state, token, matches, nexts):
    action = get_action(state, token)
    is_match, keep_state, advance_state = [bool(int(c)) for c in action]
    pattern, i, start = state
    if start is None:
        start = token.i
    if is_match:
        matches.append((pattern, start, token.i+1))
    if keep_state:
        nexts.append((pattern, i, start))
    if advance_state:
        nexts.append((pattern, i+1, start))
    return (matches, nexts)


def get_action(state, token):
    '''We need to consider:

    a) Does the token match the specification? [Yes, No]
    b) What's the quantifier? [1, 1+, 0+]
    c) Is this the last specification? [final, non-final]

    We therefore have 12 cases to consider. For each case, we need to know
    whether to emit a match, whether to keep the current state in the partials,
    and whether to add an advanced state to the partials.

    We therefore have eight possible results for these three booleans, which
    we'll code as 000, 001 etc.
    
    - No match:
      000
    - Match, final:
        1: 100
        1+: 110
    - Match, non-final:
        1: 001
        1+: 011

    Problem: If a quantifier is matching, we're adding a lot of open partials
    '''
    is_match = get_is_match(state, token)
    operator = get_operator(state, token)
    is_final = get_is_final(state, token)
    if operator == '1':
        if not is_match:
            return '000'
        elif is_final:
            return '100'
        else:
            return '001'
    elif operator == '1+':
        if not is_match:
            return '000'
        if is_final:
            return '110'
        else:
            return '011'
    elif operator == '0+':
        if is_final:
            return '100'
        elif is_match:
            return '011'
        else:
            return '010'
    else:
        print(operator, is_match, is_final)
        raise ValueError


def get_is_match(state, token):
    pattern, i, start = state
    is_match = token.text == pattern[i]['spec']
    if pattern[i].get('invert'):
        return not is_match
    else:
        return is_match

def get_is_final(state, token):
    pattern, i, start = state
    return i == len(pattern)-1

def get_operator(state, token):
    pattern, i, start = state
    return pattern[i].get('op', '1')


########################
# Tests for get_action #
########################


def test_get_action_simple_match():
    pattern = [{'spec': 'a', 'op': '1'}]
    doc = Doc(Vocab(), words=['a'])
    state = (pattern, 0, None)
    action = get_action(state, doc[0])
    assert action == '100'


def test_get_action_simple_reject():
    pattern = [{'spec': 'b', 'op': '1'}]
    doc = Doc(Vocab(), words=['a'])
    state = (pattern, 0, None)
    action = get_action(state, doc[0])
    assert action == '000'


def test_get_action_simple_match_match():
    pattern = [{'spec': 'a', 'op': '1'}, {'spec': 'a', 'op': '1'}]
    doc = Doc(Vocab(), words=['a', 'a'])
    state = (pattern, 0, None)
    action = get_action(state, doc[0])
    assert action == '001'
    state = (pattern, 1, 0)
    action = get_action(state, doc[1])
    assert action == '100'


def test_get_action_simple_match_reject():
    pattern = [{'spec': 'a', 'op': '1'}, {'spec': 'b', 'op': '1'}]
    doc = Doc(Vocab(), words=['a', 'a'])
    state = (pattern, 0, None)
    action = get_action(state, doc[0])
    assert action == '001'
    state = (pattern, 1, 0)
    action = get_action(state, doc[1])
    assert action == '000'


def test_get_action_simple_match_reject():
    pattern = [{'spec': 'a', 'op': '1'}, {'spec': 'b', 'op': '1'}]
    doc = Doc(Vocab(), words=['a', 'a'])
    state = (pattern, 0, None)
    action = get_action(state, doc[0])
    assert action == '001'
    state = (pattern, 1, 0)
    action = get_action(state, doc[1])
    assert action == '000'


def test_get_action_plus_match():
    pattern = [{'spec': 'a', 'op': '1+'}]
    doc = Doc(Vocab(), words=['a'])
    state = (pattern, 0, None)
    action = get_action(state, doc[0])
    assert action == '110'


def test_get_action_plus_match_match():
    pattern = [{'spec': 'a', 'op': '1+'}]
    doc = Doc(Vocab(), words=['a', 'a'])
    state = (pattern, 0, None)
    action = get_action(state, doc[0])
    assert action == '110'
    state = (pattern, 0, 0)
    action = get_action(state, doc[1])
    assert action == '110'


##########################
# Tests for find_matches #
##########################

def test_find_matches_simple_accept():
    pattern = [{'spec': 'a', 'op': '1'}]
    doc = Doc(Vocab(), words=['a'])
    matches = find_matches([pattern], doc)
    assert matches == [(pattern, 0, 1)]


def test_find_matches_simple_reject():
    pattern = [{'spec': 'a', 'op': '1'}]
    doc = Doc(Vocab(), words=['b'])
    matches = find_matches([pattern], doc)
    assert matches == []


def test_find_matches_match_twice():
    pattern = [{'spec': 'a', 'op': '1'}]
    doc = Doc(Vocab(), words=['a', 'a'])
    matches = find_matches([pattern], doc)
    assert matches == [(pattern, 0, 1), (pattern, 1, 2)]


def test_find_matches_longer_pattern():
    pattern = [{'spec': 'a', 'op': '1'}, {'spec': 'b', 'op': '1'}]
    doc = Doc(Vocab(), words=['a', 'b'])
    matches = find_matches([pattern], doc)
    assert matches == [(pattern, 0, 2)]


def test_find_matches_two_patterns():
    patterns = [[{'spec': 'a', 'op': '1'}], [{'spec': 'b', 'op': '1'}]]
    doc = Doc(Vocab(), words=['a', 'b'])
    matches = find_matches(patterns, doc)
    assert matches == [(patterns[0], 0, 1), (patterns[1], 1, 2)]


def test_find_matches_two_patterns_overlap():
    patterns = [[{'spec': 'a'}, {'spec': 'b'}],
                [{'spec': 'b'}, {'spec': 'c'}]]
    doc = Doc(Vocab(), words=['a', 'b', 'c'])
    matches = find_matches(patterns, doc)
    assert matches == [(patterns[0], 0, 2), (patterns[1], 1, 3)]


def test_find_matches_greedy():
    patterns = [[{'spec': 'a', 'op': '1+'}]]
    doc = Doc(Vocab(), words=['a'])
    matches = find_matches(patterns, doc)
    assert matches == [(patterns[0], 0, 1)]
    doc = Doc(Vocab(), words=['a', 'a'])
    matches = find_matches(patterns, doc)
    assert matches == [(patterns[0], 0, 1), (patterns[0], 0, 2), (patterns[0], 1, 2)]

def test_find_matches_non_greedy():
    patterns = [[{'spec': 'a', 'op': '0+'}, {'spec': 'b'}]]
    doc = Doc(Vocab(), words=['b'])
    matches = find_matches(patterns, doc)
    assert matches == [(patterns[0], 0, 1)]
