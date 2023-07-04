# cython: binding=True, infer_types=True, profile=True
from typing import Iterable, List

from cymem.cymem cimport Pool
from libc.stdint cimport int8_t, int32_t
from libc.string cimport memcmp, memset
from libcpp.vector cimport vector
from murmurhash.mrmr cimport hash64

import re
import warnings

import srsly

from ..attrs cimport (
    DEP,
    ENT_IOB,
    ID,
    LEMMA,
    MORPH,
    NULL_ATTR,
    ORTH,
    POS,
    TAG,
    attr_id_t,
)
from ..structs cimport TokenC
from ..tokens.doc cimport Doc, get_token_attr_for_matcher
from ..tokens.morphanalysis cimport MorphAnalysis
from ..tokens.span cimport Span
from ..tokens.token cimport Token
from ..typedefs cimport attr_t
from ..vocab cimport Vocab

from ..attrs import IDS
from ..errors import Errors, MatchPatternError, Warnings
from ..schemas import validate_token_pattern
from ..strings import get_string_id
from ..util import registry
from .levenshtein import levenshtein_compare

DEF PADDING = 5


cdef class Matcher:
    """Match sequences of tokens, based on pattern rules.

    DOCS: https://spacy.io/api/matcher
    USAGE: https://spacy.io/usage/rule-based-matching
    """

    def __init__(self, vocab, validate=True, *, fuzzy_compare=levenshtein_compare):
        """Create the Matcher.

        vocab (Vocab): The vocabulary object, which must be shared with the
        validate (bool): Validate all patterns added to this matcher.
        fuzzy_compare (Callable[[str, str, int], bool]): The comparison method
            for the FUZZY operators.
        """
        self._extra_predicates = []
        self._patterns = {}
        self._callbacks = {}
        self._filter = {}
        self._extensions = {}
        self._seen_attrs = set()
        self.vocab = vocab
        self.mem = Pool()
        self.validate = validate
        self._fuzzy_compare = fuzzy_compare

    def __reduce__(self):
        data = (self.vocab, self._patterns, self._callbacks, self.validate, self._fuzzy_compare)
        return (unpickle_matcher, data, None, None)

    def __len__(self):
        """Get the number of rules added to the matcher. Note that this only
        returns the number of rules (identical with the number of IDs), not the
        number of individual patterns.

        RETURNS (int): The number of rules.
        """
        return len(self._patterns)

    def __contains__(self, key):
        """Check whether the matcher contains rules for a match ID.

        key (str): The match ID.
        RETURNS (bool): Whether the matcher contains rules for this match ID.
        """
        return self.has_key(key)

    def add(self, key, patterns, *, on_match=None, greedy: str=None):
        """Add a match-rule to the matcher. A match-rule consists of: an ID
        key, an on_match callback, and one or more patterns.

        If the key exists, the patterns are appended to the previous ones, and
        the previous on_match callback is replaced. The `on_match` callback
        will receive the arguments `(matcher, doc, i, matches)`. You can also
        set `on_match` to `None` to not perform any actions.

        A pattern consists of one or more `token_specs`, where a `token_spec`
        is a dictionary mapping attribute IDs to values, and optionally a
        quantifier operator under the key "op". The available quantifiers are:

        '!':      Negate the pattern, by requiring it to match exactly 0 times.
        '?':      Make the pattern optional, by allowing it to match 0 or 1 times.
        '+':      Require the pattern to match 1 or more times.
        '*':      Allow the pattern to zero or more times.
        '{n}':    Require the pattern to match exactly _n_ times.
        '{n,m}':  Require the pattern to match at least _n_ but not more than _m_ times.
        '{n,}':   Require the pattern to match at least _n_ times.
        '{,m}':   Require the pattern to match at most _m_ times.

        The + and * operators return all possible matches (not just the greedy
        ones). However, the "greedy" argument can filter the final matches
        by returning a non-overlapping set per key, either taking preference to
        the first greedy match ("FIRST"), or the longest ("LONGEST").

        Since spaCy v2.2.2, Matcher.add takes a list of patterns as the second
        argument, and the on_match callback is an optional keyword argument.

        key (Union[str, int]): The match ID.
        patterns (list): The patterns to add for the given key.
        on_match (callable): Optional callback executed on match.
        greedy (str): Optional filter: "FIRST" or "LONGEST".
        """
        errors = {}
        if on_match is not None and not hasattr(on_match, "__call__"):
            raise ValueError(Errors.E171.format(arg_type=type(on_match)))
        if patterns is None or not isinstance(patterns, List):  # old API
            raise ValueError(Errors.E948.format(arg_type=type(patterns)))
        if greedy is not None and greedy not in ["FIRST", "LONGEST"]:
            raise ValueError(Errors.E947.format(expected=["FIRST", "LONGEST"], arg=greedy))
        for i, pattern in enumerate(patterns):
            if len(pattern) == 0:
                raise ValueError(Errors.E012.format(key=key))
            if not isinstance(pattern, list):
                raise ValueError(Errors.E178.format(pat=pattern, key=key))
            if self.validate:
                errors[i] = validate_token_pattern(pattern)
        if any(err for err in errors.values()):
            raise MatchPatternError(key, errors)
        key = self._normalize_key(key)
        for pattern in patterns:
            try:
                specs = _preprocess_pattern(pattern, self.vocab,
                    self._extensions, self._extra_predicates, self._fuzzy_compare)
                self.patterns.push_back(init_pattern(self.mem, key, specs))
                for spec in specs:
                    for attr, _ in spec[1]:
                        self._seen_attrs.add(attr)
            except OverflowError, AttributeError:
                raise ValueError(Errors.E154.format()) from None
        self._patterns.setdefault(key, [])
        self._callbacks[key] = on_match
        self._filter[key] = greedy
        self._patterns[key].extend(patterns)

    def _require_patterns(self) -> None:
        """Raise a warning if this component has no patterns defined."""
        if len(self) == 0:
            warnings.warn(Warnings.W036.format(name="matcher"))

    def remove(self, key):
        """Remove a rule from the matcher. A KeyError is raised if the key does
        not exist.

        key (str): The ID of the match rule.
        """
        norm_key = self._normalize_key(key)
        if not norm_key in self._patterns:
            raise ValueError(Errors.E175.format(key=key))
        self._patterns.pop(norm_key)
        self._callbacks.pop(norm_key)
        cdef int i = 0
        while i < self.patterns.size():
            pattern_key = get_ent_id(self.patterns.at(i))
            if pattern_key == norm_key:
                self.patterns.erase(self.patterns.begin()+i)
            else:
                i += 1

    def has_key(self, key):
        """Check whether the matcher has a rule with a given key.

        key (string or int): The key to check.
        RETURNS (bool): Whether the matcher has the rule.
        """
        return self._normalize_key(key) in self._patterns

    def get(self, key, default=None):
        """Retrieve the pattern stored for a key.

        key (str / int): The key to retrieve.
        RETURNS (tuple): The rule, as an (on_match, patterns) tuple.
        """
        key = self._normalize_key(key)
        if key not in self._patterns:
            return default
        return (self._callbacks[key], self._patterns[key])

    def pipe(self, docs, batch_size=1000, return_matches=False, as_tuples=False):
        """Match a stream of documents, yielding them in turn. Deprecated as of
        spaCy v3.0.
        """
        warnings.warn(Warnings.W105.format(matcher="Matcher"), DeprecationWarning)
        if as_tuples:
            for doc, context in docs:
                matches = self(doc)
                if return_matches:
                    yield ((doc, matches), context)
                else:
                    yield (doc, context)
        else:
            for doc in docs:
                matches = self(doc)
                if return_matches:
                    yield (doc, matches)
                else:
                    yield doc

    def __call__(self, object doclike, *, as_spans=False, allow_missing=False, with_alignments=False):
        """Find all token sequences matching the supplied pattern.

        doclike (Doc or Span): The document to match over.
        as_spans (bool): Return Span objects with labels instead of (match_id,
            start, end) tuples.
        allow_missing (bool): Whether to skip checks for missing annotation for
            attributes included in patterns. Defaults to False.
        with_alignments (bool): Return match alignment information, which is
            `List[int]` with length of matched span. Each entry denotes the
            corresponding index of token pattern. If as_spans is set to True,
            this setting is ignored.
        RETURNS (list): A list of `(match_id, start, end)` tuples,
            describing the matches. A match tuple describes a span
            `doc[start:end]`. The `match_id` is an integer. If as_spans is set
            to True, a list of Span objects is returned.
            If with_alignments is set to True and as_spans is set to False,
            A list of `(match_id, start, end, alignments)` tuples is returned.
        """
        self._require_patterns()
        if isinstance(doclike, Doc):
            doc = doclike
            length = len(doc)
        elif isinstance(doclike, Span):
            doc = doclike.doc
            length = doclike.end - doclike.start
        else:
            raise ValueError(Errors.E195.format(good="Doc or Span", got=type(doclike).__name__))
        # Skip alignments calculations if as_spans is set
        if as_spans:
            with_alignments = False
        cdef Pool tmp_pool = Pool()
        if not allow_missing:
            for attr in (TAG, POS, MORPH, LEMMA, DEP):
                if attr in self._seen_attrs and not doc.has_annotation(attr):
                    if attr == TAG:
                        pipe = "tagger"
                    elif attr in (POS, MORPH):
                        pipe = "morphologizer or tagger+attribute_ruler"
                    elif attr == LEMMA:
                        pipe = "lemmatizer"
                    elif attr == DEP:
                        pipe = "parser"
                    error_msg = Errors.E155.format(pipe=pipe, attr=self.vocab.strings.as_string(attr))
                    raise ValueError(error_msg)

        if self.patterns.empty():
            matches = []
        else:
            matches = find_matches(&self.patterns[0], self.patterns.size(), doclike, length,
                                    extensions=self._extensions, predicates=self._extra_predicates, with_alignments=with_alignments)
        final_matches = []
        pairs_by_id = {}
        # For each key, either add all matches, or only the filtered,
        # non-overlapping ones this `match` can be either (start, end) or
        # (start, end, alignments) depending on `with_alignments=` option.
        for key, *match in matches:
            span_filter = self._filter.get(key)
            if span_filter is not None:
                pairs = pairs_by_id.get(key, [])
                pairs.append(match)
                pairs_by_id[key] = pairs
            else:
                final_matches.append((key, *match))
        matched = <char*>tmp_pool.alloc(length, sizeof(char))
        empty = <char*>tmp_pool.alloc(length, sizeof(char))
        for key, pairs in pairs_by_id.items():
            memset(matched, 0, length * sizeof(matched[0]))
            span_filter = self._filter.get(key)
            if span_filter == "FIRST":
                sorted_pairs = sorted(pairs, key=lambda x: (x[0], -x[1]), reverse=False) # sort by start
            elif span_filter == "LONGEST":
                sorted_pairs = sorted(pairs, key=lambda x: (x[1]-x[0], -x[0]), reverse=True) # reverse sort by length
            else:
                raise ValueError(Errors.E947.format(expected=["FIRST", "LONGEST"], arg=span_filter))
            for match in sorted_pairs:
                start, end = match[:2]
                assert 0 <= start < end  # Defend against segfaults
                span_len = end-start
                # If no tokens in the span have matched
                if memcmp(&matched[start], &empty[start], span_len * sizeof(matched[0])) == 0:
                    final_matches.append((key, *match))
                    # Mark tokens that have matched
                    memset(&matched[start], 1, span_len * sizeof(matched[0]))
        if as_spans:
            final_results = []
            for key, start, end, *_ in final_matches:
                if isinstance(doclike, Span):
                    start += doclike.start
                    end += doclike.start
                final_results.append(Span(doc, start, end, label=key))
        elif with_alignments:
            # convert alignments List[Dict[str, int]] --> List[int]
            # when multiple alignment (belongs to the same length) is found,
            # keeps the alignment that has largest token_idx
            final_results = []
            for key, start, end, alignments in final_matches:
                sorted_alignments = sorted(alignments, key=lambda x: (x['length'], x['token_idx']), reverse=False)
                alignments = [0] * (end-start)
                for align in sorted_alignments:
                    if align['length'] >= end-start:
                        continue
                    # Since alignments are sorted in order of (length, token_idx)
                    # this overwrites smaller token_idx when they have same length.
                    alignments[align['length']] = align['token_idx']
                final_results.append((key, start, end, alignments))
            final_matches = final_results  # for callbacks
        else:
            final_results = final_matches
        # perform the callbacks on the filtered set of results
        for i, (key, *_) in enumerate(final_matches):
            on_match = self._callbacks.get(key, None)
            if on_match is not None:
                on_match(self, doc, i, final_matches)
        return final_results

    def _normalize_key(self, key):
        if isinstance(key, str):
            return self.vocab.strings.add(key)
        else:
            return key


