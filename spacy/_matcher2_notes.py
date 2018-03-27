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
    if advance_state:
        nexts.append((pattern, i+1, start))
    if keep_state:
        # TODO: This needs to be zero-width :(.
        nexts.append((pattern, i, start))
    return (matches, nexts)


def get_action(state, token):
    '''We need to consider:

    a) Does the token match the specification? [Yes, No]
    b) What's the quantifier? [1, 0+, ?]
    c) Is this the last specification? [final, non-final]

    We can transition in the following ways:

    a) Do we emit a match?
    b) Do we add a state with (next state, next token)?
    c) Do we add a state with (next state, same token)?
    d) Do we add a state with (same state, next token)?

    We'll code the actions as boolean strings, so 0000 means no to all 4,
    1000 means match but no states added, etc.
    
    1:
      Yes, final:
        1000
      Yes, non-final:
        0100
      No, final:
        0000
      No, non-final
        0000
    0+:
      Yes, final:
        1001
      Yes, non-final:
        0111
      No, final:
        1000 (note: Don't include last token!)
      No, non-final:
        0010
    ?:
      Yes, final:
        1000
      Yes, non-final:
        0100
      No, final:
        1000 (note: Don't include last token!)
      No, non-final:
        0010

    Problem: If a quantifier is matching, we're adding a lot of open partials
    '''
    is_match = get_is_match(state, token)
    operator = get_operator(state, token)
    is_final = get_is_final(state, token)
    raise NotImplementedError


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
    patterns = [[{'spec': 'a', 'op': '0+'}, {'spec': 'b', "op": "1"}]]
    doc = Doc(Vocab(), words=['b'])
    matches = find_matches(patterns, doc)
    assert matches == [(patterns[0], 0, 1)]
