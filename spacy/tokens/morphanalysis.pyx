from libc.string cimport memset

from ..vocab cimport Vocab
from ..typedefs cimport hash_t, attr_t
from ..morphology cimport check_feature, tag_to_json

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
        cdef MorphAnalysis morph = MorphAnalysis.__new__(MorphAnalysis, vocab)
        morph.key = key
        analysis = <const MorphAnalysisC*>vocab.morphology.tags.get(key)
        if analysis is not NULL:
            morph.c = analysis[0]
        else:
            memset(&morph.c, 0, sizeof(morph.c))
        return morph

    def __contains__(self, feature):
        cdef attr_t feat_id = get_string_id(feature)
        return check_feature(&self.c, feat_id)

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def get(self, field):
        raise NotImplementedError

    def to_json(self):
        return tag_to_json(self.c)

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
            pass

    property adp_type_:
        def __get__(self):
            pass

    property adv_type_:
        def __get__(self):
            pass

    property animacy_:
        def __get__(self):
            pass

    property aspect_:
        def __get__(self):
            pass
        
    property case_:
        def __get__(self):
            pass
    
    property conj_type_:
        def __get__(self):
            pass

    property connegative_:
        def __get__(self):
            pass

    property definite_:
        def __get__(self):
            pass

    property degree_:
        def __get__(self):
            pass

    property derivation_:
        def __get__(self):
            pass

    property echo_:
        def __get__(self):
            pass

    property foreign_:
        def __get__(self):
            pass

    property gender_:
        def __get__(self):
            pass

    property hyph_:
        def __get__(self):
            pass

    property inf_form_:
        def __get__(self):
            pass

    property name_type_:
        def __get__(self):
            pass

    property negative_:
        def __get__(self):
            pass

    property mood_:
        def __get__(self):
            pass
    
    property number_:
        def __get__(self):
            pass

    property num_form_:
        def __get__(self):
            pass

    property num_type_:
        def __get__(self):
            pass

    property num_value_:
        def __get__(self):
            pass

    property part_form_:
        def __get__(self):
            pass

    property part_type_:
        def __get__(self):
            pass

    property person_:
        def __get__(self):
            pass
    
    property polite_:
        def __get__(self):
            pass
    
    property polarity_:
        def __get__(self):
            pass

    property poss_:
        def __get__(self):
            pass

    property prefix_:
        def __get__(self):
            pass

    property prep_case_:
        def __get__(self):
            pass

    property pron_type_:
        def __get__(self):
            pass

    property punct_side_:
        def __get__(self):
            pass

    property punct_type_:
        def __get__(self):
            pass

    property reflex_:
        def __get__(self):
            pass

    property style_:
        def __get__(self):
            pass
    
    property style_variant_:
        def __get__(self):
            pass
 
    property tense_:
        def __get__(self):
            pass
 
    property typo_:
        def __get__(self):
            pass
 
    property verb_form_:
        def __get__(self):
            pass
 
    property voice_:
        def __get__(self):
            pass
 
    property verb_type_:
        def __get__(self):
            pass