def unpickle_matcher(vocab, patterns, callbacks, validate, fuzzy_compare):
    matcher = Matcher(vocab, validate=validate, fuzzy_compare=fuzzy_compare)
    for key, pattern in patterns.items():
        callback = callbacks.get(key, None)
        matcher.add(key, pattern, on_match=callback)
    return matcher


cdef find_matches(TokenPatternC** patterns, int n, object doclike, int length, extensions=None, predicates=tuple(), bint with_alignments=0):
    """Find matches in a doc, with a compiled array of patterns. Matches are
    returned as a list of (id, start, end) tuples or (id, start, end, alignments) tuples (if with_alignments != 0)

    To augment the compiled patterns, we optionally also take two Python lists.

    The "predicates" list contains functions that take a Python list and return a
    boolean value. It's mostly used for regular expressions.

    The "extensions" list contains functions that take a Python list and return
    an attr ID. It's mostly used for extension attributes.
    """
    cdef vector[PatternStateC] states
    cdef vector[MatchC] matches
    cdef vector[vector[MatchAlignmentC]] align_states
    cdef vector[vector[MatchAlignmentC]] align_matches
    cdef PatternStateC state
    cdef int i, j, nr_extra_attr
    cdef Pool mem = Pool()
    output = []
    if length == 0:
        # avoid any processing or mem alloc if the document is empty
        return output
    if len(predicates) > 0:
        predicate_cache = <int8_t*>mem.alloc(length * len(predicates), sizeof(int8_t))
    if extensions is not None and len(extensions) >= 1:
        nr_extra_attr = max(extensions.values()) + 1
        extra_attr_values = <attr_t*>mem.alloc(length * nr_extra_attr, sizeof(attr_t))
    else:
        nr_extra_attr = 0
        extra_attr_values = <attr_t*>mem.alloc(length, sizeof(attr_t))
    for i, token in enumerate(doclike):
        for name, index in extensions.items():
            value = token._.get(name)
            if isinstance(value, str):
                value = token.vocab.strings[value]
            extra_attr_values[i * nr_extra_attr + index] = value
    # Main loop
    cdef int nr_predicate = len(predicates)
    for i in range(length):
        for j in range(n):
            states.push_back(PatternStateC(patterns[j], i, 0))
        if with_alignments != 0:
            align_states.resize(states.size())
        transition_states(states, matches, align_states, align_matches, predicate_cache,
            doclike[i], extra_attr_values, predicates, with_alignments)
        extra_attr_values += nr_extra_attr
        predicate_cache += len(predicates)
    # Handle matches that end in 0-width patterns
    finish_states(matches, states, align_matches, align_states, with_alignments)
    seen = set()
    for i in range(matches.size()):
        match = (
            matches[i].pattern_id,
            matches[i].start,
            matches[i].start+matches[i].length
        )
        # We need to deduplicate, because we could otherwise arrive at the same
        # match through two paths, e.g. .?.? matching 'a'. Are we matching the
        # first .?, or the second .? -- it doesn't matter, it's just one match.
        # Skip 0-length matches. (TODO: fix algorithm)
        if match not in seen and matches[i].length > 0:
            if with_alignments != 0:
                # since the length of align_matches equals to that of match, we can share same 'i'
                output.append(match + (align_matches[i],))
            else:
                output.append(match)
            seen.add(match)
    return output


