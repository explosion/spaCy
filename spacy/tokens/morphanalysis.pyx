from libc.string cimport memset
cimport numpy as np

from ..errors import Errors
from ..morphology import Morphology
from ..vocab cimport Vocab
from ..typedefs cimport hash_t, attr_t
from ..morphology cimport list_features, check_feature, get_by_field, MorphAnalysisC
from libcpp.memory cimport shared_ptr
from cython.operator cimport dereference as deref


cdef shared_ptr[MorphAnalysisC] EMPTY_MORPH_TAG = shared_ptr[MorphAnalysisC](new MorphAnalysisC())


cdef class MorphAnalysis:
    """Control access to morphological features for a token."""
    def __init__(self, Vocab vocab, features=dict()):
        self.vocab = vocab
        self.key = self.vocab.morphology.add(features)
        self._init_c(self.key)

    cdef void _init_c(self, hash_t key):
        cdef shared_ptr[MorphAnalysisC] analysis = self.vocab.morphology.get_morph_c(key)
        if analysis:
            self.c = analysis
        else:
            self.c = EMPTY_MORPH_TAG

    @classmethod
    def from_id(cls, Vocab vocab, hash_t key):
        """Create a morphological analysis from a given ID."""
        cdef MorphAnalysis morph = MorphAnalysis(vocab)
        morph.vocab = vocab
        morph.key = key
        morph._init_c(key)
        return morph

    def __contains__(self, feature):
        """Test whether the morphological analysis contains some feature."""
        cdef attr_t feat_id = self.vocab.strings.as_int(feature)
        return check_feature(self.c, feat_id)

    def __iter__(self):
        """Iterate over the features in the analysis."""
        cdef attr_t feature
        for feature in list_features(self.c):
            yield self.vocab.strings[feature]

    def __len__(self):
        """The number of features in the analysis."""
        return deref(self.c).features.size()

    def __hash__(self):
        return self.key

    def __eq__(self, other):
        if isinstance(other, str):
            raise ValueError(Errors.E977)
        return self.key == other.key

    def __ne__(self, other):
        return self.key != other.key

    def get(self, field):
        """Retrieve feature values by field."""
        cdef attr_t field_id = self.vocab.strings.as_int(field)
        cdef np.ndarray results = get_by_field(self.c, field_id)
        features = [self.vocab.strings[result] for result in results]
        return [f.split(Morphology.FIELD_SEP)[1] for f in features]

    def to_json(self):
        """Produce a json serializable representation as a UD FEATS-style
        string.
        """
        morph_string = self.vocab.strings[deref(self.c).key]
        if morph_string == self.vocab.morphology.EMPTY_MORPH:
            return ""
        return morph_string

    def to_dict(self):
        """Produce a dict representation.
        """
        return self.vocab.morphology.feats_to_dict(self.to_json())

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.to_json()

