from ..vocab cimport Vocab
from ..typedefs cimport hash_t


cdef class MorphAnalysis:
    """Control access to morphological features for a token."""
    def __init__(self, Vocab vocab, features=tuple()):
        self.vocab = vocab
        self.key = self.vocab.morphology.add(features)
        analysis = <const MorphAnalysisC*>self.vocab.morphology.tags.get(self.key)
        self.c = analysis[0]

    @classmethod
    def from_id(self, Vocab vocab, hash_t key):
        pass

    def __contains__(self, feature):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __hash__(self):
        pass

    def get(self, name):
        pass

    def to_json(self):
        pass

    @property
    def is_base_form(self):
        pass

    @property
    def pos(self):
        pass

    @property
    def pos_(self):
        pass

    @property
    def id(self):
        pass

    property abbr:
        def __get__(self):
            pass

    property adp_type:
        def __get__(self):
            pass

    property adv_type:
        def __get__(self):
            pass

    property animacy:
        def __get__(self):
            pass

    property aspect:
        def __get__(self):
            pass
        
    property case:
        def __get__(self):
            pass
    
    property conj_type:
        def __get__(self):
            pass

    property connegative:
        def __get__(self):
            pass

    property definite:
        def __get__(self):
            pass

    property degree:
        def __get__(self):
            pass

    property derivation:
        def __get__(self):
            pass

    property echo:
        def __get__(self):
            pass

    property foreign:
        def __get__(self):
            pass

    property gender:
        def __get__(self):
            pass

    property hyph:
        def __get__(self):
            pass

    property inf_form:
        def __get__(self):
            pass

    property mood:
        def __get__(self):
            pass
    
    property name_type:
        def __get__(self):
            pass

    property negative:
        def __get__(self):
            pass

    property noun_type:
        def __get__(self):
            pass

    property number:
        def __get__(self):
            pass

    property num_form:
        def __get__(self):
            pass

    property num_type:
        def __get__(self):
            pass

    property num_value:
        def __get__(self):
            pass

    property part_form:
        def __get__(self):
            pass

    property part_type:
        def __get__(self):
            pass

    property person:
        def __get__(self):
            pass
    
    property polite:
        def __get__(self):
            pass
    
    property polarity:
        def __get__(self):
            pass

    property poss:
        def __get__(self):
            pass

    property prefix:
        def __get__(self):
            pass

    property prep_case:
        def __get__(self):
            pass

    property pron_type:
        def __get__(self):
            pass

    property punct_side:
        def __get__(self):
            pass

    property punct_type:
        def __get__(self):
            pass

    property reflex:
        def __get__(self):
            pass

    property style:
        def __get__(self):
            pass
    
    property style_variant:
        def __get__(self):
            pass
 
    property tense:
        def __get__(self):
            pass
 
    property typo:
        def __get__(self):
            pass
 
    property verb_form:
        def __get__(self):
            pass
 
    property voice:
        def __get__(self):
            pass
 
    property verb_type:
        def __get__(self):
            pass

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