cdef void transition_states(vector[PatternStateC]& states, vector[MatchC]& matches,
                            vector[vector[MatchAlignmentC]]& align_states, vector[vector[MatchAlignmentC]]& align_matches,
                            int8_t* cached_py_predicates,
        Token token, const attr_t* extra_attrs, py_predicates, bint with_alignments) except *:
    cdef int q = 0
    cdef vector[PatternStateC] new_states
    cdef vector[vector[MatchAlignmentC]] align_new_states
    cdef int nr_predicate = len(py_predicates)
    for i in range(states.size()):
        if states[i].pattern.nr_py >= 1:
            update_predicate_cache(cached_py_predicates,
                states[i].pattern, token, py_predicates)
        action = get_action(states[i], token.c, extra_attrs,
                            cached_py_predicates)
        if action == REJECT:
            continue
        # Keep only a subset of states (the active ones). Index q is the
        # states which are still alive. If we reject a state, we overwrite
        # it in the states list, because q doesn't advance.
        state = states[i]
        states[q] = state
        # Separate from states, performance is guaranteed for users who only need basic options (without alignments).
        # `align_states` always corresponds to `states` 1:1.
        if with_alignments != 0:
            align_state = align_states[i]
            align_states[q] = align_state
        while action in (RETRY, RETRY_ADVANCE, RETRY_EXTEND):
            # Update alignment before the transition of current state
            # 'MatchAlignmentC' maps 'original token index of current pattern' to 'current matching length'
            if with_alignments != 0:
                align_states[q].push_back(MatchAlignmentC(states[q].pattern.token_idx, states[q].length))
            if action == RETRY_EXTEND:
                # This handles the 'extend'
                new_states.push_back(
                    PatternStateC(pattern=states[q].pattern, start=state.start,
                                  length=state.length+1))
                if with_alignments != 0:
                    align_new_states.push_back(align_states[q])
            if action == RETRY_ADVANCE:
                # This handles the 'advance'
                new_states.push_back(
                    PatternStateC(pattern=states[q].pattern+1, start=state.start,
                                  length=state.length+1))
                if with_alignments != 0:
                    align_new_states.push_back(align_states[q])
            states[q].pattern += 1
            if states[q].pattern.nr_py != 0:
                update_predicate_cache(cached_py_predicates,
                    states[q].pattern, token, py_predicates)
            action = get_action(states[q], token.c, extra_attrs,
                                cached_py_predicates)
        # Update alignment before the transition of current state
        if with_alignments != 0:
            align_states[q].push_back(MatchAlignmentC(states[q].pattern.token_idx, states[q].length))
        if action == REJECT:
            pass
        elif action == ADVANCE:
            states[q].pattern += 1
            states[q].length += 1
            q += 1
        else:
            ent_id = get_ent_id(state.pattern)
            if action == MATCH:
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start,
                            length=state.length+1))
                # `align_matches` always corresponds to `matches` 1:1
                if with_alignments != 0:
                    align_matches.push_back(align_states[q])
            elif action == MATCH_DOUBLE:
                # push match without last token if length > 0
                if state.length > 0:
                    matches.push_back(
                        MatchC(pattern_id=ent_id, start=state.start,
                                length=state.length))
                    # MATCH_DOUBLE emits matches twice,
                    # add one more to align_matches in order to keep 1:1 relationship
                    if with_alignments != 0:
                        align_matches.push_back(align_states[q])
                # push match with last token
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start,
                            length=state.length+1))
                # `align_matches` always corresponds to `matches` 1:1
                if with_alignments != 0:
                    align_matches.push_back(align_states[q])
            elif action == MATCH_REJECT:
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start,
                            length=state.length))
                # `align_matches` always corresponds to `matches` 1:1
                if with_alignments != 0:
                    align_matches.push_back(align_states[q])
            elif action == MATCH_EXTEND:
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start,
                           length=state.length))
                # `align_matches` always corresponds to `matches` 1:1
                if with_alignments != 0:
                    align_matches.push_back(align_states[q])
                states[q].length += 1
                q += 1
    states.resize(q)
    for i in range(new_states.size()):
        states.push_back(new_states[i])
    # `align_states` always corresponds to `states` 1:1
    if with_alignments != 0:
        align_states.resize(q)
        for i in range(align_new_states.size()):
            align_states.push_back(align_new_states[i])


