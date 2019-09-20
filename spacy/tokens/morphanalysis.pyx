from libc.string cimport memset

from ..vocab cimport Vocab
from ..typedefs cimport hash_t, attr_t
from ..morphology cimport list_features, check_feature, get_field, tag_to_json

from ..strings import get_string_id


cdef class MorphAnalysis:
    """Control access to morphological features for a token."""
    def __init__(self, Vocab vocab, features=tuple()):
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
        cdef attr_t feat_id = get_string_id(feature)
        return check_feature(&self.c, feat_id)

    def __iter__(self):
        """Iterate over the features in the analysis."""
        cdef attr_t feature
        for feature in list_features(&self.c):
            yield self.vocab.strings[feature]

    def __len__(self):
        """The number of features in the analysis."""
        return self.c.length

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.to_json()

    def __hash__(self):
        return self.key

    def get(self, unicode field):
        """Retrieve a feature by field."""
        cdef int field_id = self.vocab.morphology._feat_map.attr2field[field]
        return self.vocab.strings[get_field(&self.c, field_id)]

    def to_json(self):
        """Produce a json serializable representation, which will be a list of
        strings.
        """
        return tag_to_json(&self.c)

    @property
    def is_base_form(self):
        raise NotImplementedError

    @property
    def pos(self):
        return self.c.pos

    @property
    def pos_(self):
        return self.vocab.strings[self.c.pos]

    property id:
        def __get__(self):
            return self.key

    property abbr:
        def __get__(self):
            return self.c.abbr

    property adp_type:
        def __get__(self):
            return self.c.adp_type

    property adv_type:
        def __get__(self):
            return self.c.adv_type

    property animacy:
        def __get__(self):
            return self.c.animacy

    property aspect:
        def __get__(self):
            return self.c.aspect
        
    property case:
        def __get__(self):
            return self.c.case
    
    property conj_type:
        def __get__(self):
            return self.c.conj_type

    property connegative:
        def __get__(self):
            return self.c.connegative

    property definite:
        def __get__(self):
            return self.c.definite

    property degree:
        def __get__(self):
            return self.c.degree

    property derivation:
        def __get__(self):
            return self.c.derivation

    property echo:
        def __get__(self):
            return self.c.echo

    property foreign:
        def __get__(self):
            return self.c.foreign

    property gender:
        def __get__(self):
            return self.c.gender

    property hyph:
        def __get__(self):
            return self.c.hyph

    property inf_form:
        def __get__(self):
            return self.c.inf_form

    property mood:
        def __get__(self):
            return self.c.mood
    
    property name_type:
        def __get__(self):
            return self.c.name_type

    property negative:
        def __get__(self):
            return self.c.negative

    property noun_type:
        def __get__(self):
            return self.c.noun_type

    property number:
        def __get__(self):
            return self.c.number

    property num_form:
        def __get__(self):
            return self.c.num_form

    property num_type:
        def __get__(self):
            return self.c.num_type

    property num_value:
        def __get__(self):
            return self.c.num_value

    property part_form:
        def __get__(self):
            return self.c.part_form

    property part_type:
        def __get__(self):
            return self.c.part_type

    property person:
        def __get__(self):
            return self.c.person
    
    property polite:
        def __get__(self):
            return self.c.polite
    
    property polarity:
        def __get__(self):
            return self.c.polarity

    property poss:
        def __get__(self):
            return self.c.poss

    property prefix:
        def __get__(self):
            return self.c.prefix

    property prep_case:
        def __get__(self):
            return self.c.prep_case

    property pron_type:
        def __get__(self):
            return self.c.pron_type

    property punct_side:
        def __get__(self):
            return self.c.punct_side

    property punct_type:
        def __get__(self):
            return self.c.punct_type

    property reflex:
        def __get__(self):
            return self.c.reflex

    property style:
        def __get__(self):
            return self.c.style
    
    property style_variant:
        def __get__(self):
            return self.c.style_variant
 
    property tense:
        def __get__(self):
            return self.c.tense
 
    property typo:
        def __get__(self):
            return self.c.typo
 
    property verb_form:
        def __get__(self):
            return self.c.verb_form
 
    property voice:
        def __get__(self):
            return self.c.voice
 
    property verb_type:
        def __get__(self):
            return self.c.verb_type

    property abbr_:
        def __get__(self):
            return self.vocab.strings[self.c.abbr]

    property adp_type_:
        def __get__(self):
            return self.vocab.strings[self.c.adp_type]

    property adv_type_:
        def __get__(self):
            return self.vocab.strings[self.c.adv_type]

    property animacy_:
        def __get__(self):
            return self.vocab.strings[self.c.animacy]

    property aspect_:
        def __get__(self):
            return self.vocab.strings[self.c.aspect]
        
    property case_:
        def __get__(self):
            return self.vocab.strings[self.c.case]
    
    property conj_type_:
        def __get__(self):
            return self.vocab.strings[self.c.conj_type]

    property connegative_:
        def __get__(self):
            return self.vocab.strings[self.c.connegative]

    property definite_:
        def __get__(self):
            return self.vocab.strings[self.c.definite]

    property degree_:
        def __get__(self):
            return self.vocab.strings[self.c.degree]

    property derivation_:
        def __get__(self):
            return self.vocab.strings[self.c.derivation]

    property echo_:
        def __get__(self):
            return self.vocab.strings[self.c.echo]

    property foreign_:
        def __get__(self):
            return self.vocab.strings[self.c.foreign]

    property gender_:
        def __get__(self):
            return self.vocab.strings[self.c.gender]

    property hyph_:
        def __get__(self):
            return self.vocab.strings[self.c.hyph]

    property inf_form_:
        def __get__(self):
            return self.vocab.strings[self.c.inf_form]

    property name_type_:
        def __get__(self):
            return self.vocab.strings[self.c.name_type]

    property negative_:
        def __get__(self):
            return self.vocab.strings[self.c.negative]

    property mood_:
        def __get__(self):
            return self.vocab.strings[self.c.mood]
    
    property number_:
        def __get__(self):
            return self.vocab.strings[self.c.number]

    property num_form_:
        def __get__(self):
            return self.vocab.strings[self.c.num_form]

    property num_type_:
        def __get__(self):
            return self.vocab.strings[self.c.num_type]

    property num_value_:
        def __get__(self):
            return self.vocab.strings[self.c.num_value]

    property part_form_:
        def __get__(self):
            return self.vocab.strings[self.c.part_form]

    property part_type_:
        def __get__(self):
            return self.vocab.strings[self.c.part_type]

    property person_:
        def __get__(self):
            return self.vocab.strings[self.c.person]
    
    property polite_:
        def __get__(self):
            return self.vocab.strings[self.c.polite]
    
    property polarity_:
        def __get__(self):
            return self.vocab.strings[self.c.polarity]

    property poss_:
        def __get__(self):
            return self.vocab.strings[self.c.poss]

    property prefix_:
        def __get__(self):
            return self.vocab.strings[self.c.prefix]

    property prep_case_:
        def __get__(self):
            return self.vocab.strings[self.c.prep_case]

    property pron_type_:
        def __get__(self):
            return self.vocab.strings[self.c.pron_type]

    property punct_side_:
        def __get__(self):
            return self.vocab.strings[self.c.punct_side]

    property punct_type_:
        def __get__(self):
            return self.vocab.strings[self.c.punct_type]

    property reflex_:
        def __get__(self):
            return self.vocab.strings[self.c.reflex]

    property style_:
        def __get__(self):
            return self.vocab.strings[self.c.style]
    
    property style_variant_:
        def __get__(self):
            return self.vocab.strings[self.c.style_variant]
 
    property tense_:
        def __get__(self):
            return self.vocab.strings[self.c.tense]
 
    property typo_:
        def __get__(self):
            return self.vocab.strings[self.c.typo]
 
    property verb_form_:
        def __get__(self):
            return self.vocab.strings[self.c.verb_form]
 
    property voice_:
        def __get__(self):
            return self.vocab.strings[self.c.voice]
 
    property verb_type_:
        def __get__(self):
            return self.vocab.strings[self.c.verb_type]
