# cython: infer_types
from libc.string cimport memset

import srsly
from collections import Counter
import numpy
import warnings

from .attrs cimport POS, IS_SPACE
from .parts_of_speech cimport SPACE
from .lexeme cimport Lexeme

from .strings import get_string_id
from .attrs import LEMMA, intify_attrs
from .parts_of_speech import IDS as POS_IDS
from .errors import Errors, Warnings
from .util import ensure_path
from . import symbols


def _normalize_props(props):
    """Convert attrs dict so that POS is always by ID, other features are left
    as is as long as they are strings or IDs.
    """
    out = {}
    props = dict(props)
    for key, value in props.items():
        # convert POS value to ID
        if key == POS:
            if hasattr(value, 'upper'):
                value = value.upper()
            if value in POS_IDS:
                value = POS_IDS[value]
            out[key] = value
        elif isinstance(key, str) and key.lower() == 'pos':
            out[POS] = POS_IDS[value.upper()]
        # sort values
        elif isinstance(value, str) and Morphology.VALUE_SEP in value:
            out[key] = Morphology.VALUE_SEP.join(
                    sorted(value.split(Morphology.VALUE_SEP)))
        # accept any string or ID fields and values
        elif isinstance(key, (int, str)) and isinstance(value, (int, str)):
            out[key] = value
        else:
            warnings.warn(Warnings.W029.format(feature={key: value}))
    return out