cdef int update_predicate_cache(int8_t* cache,
        const TokenPatternC* pattern, Token token, predicates) except -1:
    # If the state references any extra predicates, check whether they match.
    # These are cached, so that we don't call these potentially expensive
    # Python functions more than we need to.
    for i in range(pattern.nr_py):
        index = pattern.py_predicates[i]
        if cache[index] == 0:
            predicate = predicates[index]
            result = predicate(token)
            if result is True:
                cache[index] = 1
            elif result is False:
                cache[index] = -1
            elif result is None:
                pass
            else:
                raise ValueError(Errors.E125.format(value=result))


cdef void finish_states(vector[MatchC]& matches, vector[PatternStateC]& states,
                        vector[vector[MatchAlignmentC]]& align_matches,
                        vector[vector[MatchAlignmentC]]& align_states,
                        bint with_alignments) except *:
    """Handle states that end in zero-width patterns."""
    cdef PatternStateC state
    cdef vector[MatchAlignmentC] align_state
    for i in range(states.size()):
        state = states[i]
        if with_alignments != 0:
            align_state = align_states[i]
        while get_quantifier(state) in (ZERO_PLUS, ZERO_ONE):
            # Update alignment before the transition of current state
            if with_alignments != 0:
                align_state.push_back(MatchAlignmentC(state.pattern.token_idx, state.length))
            is_final = get_is_final(state)
            if is_final:
                ent_id = get_ent_id(state.pattern)
                # `align_matches` always corresponds to `matches` 1:1
                if with_alignments != 0:
                    align_matches.push_back(align_state)
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start, length=state.length))
                break
            else:
                state.pattern += 1


