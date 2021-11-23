from ..matcher import Matcher
from ..language import Language
from typing import Optional, Union, List, Dict, Tuple, Iterable, Any, Callable, Sequence
from ..tokens import Span

from collections import defaultdict

DEFAULT_MATCH_ID_SEPARATOR = "||"
PatternType = Dict[str, Union[str, List[Dict[str, Any]]]]
PatternDictType = Dict[str, Dict[str, Dict[str, List[List[Dict[str, Any]]]]]]


class SpanGroupRuler :
    """
    This class populates Doc.spans based on spacy matcher rules, similarly to EntityRuler.
    Pattenrs are accepted in a list form (similar to EntityRuler), or more convenient
    dictionary form:
    { 'GROUP_NAME' : {
            'LABEL_NAME' : {
                'KB_ID' : [rule_1, rule_2, rule_N],
            },
        },
    }
    The class provides flexibility controlling span overlaps. By default, it allows overlapping spans
    between groups. Within each groups, all matched spans are treated similar to entities
    in entity ruler, i.e. overlapping matches are filtered using 'LONGEST' policy.
    It can be configured by specifying overlap_filter_level parameter.

    ruler() method returns a dictionary of span lists
    __call__() method assigns matched spans to doc.spans
    """
    def __init__(
            self,
            nlp : Language,
            name : str = 'span_group_ruler',
            *,
            validate : bool = True,
            match_id_separator : str = DEFAULT_MATCH_ID_SEPARATOR,
            reset_groups : bool = True,
            overlap_filter_level : str = 'group', # can be 'group', 'label', 'kb_id', 'all' or None # group means overlaps between the groups are allowed. label = between (group, label), kb_id = between (group, label, kb_id)
            patterns : Optional[List[PatternType]] = None,
            pattern_dict : Optional[PatternDictType] = None,
    ):
        self.nlp = nlp
        self.name = name
        self.validate = validate
        self.match_id_separator = match_id_separator
        self.reset_groups = reset_groups
        self.overlap_filter_level = overlap_filter_level # TODO: validate
        self.matcher = Matcher(self.nlp.vocab, validate = self.validate)
        self.key2id = {}
        self.id2key = {}
        self._patterns = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # group : {label : {kb_id: [patterns]}}
        assert not (patterns and pattern_dict), "Only one of (pattern, pattern_dict) can be specified "
        if patterns :
            self.add_pattern_list(patterns)
        elif pattern_dict :
            self.add_pattern_dict(pattern_dict)

    def add_pattern_list(self, patterns):
        pattern_dict = defaultdict(lambda : defaultdict(lambda : defaultdict(list)))
        for entry in patterns:
            group = entry.get('group', '')
            label = entry.get('label', '')
            kb_id = entry.get('kb_id', entry.get('id', '')) # To make it compatible with EntityRuler
            pattern = entry['pattern']
            pattern_dict = patterns[group][label][kb_id].appennd(pattern)
        self.add_pattern_dict(pattern_dict)
        pass

    def add_pattern_dict(self, pattern_dict):
        patterns_by_match_id = defaultdict(list)
        for group, label_dict in pattern_dict.items() :
            for label, kb_id_dict in label_dict.items() :
                for kb_id, patterns in kb_id_dict.items() :
                    match_id = self._create_match_id(group, label, kb_id)
                    patterns_by_match_id[match_id].extend(patterns)
        for match_id, patterns in patterns_by_match_id.items() :
            self.matcher.add(match_id, patterns)

    def _create_match_id(self, group_name, label, kb_id):
        key = (group_name, label, kb_id)
        match_id = self.match_id_separator.join(key)
        self.nlp.vocab[match_id] # Make sure it is in vocab
        match_id_int = self.nlp.vocab.strings[match_id]
        if match_id_int not in self.id2key :
            self.id2key[match_id_int] = key
            self.key2id[key] = match_id_int
        return match_id_int

    def rule(self, doc):
        """
        Runs the rules and returns a dictionary of span lists, a span list per group
        :param doc:
        :return:
        """
        matches = self.matcher(doc)
        result = []

        # TDOO: make it a class member instead
        match_id_to_key_setup = {
            'all' : lambda match_id : '',
            'kb_id' : lambda match_id : self.id2key[match_id], # (group, label, kb_id)
            'label' : lambda match_id: (self.id2key[match_id][0:2]), # (group, label)
            'group' : lambda match_id: (self.id2key[match_id][0]),
        }

        if self.overlap_filter_level :
            match_id_to_key = match_id_to_key_setup.get(self.overlap_filter_level, lambda match_id : self.key2id[match_id])
            matches_by_key = defaultdict(list)
            for match in matches:
                matches_by_key[match_id_to_key(match[0])].append(match)
            for group in matches_by_key.values():
                result.extend(filter_overlapping_matches(group))
        else :
            result = filter_fully_overlapped_matches(matches) # Should be an option not to do it?

        result_dict = defaultdict(list)

        for match in result :
            group, label, kb_id = self.id2key[match[0]]
            result_dict[group].append(Span(doc, match[1], match[2], label, kb_id = kb_id))

        return result_dict

    def __call__(self, doc):
        result_dict = self.rule(doc)
        for group, spans in result_dict.items():
            if not group in doc.spans or self.reset_groups:
                doc.spans[group] = spans
            else :
                doc.spans[group].extend(spans)
        return doc

# If we could have Matcher class do this on arbitrary groupings, it would be great
def filter_overlapping_matches(matches):
    get_sort_key = lambda match: (match[2] - match[1], -match[1])
    matches = sorted(matches, key=get_sort_key, reverse=True)
    new_matches = []
    seen_tokens = set()
    for match_id, start, end in matches:
        if start not in seen_tokens and end - 1 not in seen_tokens:
            seen_tokens.update(range(start, end))
            new_matches.append((match_id, start, end))
    new_matches = sorted(new_matches, key=lambda match: (match[1], match[2] - match[1]))
    return new_matches

# Filters out matches with the same match_id that are fully contained in other matches
def filter_fully_overlapped_matches(matches) :
    result = []
    if matches :
        sort_key = lambda match: (match[0], match[1], -match[2])
        matches = sorted(matches, key=sort_key)
        ii = 0
        while ii < len(matches):
            match = matches[ii]
            match_id = match[0]
            result.append(match)
            jj = ii + 1
            while jj < len(matches) and matches[jj][0] == match_id and matches[jj][2] <= match[2]:
                ii = jj - 1  # Account for an increment of ii in the outer loop
                jj += 1
            ii += 1
    return result

# This is here temporarily, so that the demo snippet can run
def get_overlapping_spans(current_span, spans, exclude_self = True) :
    spans = sorted(spans, key=lambda x: (x.start, x.end))
    result = []
    start = current_span.start
    end = current_span.end
    for span in spans :
        if span.end <= start :
            continue
        if span.start >= end :
            break
        if not exclude_self or current_span != span :
            result.append(span)
    result = list(set(result))
    return result
