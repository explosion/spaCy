from libc.string cimport memset
cimport numpy as np

from ..errors import Errors
from ..morphology import Morphology
from ..vocab cimport Vocab
from ..typedefs cimport hash_t, attr_t
from ..morphology cimport list_features, check_feature, get_by_field


cdef class MorphAnalysis:
    """Control access to morphological features for a token."""
    def __init__(self, Vocab vocab, features=dict()):
        self.vocab = vocab
        self.key = self.vocab.morphology.add(features)
        analysis = <const MorphAnalysisC*>self.vocab.morphology.tags.get(self.key)
        if analysis is not NULL:
            self.c = analysis[0]
        else:
            memset(&self.c, 0, sizeof(self.c))

    @classmethod
    def from_id(cls, Vocab vocab, hash_t key):
        """Create a morphological analysis from a given ID."""
        cdef MorphAnalysis morph = MorphAnalysis.__new__(MorphAnalysis, vocab)
        morph.vocab = vocab
        morph.key = key
        analysis = <const MorphAnalysisC*>vocab.morphology.tags.get(key)
        if analysis is not NULL:
            morph.c = analysis[0]
        else:
            memset(&morph.c, 0, sizeof(morph.c))
        return morph

    def __contains__(self, feature):
        """Test whether the morphological analysis contains some feature."""
        cdef attr_t feat_id = self.vocab.strings.as_int(feature)
        return check_feature(&self.c, feat_id)

    def __iter__(self):
        """Iterate over the features in the analysis."""
        cdef attr_t feature
        for feature in list_features(&self.c):
            yield self.vocab.strings[feature]

    def __len__(self):
        """The number of features in the analysis."""
        return self.c.length

    def __hash__(self):
        return self.key

    def __eq__(self, other):
        if isinstance(other, str):
            raise ValueError(Errors.E977)
        return self.key == other.key

    def __ne__(self, other):
        return self.key != other.key

    def get(self, field, default=None):
        """Retrieve feature values by field."""
        cdef attr_t field_id = self.vocab.strings.as_int(field)
        cdef np.ndarray results = get_by_field(&self.c, field_id)
        if len(results) == 0:
            if default is None:
                default = []
            return default
        features = [self.vocab.strings[result] for result in results]
        return [f.split(Morphology.FIELD_SEP)[1] for f in features]

    def to_json(self):
        """Produce a json serializable representation as a UD FEATS-style
        string.
        """
        morph_string = self.vocab.strings[self.c.key]
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