cdef action_t get_action(PatternStateC state,
        const TokenC* token, const attr_t* extra_attrs,
        const int8_t* predicate_matches) nogil:
    """We need to consider:
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
        0011
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

    Possible combinations:  1000, 0100, 0000, 1001, 0110, 0011, 0010,

    We'll name the bits "match", "advance", "retry", "extend"
    REJECT = 0000
    MATCH = 1000
    ADVANCE = 0100
    RETRY = 0010
    MATCH_EXTEND = 1001
    RETRY_ADVANCE = 0110
    RETRY_EXTEND = 0011
    MATCH_REJECT = 2000 # Match, but don't include last token
    MATCH_DOUBLE = 3000 # Match both with and without last token

    Problem: If a quantifier is matching, we're adding a lot of open partials
    """
    cdef int8_t is_match
    is_match = get_is_match(state, token, extra_attrs, predicate_matches)
    quantifier = get_quantifier(state)
    is_final = get_is_final(state)
    if quantifier == ZERO:
        is_match = not is_match
        quantifier = ONE
    if quantifier == ONE:
      if is_match and is_final:
          # Yes, final: 1000
          return MATCH
      elif is_match and not is_final:
          # Yes, non-final: 0100
          return ADVANCE
      elif not is_match and is_final:
          # No, final: 0000
          return REJECT
      else:
          return REJECT
    elif quantifier == ZERO_PLUS:
      if is_match and is_final:
          # Yes, final: 1001
          return MATCH_EXTEND
      elif is_match and not is_final:
          # Yes, non-final: 0011
          return RETRY_EXTEND
      elif not is_match and is_final:
          # No, final 2000 (note: Don't include last token!)
          return MATCH_REJECT
      else:
          # No, non-final 0010
          return RETRY
    elif quantifier == ZERO_ONE:
      if is_match and is_final:
          # Yes, final: 3000
          # To cater for a pattern ending in "?", we need to add
          # a match both with and without the last token
          return MATCH_DOUBLE
      elif is_match and not is_final:
          # Yes, non-final: 0110
          # We need both branches here, consider a pair like:
          # pattern: .?b string: b
          # If we 'ADVANCE' on the .?, we miss the match.
          return RETRY_ADVANCE
      elif not is_match and is_final:
          # No, final 2000 (note: Don't include last token!)
          return MATCH_REJECT
      else:
          # No, non-final 0010
          return RETRY


cdef int8_t get_is_match(PatternStateC state,
        const TokenC* token, const attr_t* extra_attrs,
        const int8_t* predicate_matches) nogil:
    for i in range(state.pattern.nr_py):
        if predicate_matches[state.pattern.py_predicates[i]] == -1:
            return 0
    spec = state.pattern
    if spec.nr_attr > 0:
        for attr in spec.attrs[:spec.nr_attr]:
            if get_token_attr_for_matcher(token, attr.attr) != attr.value:
                return 0
    for i in range(spec.nr_extra_attr):
        if spec.extra_attrs[i].value != extra_attrs[spec.extra_attrs[i].index]:
            return 0
    return True


cdef inline int8_t get_is_final(PatternStateC state) nogil:
    if state.pattern[1].quantifier == FINAL_ID:
        return 1
    else:
        return 0


cdef inline int8_t get_quantifier(PatternStateC state) nogil:
    return state.pattern.quantifier


cdef TokenPatternC* init_pattern(Pool mem, attr_t entity_id, object token_specs) except NULL:
    pattern = <TokenPatternC*>mem.alloc(len(token_specs) + 1, sizeof(TokenPatternC))
    cdef int i, index
    for i, (quantifier, spec, extensions, predicates, token_idx) in enumerate(token_specs):
        pattern[i].quantifier = quantifier
        # Ensure attrs refers to a null pointer if nr_attr == 0
        if len(spec) > 0:
            pattern[i].attrs = <AttrValueC*>mem.alloc(len(spec), sizeof(AttrValueC))
        pattern[i].nr_attr = len(spec)
        for j, (attr, value) in enumerate(spec):
            pattern[i].attrs[j].attr = attr
            pattern[i].attrs[j].value = value
        if len(extensions) > 0:
            pattern[i].extra_attrs = <IndexValueC*>mem.alloc(len(extensions), sizeof(IndexValueC))
        for j, (index, value) in enumerate(extensions):
            pattern[i].extra_attrs[j].index = index
            pattern[i].extra_attrs[j].value = value
        pattern[i].nr_extra_attr = len(extensions)
        if len(predicates) > 0:
            pattern[i].py_predicates = <int32_t*>mem.alloc(len(predicates), sizeof(int32_t))
        for j, index in enumerate(predicates):
            pattern[i].py_predicates[j] = index
        pattern[i].nr_py = len(predicates)
        pattern[i].key = hash64(pattern[i].attrs, pattern[i].nr_attr * sizeof(AttrValueC), 0)
        pattern[i].token_idx = token_idx
    i = len(token_specs)
    # Use quantifier to identify final ID pattern node (rather than previous
    # uninitialized quantifier == 0/ZERO + nr_attr == 0 + non-zero-length attrs)
    pattern[i].quantifier = FINAL_ID
    pattern[i].attrs = <AttrValueC*>mem.alloc(1, sizeof(AttrValueC))
    pattern[i].attrs[0].attr = ID
    pattern[i].attrs[0].value = entity_id
    pattern[i].nr_attr = 1
    pattern[i].nr_extra_attr = 0
    pattern[i].nr_py = 0
    pattern[i].token_idx = -1
    return pattern