cdef class Morphology:
    '''Store the possible morphological analyses for a language, and index them
    by hash.

    To save space on each token, tokens only know the hash of their morphological
    analysis, so queries of morphological attributes are delegated
    to this class.
    '''

    FEATURE_SEP = "|"
    FIELD_SEP = "="
    VALUE_SEP = ","
    EMPTY_MORPH = "_"

    def __init__(self, StringStore strings, tag_map, lemmatizer, exc=None):
        self.mem = Pool()
        self.strings = strings
        self.tags = PreshMap()
        # Add special space symbol. We prefix with underscore, to make sure it
        # always sorts to the end.
        space_attrs = tag_map.get('SP', {POS: SPACE})
        if '_SP' not in tag_map:
            self.strings.add('_SP')
            tag_map = dict(tag_map)
            tag_map['_SP'] = space_attrs
        self.tag_names = tuple(sorted(tag_map.keys()))
        self.tag_map = {}
        self.lemmatizer = lemmatizer
        self.n_tags = len(tag_map)
        self.reverse_index = {}
        self._load_from_tag_map(tag_map)

        self._cache = PreshMapArray(self.n_tags)
        self.exc = {}
        if exc is not None:
            for (tag, orth), attrs in exc.items():
                attrs = _normalize_props(attrs)
                self.add_special_case(
                    self.strings.as_string(tag), self.strings.as_string(orth), attrs)

    def _load_from_tag_map(self, tag_map):
        for i, (tag_str, attrs) in enumerate(sorted(tag_map.items())):
            attrs = _normalize_props(attrs)
            self.add(attrs)
            self.tag_map[tag_str] = dict(attrs)
            self.reverse_index[self.strings.add(tag_str)] = i

    def __reduce__(self):
        return (Morphology, (self.strings, self.tag_map, self.lemmatizer,
                self.exc), None, None)

    def add(self, features):
        """Insert a morphological analysis in the morphology table, if not
        already present. The morphological analysis may be provided in the UD
        FEATS format as a string or in the tag map dict format.
        Returns the hash of the new analysis.
        """
        cdef MorphAnalysisC* tag_ptr
        if features == self.EMPTY_MORPH:
            features = ""
        if isinstance(features, str):
            tag_ptr = <MorphAnalysisC*>self.tags.get(<hash_t>self.strings[features])
            if tag_ptr != NULL:
                return tag_ptr.key
            features = self.feats_to_dict(features)
        if not isinstance(features, dict):
            warnings.warn(Warnings.W029.format(feature=features))
            features = {}
        features = _normalize_props(features)
        string_features = {self.strings.as_string(field): self.strings.as_string(values) for field, values in features.items()}
        # normalized UFEATS string with sorted fields and values
        norm_feats_string = self.FEATURE_SEP.join(sorted([
                self.FIELD_SEP.join([field, values])
            for field, values in string_features.items()
        ]))
        # intified ("Field", "Field=Value") pairs
        field_feature_pairs = []
        for field in sorted(string_features):
            values = string_features[field]
            for value in values.split(self.VALUE_SEP):
                field_feature_pairs.append((
                    self.strings.add(field),
                    self.strings.add(field + self.FIELD_SEP + value),
                ))
        cdef MorphAnalysisC tag = self.create_morph_tag(field_feature_pairs)
        # the hash key for the tag is either the hash of the normalized UFEATS
        # string or the hash of an empty placeholder (using the empty string
        # would give a hash key of 0, which is not good for PreshMap)
        if norm_feats_string:
            tag.key = self.strings.add(norm_feats_string)
        else:
            tag.key = self.strings.add(self.EMPTY_MORPH)
        self.insert(tag)
        return tag.key

    cdef MorphAnalysisC create_morph_tag(self, field_feature_pairs) except *:
        """Creates a MorphAnalysisC from a list of intified
        ("Field", "Field=Value") tuples where fields with multiple values have
        been split into individual tuples, e.g.:
        [("Field1", "Field1=Value1"), ("Field1", "Field1=Value2"),
        ("Field2", "Field2=Value3")]
        """
        cdef MorphAnalysisC tag
        tag.length = len(field_feature_pairs)
        tag.fields = <attr_t*>self.mem.alloc(tag.length, sizeof(attr_t))
        tag.features = <attr_t*>self.mem.alloc(tag.length, sizeof(attr_t))
        for i, (field, feature) in enumerate(field_feature_pairs):
            tag.fields[i] = field
            tag.features[i] = feature
        return tag

    cdef int insert(self, MorphAnalysisC tag) except -1:
        cdef hash_t key = tag.key
        if self.tags.get(key) == NULL:
            tag_ptr = <MorphAnalysisC*>self.mem.alloc(1, sizeof(MorphAnalysisC))
            tag_ptr[0] = tag
            self.tags.set(key, <void*>tag_ptr)

    def get(self, hash_t morph):
        tag = <MorphAnalysisC*>self.tags.get(morph)
        if tag == NULL:
            return []
        else:
            return self.strings[tag.key]

    def lemmatize(self, const univ_pos_t univ_pos, attr_t orth, morphology):
        if orth not in self.strings:
            return orth
        cdef unicode py_string = self.strings[orth]
        if self.lemmatizer is None:
            return self.strings.add(py_string.lower())
        cdef list lemma_strings
        cdef unicode lemma_string
        # Normalize features into a dict keyed by the field, to make life easier
        # for the lemmatizer. Handles string-to-int conversion too.
        string_feats = {}
        for key, value in morphology.items():
            if value is True:
                name, value = self.strings.as_string(key).split('_', 1)
                string_feats[name] = value
            else:
                string_feats[self.strings.as_string(key)] = self.strings.as_string(value)
        lemma_strings = self.lemmatizer(py_string, univ_pos, string_feats)
        lemma_string = lemma_strings[0]
        lemma = self.strings.add(lemma_string)
        return lemma

    def add_special_case(self, unicode tag_str, unicode orth_str, attrs,
                         force=False):
        """Add a special-case rule to the morphological analyser. Tokens whose
        tag and orth match the rule will receive the specified properties.

        tag (unicode): The part-of-speech tag to key the exception.
        orth (unicode): The word-form to key the exception.
        """
        attrs = dict(attrs)
        attrs = _normalize_props(attrs)
        self.add(attrs)
        attrs = intify_attrs(attrs, self.strings, _do_deprecated=True)
        self.exc[(tag_str, self.strings.add(orth_str))] = attrs

    cdef int assign_untagged(self, TokenC* token) except -1:
        """Set morphological attributes on a token without a POS tag. Uses
        the lemmatizer's lookup() method, which looks up the string in the
        table provided by the language data as lemma_lookup (if available).
        """
        if token.lemma == 0:
            orth_str = self.strings[token.lex.orth]
            lemma = self.lemmatizer.lookup(orth_str, orth=token.lex.orth)
            token.lemma = self.strings.add(lemma)

    cdef int assign_tag(self, TokenC* token, tag_str) except -1:
        cdef attr_t tag = self.strings.as_int(tag_str)
        if tag in self.reverse_index:
            tag_id = self.reverse_index[tag]
            self.assign_tag_id(token, tag_id)
        else:
            token.tag = tag

    cdef int assign_tag_id(self, TokenC* token, int tag_id) except -1:
        if tag_id > self.n_tags:
            raise ValueError(Errors.E014.format(tag=tag_id))
        # Ensure spaces get tagged as space.
        # It seems pretty arbitrary to put this logic here, but there's really
        # nowhere better. I guess the justification is that this is where the
        # specific word and the tag interact. Still, we should have a better
        # way to enforce this rule, or figure out why the statistical model fails.
        # Related to Issue #220
        if Lexeme.c_check_flag(token.lex, IS_SPACE):
            tag_id = self.reverse_index[self.strings.add('_SP')]
        tag_str = self.tag_names[tag_id]
        features = dict(self.tag_map.get(tag_str, {}))
        if features:
            pos = self.strings.as_int(features.pop(POS))
        else:
            pos = 0
        cdef attr_t lemma = <attr_t>self._cache.get(tag_id, token.lex.orth)
        if lemma == 0:
            # Ugh, self.lemmatize has opposite arg order from self.lemmatizer :(
            lemma = self.lemmatize(pos, token.lex.orth, features)
            self._cache.set(tag_id, token.lex.orth, <void*>lemma)
        token.lemma = lemma
        token.pos = <univ_pos_t>pos
        token.tag = self.strings[tag_str]
        token.morph = self.add(features)
        if (self.tag_names[tag_id], token.lex.orth) in self.exc:
            self._assign_tag_from_exceptions(token, tag_id)

    cdef int _assign_tag_from_exceptions(self, TokenC* token, int tag_id) except -1:
        key = (self.tag_names[tag_id], token.lex.orth)
        cdef dict attrs
        attrs = self.exc[key]
        token.pos = attrs.get(POS, token.pos)
        token.lemma = attrs.get(LEMMA, token.lemma)

    def load_morph_exceptions(self, dict exc):
        # Map (form, pos) to attributes
        for tag_str, entries in exc.items():
            for form_str, attrs in entries.items():
                self.add_special_case(tag_str, form_str, attrs)

    @staticmethod
    def feats_to_dict(feats):
        if not feats:
            return {}
        return {field: Morphology.VALUE_SEP.join(sorted(values.split(Morphology.VALUE_SEP))) for field, values in
                [feat.split(Morphology.FIELD_SEP) for feat in feats.split(Morphology.FEATURE_SEP)]}

    @staticmethod
    def dict_to_feats(feats_dict):
        if len(feats_dict) == 0:
            return ""
        return Morphology.FEATURE_SEP.join(sorted([Morphology.FIELD_SEP.join([field, Morphology.VALUE_SEP.join(sorted(values.split(Morphology.VALUE_SEP)))]) for field, values in feats_dict.items()]))

    @staticmethod
    def list_to_feats(feats_list):
        if len(feats_list) == 0:
            return ""
        feats_dict = {}
        for feat in feats_list:
            field, value = feat.split(Morphology.FIELD_SEP)
            if field not in feats_dict:
                feats_dict[field] = set()
            feats_dict[field].add(value)
        feats_dict = {field: Morphology.VALUE_SEP.join(sorted(values)) for field, values in feats_dict.items()}
        return Morphology.dict_to_feats(feats_dict)


cdef int check_feature(const MorphAnalysisC* morph, attr_t feature) nogil:
    cdef int i
    for i in range(morph.length):
        if morph.features[i] == feature:
            return True
    return False


cdef list list_features(const MorphAnalysisC* morph):
    cdef int i
    features = []
    for i in range(morph.length):
        features.append(morph.features[i])
    return features


cdef np.ndarray get_by_field(const MorphAnalysisC* morph, attr_t field):
    cdef np.ndarray results = numpy.zeros((morph.length,), dtype="uint64")
    n = get_n_by_field(<uint64_t*>results.data, morph, field)
    return results[:n]


cdef int get_n_by_field(attr_t* results, const MorphAnalysisC* morph, attr_t field) nogil:
    cdef int n_results = 0
    cdef int i
    for i in range(morph.length):
        if morph.fields[i] == field:
            results[n_results] = morph.features[i]
            n_results += 1
    return n_results
