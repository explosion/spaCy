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


cdef class Morphology:
    """Store the possible morphological analyses for a language, and index them
    by hash.

    To save space on each token, tokens only know the hash of their
    morphological analysis, so queries of morphological attributes are delegated
    to this class.
    """
    FEATURE_SEP = "|"
    FIELD_SEP = "="
    VALUE_SEP = ","
    # not an empty string so that the PreshMap key is not 0
    EMPTY_MORPH = symbols.NAMES[symbols._]

    def __init__(self, StringStore strings):
        self.mem = Pool()
        self.strings = strings
        self.tags = PreshMap()

    def __reduce__(self):
        tags = set([self.get(self.strings[s]) for s in self.strings])
        tags -= set([""])
        return (unpickle_morphology, (self.strings, sorted(tags)), None, None)

    def add(self, features):
        """Insert a morphological analysis in the morphology table, if not
        already present. The morphological analysis may be provided in the UD
        FEATS format as a string or in the tag map dict format.
        Returns the hash of the new analysis.
        """
        cdef MorphAnalysisC* tag_ptr
        if isinstance(features, str):
            if features == self.EMPTY_MORPH:
                features = ""
            tag_ptr = <MorphAnalysisC*>self.tags.get(<hash_t>self.strings[features])
            if tag_ptr != NULL:
                return tag_ptr.key
            features = self.feats_to_dict(features)
        if not isinstance(features, dict):
            warnings.warn(Warnings.W100.format(feature=features))
            features = {}
        string_features = {self.strings.as_string(field): self.strings.as_string(values) for field, values in features.items()}
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
        norm_feats_string = self.normalize_features(features)
        if norm_feats_string:
            tag.key = self.strings.add(norm_feats_string)
        else:
            tag.key = self.strings.add(self.EMPTY_MORPH)
        self.insert(tag)
        return tag.key

    def normalize_features(self, features):
        """Create a normalized FEATS string from a features string or dict.

        features (Union[dict, str]): Features as dict or UFEATS string.
        RETURNS (str): Features as normalized UFEATS string.
        """
        if isinstance(features, str):
            features = self.feats_to_dict(features)
        if not isinstance(features, dict):
            warnings.warn(Warnings.W100.format(feature=features))
            features = {}
        features = self.normalize_attrs(features)
        string_features = {self.strings.as_string(field): self.strings.as_string(values) for field, values in features.items()}
        # normalized UFEATS string with sorted fields and values
        norm_feats_string = self.FEATURE_SEP.join(sorted([
                self.FIELD_SEP.join([field, values])
            for field, values in string_features.items()
        ]))
        return norm_feats_string or self.EMPTY_MORPH

    def normalize_attrs(self, attrs):
        """Convert attrs dict so that POS is always by ID, other features are
        by string. Values separated by VALUE_SEP are sorted.
        """
        out = {}
        attrs = dict(attrs)
        for key, value in attrs.items():
            # convert POS value to ID
            if key == POS or (isinstance(key, str) and key.upper() == "POS"):
                if isinstance(value, str) and value.upper() in POS_IDS:
                    value = POS_IDS[value.upper()]
                elif isinstance(value, int) and value not in POS_IDS.values():
                    warnings.warn(Warnings.W100.format(feature={key: value}))
                    continue
                out[POS] = value
            # accept any string or ID fields and values and convert to strings
            elif isinstance(key, (int, str)) and isinstance(value, (int, str)):
                key = self.strings.as_string(key)
                value = self.strings.as_string(value)
                # sort values
                if self.VALUE_SEP in value:
                    value = self.VALUE_SEP.join(sorted(value.split(self.VALUE_SEP)))
                out[key] = value
            else:
                warnings.warn(Warnings.W100.format(feature={key: value}))
        return out

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
            return ""
        else:
            return self.strings[tag.key]

    @staticmethod
    def feats_to_dict(feats):
        if not feats or feats == Morphology.EMPTY_MORPH:
            return {}
        return {field: Morphology.VALUE_SEP.join(sorted(values.split(Morphology.VALUE_SEP))) for field, values in
                [feat.split(Morphology.FIELD_SEP) for feat in feats.split(Morphology.FEATURE_SEP)]}

    @staticmethod
    def dict_to_feats(feats_dict):
        if len(feats_dict) == 0:
            return ""
        return Morphology.FEATURE_SEP.join(sorted([Morphology.FIELD_SEP.join([field, Morphology.VALUE_SEP.join(sorted(values.split(Morphology.VALUE_SEP)))]) for field, values in feats_dict.items()]))


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

def unpickle_morphology(strings, tags):
    cdef Morphology morphology = Morphology(strings)
    for tag in tags:
        morphology.add(tag)
    return morphology