cdef attr_t get_ent_id(const TokenPatternC* pattern) nogil:
    while pattern.quantifier != FINAL_ID:
        pattern += 1
    id_attr = pattern[0].attrs[0]
    if id_attr.attr != ID:
        with gil:
            raise ValueError(Errors.E074.format(attr=ID, bad_attr=id_attr.attr))
    return id_attr.value


def _preprocess_pattern(token_specs, vocab, extensions_table, extra_predicates, fuzzy_compare):
    """This function interprets the pattern, converting the various bits of
    syntactic sugar before we compile it into a struct with init_pattern.

    We need to split the pattern up into four parts:
    * Normal attribute/value pairs, which are stored on either the token or lexeme,
        can be handled directly.
    * Extension attributes are handled specially, as we need to prefetch the
        values from Python for the doc before we begin matching.
    * Extra predicates also call Python functions, so we have to create the
        functions and store them. So we store these specially as well.
    * Extension attributes that have extra predicates are stored within the
        extra_predicates.
    * Token index that this pattern belongs to.
    """
    tokens = []
    string_store = vocab.strings
    for token_idx, spec in enumerate(token_specs):
        if not spec:
            # Signifier for 'any token'
            tokens.append((ONE, [(NULL_ATTR, 0)], [], [], token_idx))
            continue
        if not isinstance(spec, dict):
            raise ValueError(Errors.E154.format())
        ops = _get_operators(spec)
        attr_values = _get_attr_values(spec, string_store)
        extensions = _get_extensions(spec, string_store, extensions_table)
        predicates = _get_extra_predicates(spec, extra_predicates, vocab, fuzzy_compare)
        for op in ops:
            tokens.append((op, list(attr_values), list(extensions), list(predicates), token_idx))
    return tokens


def _get_attr_values(spec, string_store):
    attr_values = []
    for attr, value in spec.items():
        input_attr = attr
        if isinstance(attr, str):
            attr = attr.upper()
            if attr == '_':
                continue
            elif attr == "OP":
                continue
            if attr == "TEXT":
                attr = "ORTH"
            if attr == "IS_SENT_START":
                attr = "SENT_START"
            attr = IDS.get(attr)
        if isinstance(value, str):
            if attr == ENT_IOB and value in Token.iob_strings():
                value = Token.iob_strings().index(value)
            else:
                value = string_store.add(value)
        elif isinstance(value, bool):
            value = int(value)
        elif isinstance(value, int):
            pass
        elif isinstance(value, dict):
            continue
        else:
            raise ValueError(Errors.E153.format(vtype=type(value).__name__))
        if attr is not None:
            attr_values.append((attr, value))
        else:
            # should be caught in validation
            raise ValueError(Errors.E152.format(attr=input_attr))
    return attr_values


def _predicate_cache_key(attr, predicate, value, *, regex=False, fuzzy=None):
    # tuple order affects performance
    return (attr, regex, fuzzy, predicate, srsly.json_dumps(value, sort_keys=True))


# These predicate helper classes are used to match the REGEX, IN, >= etc
# extensions to the matcher introduced in #3173.

class _FuzzyPredicate:
    operators = ("FUZZY", "FUZZY1", "FUZZY2", "FUZZY3", "FUZZY4", "FUZZY5",
                 "FUZZY6", "FUZZY7", "FUZZY8", "FUZZY9")

    def __init__(self, i, attr, value, predicate, is_extension=False, vocab=None,
                 regex=False, fuzzy=None, fuzzy_compare=None):
        self.i = i
        self.attr = attr
        self.value = value
        self.predicate = predicate
        self.is_extension = is_extension
        if self.predicate not in self.operators:
            raise ValueError(Errors.E126.format(good=self.operators, bad=self.predicate))
        fuzz = self.predicate[len("FUZZY"):] # number after prefix
        self.fuzzy = int(fuzz) if fuzz else -1
        self.fuzzy_compare = fuzzy_compare
        self.key = _predicate_cache_key(self.attr, self.predicate, value, fuzzy=self.fuzzy)

    def __call__(self, Token token):
        if self.is_extension:
            value = token._.get(self.attr)
        else:
            value = token.vocab.strings[get_token_attr_for_matcher(token.c, self.attr)]
        if self.value == value:
            return True
        return self.fuzzy_compare(value, self.value, self.fuzzy)


class _RegexPredicate:
    operators = ("REGEX",)

    def __init__(self, i, attr, value, predicate, is_extension=False, vocab=None,
                 regex=False, fuzzy=None, fuzzy_compare=None):
        self.i = i
        self.attr = attr
        self.value = re.compile(value)
        self.predicate = predicate
        self.is_extension = is_extension
        self.key = _predicate_cache_key(self.attr, self.predicate, value)
        if self.predicate not in self.operators:
            raise ValueError(Errors.E126.format(good=self.operators, bad=self.predicate))

    def __call__(self, Token token):
        if self.is_extension:
            value = token._.get(self.attr)
        else:
            value = token.vocab.strings[get_token_attr_for_matcher(token.c, self.attr)]
        return bool(self.value.search(value))


class _SetPredicate:
    operators = ("IN", "NOT_IN", "IS_SUBSET", "IS_SUPERSET", "INTERSECTS")

    def __init__(self, i, attr, value, predicate, is_extension=False, vocab=None,
                 regex=False, fuzzy=None, fuzzy_compare=None):
        self.i = i
        self.attr = attr
        self.vocab = vocab
        self.regex = regex
        self.fuzzy = fuzzy
        self.fuzzy_compare = fuzzy_compare
        if self.attr == MORPH:
            # normalize morph strings
            self.value = set(self.vocab.morphology.add(v) for v in value)
        else:
            if self.regex:
                self.value = set(re.compile(v) for v in value)
            elif self.fuzzy is not None:
                # add to string store
                self.value = set(self.vocab.strings.add(v) for v in value)
            else:
                self.value = set(get_string_id(v) for v in value)
        self.predicate = predicate
        self.is_extension = is_extension
        self.key = _predicate_cache_key(self.attr, self.predicate, value, regex=self.regex, fuzzy=self.fuzzy)
        if self.predicate not in self.operators:
            raise ValueError(Errors.E126.format(good=self.operators, bad=self.predicate))

    def __call__(self, Token token):
        if self.is_extension:
            value = token._.get(self.attr)
        else:
            value = get_token_attr_for_matcher(token.c, self.attr)

        if self.predicate in ("IN", "NOT_IN"):
            if isinstance(value, (str, int)):
                value = get_string_id(value)
            else:
                return False
        elif self.predicate in ("IS_SUBSET", "IS_SUPERSET", "INTERSECTS"):
            # ensure that all values are enclosed in a set
            if self.attr == MORPH:
                # break up MORPH into individual Feat=Val values
                value = set(get_string_id(v) for v in MorphAnalysis.from_id(self.vocab, value))
            elif isinstance(value, (str, int)):
                value = set((get_string_id(value),))
            elif isinstance(value, Iterable) and all(isinstance(v, (str, int)) for v in value):
                value = set(get_string_id(v) for v in value)
            else:
                return False

        if self.predicate == "IN":
            if self.regex:
                value = self.vocab.strings[value]
                return any(bool(v.search(value)) for v in self.value)
            elif self.fuzzy is not None:
                value = self.vocab.strings[value]
                return any(self.fuzzy_compare(value, self.vocab.strings[v], self.fuzzy)
                           for v in self.value)
            elif value in self.value:
                return True
            else:
                return False
        elif self.predicate == "NOT_IN":
            if self.regex:
                value = self.vocab.strings[value]
                return not any(bool(v.search(value)) for v in self.value)
            elif self.fuzzy is not None:
                value = self.vocab.strings[value]
                return not any(self.fuzzy_compare(value, self.vocab.strings[v], self.fuzzy)
                               for v in self.value)
            elif value in self.value:
                return False
            else:
                return True
        elif self.predicate == "IS_SUBSET":
            return value <= self.value
        elif self.predicate == "IS_SUPERSET":
            return value >= self.value
        elif self.predicate == "INTERSECTS":
            return bool(value & self.value)

    def __repr__(self):
        return repr(("SetPredicate", self.i, self.attr, self.value, self.predicate))


class _ComparisonPredicate:
    operators = ("==", "!=", ">=", "<=", ">", "<")

    def __init__(self, i, attr, value, predicate, is_extension=False, vocab=None,
                 regex=False, fuzzy=None, fuzzy_compare=None):
        self.i = i
        self.attr = attr
        self.value = value
        self.predicate = predicate
        self.is_extension = is_extension
        self.key = _predicate_cache_key(self.attr, self.predicate, value)
        if self.predicate not in self.operators:
            raise ValueError(Errors.E126.format(good=self.operators, bad=self.predicate))

    def __call__(self, Token token):
        if self.is_extension:
            value = token._.get(self.attr)
        else:
            value = get_token_attr_for_matcher(token.c, self.attr)
        if self.predicate == "==":
            return value == self.value
        if self.predicate == "!=":
            return value != self.value
        elif self.predicate == ">=":
            return value >= self.value
        elif self.predicate == "<=":
            return value <= self.value
        elif self.predicate == ">":
            return value > self.value
        elif self.predicate == "<":
            return value < self.value


def _get_extra_predicates(spec, extra_predicates, vocab, fuzzy_compare):
    predicate_types = {
        "REGEX": _RegexPredicate,
        "IN": _SetPredicate,
        "NOT_IN": _SetPredicate,
        "IS_SUBSET": _SetPredicate,
        "IS_SUPERSET": _SetPredicate,
        "INTERSECTS": _SetPredicate,
        "==": _ComparisonPredicate,
        "!=": _ComparisonPredicate,
        ">=": _ComparisonPredicate,
        "<=": _ComparisonPredicate,
        ">": _ComparisonPredicate,
        "<": _ComparisonPredicate,
        "FUZZY": _FuzzyPredicate,
        "FUZZY1": _FuzzyPredicate,
        "FUZZY2": _FuzzyPredicate,
        "FUZZY3": _FuzzyPredicate,
        "FUZZY4": _FuzzyPredicate,
        "FUZZY5": _FuzzyPredicate,
        "FUZZY6": _FuzzyPredicate,
        "FUZZY7": _FuzzyPredicate,
        "FUZZY8": _FuzzyPredicate,
        "FUZZY9": _FuzzyPredicate,
    }
    seen_predicates = {pred.key: pred.i for pred in extra_predicates}
    output = []
    for attr, value in spec.items():
        if isinstance(attr, str):
            if attr == "_":
                output.extend(
                    _get_extension_extra_predicates(
                        value, extra_predicates, predicate_types,
                        seen_predicates))
                continue
            elif attr.upper() == "OP":
                continue
            if attr.upper() == "TEXT":
                attr = "ORTH"
            attr = IDS.get(attr.upper())
        if isinstance(value, dict):
            output.extend(_get_extra_predicates_dict(attr, value, vocab, predicate_types,
                                                     extra_predicates, seen_predicates, fuzzy_compare=fuzzy_compare))
    return output


def _get_extra_predicates_dict(attr, value_dict, vocab, predicate_types,
                               extra_predicates, seen_predicates, regex=False, fuzzy=None, fuzzy_compare=None):
    output = []
    for type_, value in value_dict.items():
        type_ = type_.upper()
        cls = predicate_types.get(type_)
        if cls is None:
            warnings.warn(Warnings.W035.format(pattern=value_dict))
            # ignore unrecognized predicate type
            continue
        elif cls == _RegexPredicate:
            if isinstance(value, dict):
                # add predicates inside regex operator
                output.extend(_get_extra_predicates_dict(attr, value, vocab, predicate_types,
                                                         extra_predicates, seen_predicates,
                                                         regex=True))
                continue
        elif cls == _FuzzyPredicate:
            if isinstance(value, dict):
                # add predicates inside fuzzy operator
                fuzz = type_[len("FUZZY"):] # number after prefix
                fuzzy_val = int(fuzz) if fuzz else -1
                output.extend(_get_extra_predicates_dict(attr, value, vocab, predicate_types,
                                                         extra_predicates, seen_predicates,
                                                         fuzzy=fuzzy_val, fuzzy_compare=fuzzy_compare))
                continue
        predicate = cls(len(extra_predicates), attr, value, type_, vocab=vocab,
                        regex=regex, fuzzy=fuzzy, fuzzy_compare=fuzzy_compare)
        # Don't create redundant predicates.
        # This helps with efficiency, as we're caching the results.
        if predicate.key in seen_predicates:
            output.append(seen_predicates[predicate.key])
        else:
            extra_predicates.append(predicate)
            output.append(predicate.i)
            seen_predicates[predicate.key] = predicate.i
    return output


def _get_extension_extra_predicates(spec, extra_predicates, predicate_types,
        seen_predicates):
    output = []
    for attr, value in spec.items():
        if isinstance(value, dict):
            for type_, cls in predicate_types.items():
                if type_ in value:
                    key = _predicate_cache_key(attr, type_, value[type_])
                    if key in seen_predicates:
                        output.append(seen_predicates[key])
                    else:
                        predicate = cls(len(extra_predicates), attr, value[type_], type_,
                                        is_extension=True)
                        extra_predicates.append(predicate)
                        output.append(predicate.i)
                        seen_predicates[key] = predicate.i
    return output


def _get_operators(spec):
    # Support 'syntactic sugar' operator '+', as combination of ONE, ZERO_PLUS
    lookup = {"*": (ZERO_PLUS,), "+": (ONE, ZERO_PLUS),
              "?": (ZERO_ONE,), "1": (ONE,), "!": (ZERO,)}
    # Fix casing
    spec = {key.upper(): values for key, values in spec.items()
            if isinstance(key, str)}
    if "OP" not in spec:
        return (ONE,)
    elif spec["OP"] in lookup:
        return lookup[spec["OP"]]
    #Min_max {n,m}
    elif spec["OP"].startswith("{") and spec["OP"].endswith("}"):
        # {n}  --> {n,n}  exactly n                 ONE,(n)
        # {n,m}--> {n,m}  min of n, max of m        ONE,(n),ZERO_ONE,(m)
        # {,m} --> {0,m}  min of zero, max of m     ZERO_ONE,(m)
        # {n,} --> {n,∞} min of n, max of inf       ONE,(n),ZERO_PLUS

        min_max = spec["OP"][1:-1]
        min_max = min_max if "," in min_max else f"{min_max},{min_max}"
        n, m = min_max.split(",")

        #1. Either n or m is a blank string and the other is numeric -->isdigit
        #2. Both are numeric and n <= m
        if (not n.isdecimal() and not m.isdecimal()) or (n.isdecimal() and m.isdecimal() and int(n) > int(m)):
            keys = ", ".join(lookup.keys()) + ", {n}, {n,m}, {n,}, {,m} where n and m are integers and n <= m "
            raise ValueError(Errors.E011.format(op=spec["OP"], opts=keys))

        # if n is empty string, zero would be used
        head = tuple(ONE for __ in range(int(n or 0)))
        tail = tuple(ZERO_ONE for __ in range(int(m) - int(n or 0))) if m else (ZERO_PLUS,)
        return head + tail
    else:
        keys = ", ".join(lookup.keys()) + ", {n}, {n,m}, {n,}, {,m} where n and m are integers and n <= m "
        raise ValueError(Errors.E011.format(op=spec["OP"], opts=keys))


def _get_extensions(spec, string_store, name2index):
    attr_values = []
    if not isinstance(spec.get("_", {}), dict):
        raise ValueError(Errors.E154.format())
    for name, value in spec.get("_", {}).items():
        if isinstance(value, dict):
            # Handle predicates (e.g. "IN", in the extra_predicates, not here.
            continue
        if isinstance(value, str):
            value = string_store.add(value)
        if name not in name2index:
            name2index[name] = len(name2index)
        attr_values.append((name2index[name], value))
    return attr_values
