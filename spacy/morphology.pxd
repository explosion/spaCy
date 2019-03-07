from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap, PreshMapArray
from libc.stdint cimport uint64_t
from murmurhash cimport mrmr

from .structs cimport TokenC, MorphAnalysisC
from .strings cimport StringStore
from .typedefs cimport hash_t, attr_t, flags_t
from .parts_of_speech cimport univ_pos_t

from . cimport symbols

cdef class Morphology:
    cdef readonly Pool mem
    cdef readonly StringStore strings
    cdef PreshMap tags # Keyed by hash, value is pointer to tag
 
    cdef public object lemmatizer
    cdef readonly object tag_map
    cdef readonly object tag_names
    cdef readonly object reverse_index
    cdef readonly object exc
    cdef readonly PreshMapArray _cache
    cdef readonly int n_tags

    cpdef update(self, hash_t morph, features)
    cdef hash_t insert(self, MorphAnalysisC tag) except 0
    
    cdef int assign_untagged(self, TokenC* token) except -1
    cdef int assign_tag(self, TokenC* token, tag) except -1
    cdef int assign_tag_id(self, TokenC* token, int tag_id) except -1

    cdef int _assign_tag_from_exceptions(self, TokenC* token, int tag_id) except -1


cdef enum univ_morph_t:
    NIL = 0

    begin_Abbr
    Abbr_yes
    end_Abbr

    begin_AdpType
    AdpType_circ 
    AdpType_comprep 
    AdpType_prep 
    AdpType_post 
    AdpType_voc 
    end_AdpType

    begin_AdvType
    AdvType_adadj
    AdvType_cau
    AdvType_deg
    AdvType_ex
    AdvType_loc
    AdvType_man
    AdvType_mod
    AdvType_sta
    AdvType_tim
    end_AdvType

    begin_Animacy
    Animacy_anim
    Animacy_hum
    Animacy_inan
    Animacy_nhum
    end_Animacy

    begin_Aspect
    Aspect_freq
    Aspect_imp
    Aspect_mod
    Aspect_none
    Aspect_perf
    end_Aspect

    begin_Case
    Case_abe
    Case_abl
    Case_abs
    Case_acc
    Case_ade
    Case_all
    Case_cau
    Case_com
    Case_dat
    Case_del
    Case_dis
    Case_ela
    Case_ess
    Case_gen
    Case_ill
    Case_ine
    Case_ins
    Case_loc
    Case_lat
    Case_nom
    Case_par
    Case_sub
    Case_sup
    Case_tem
    Case_ter
    Case_tra
    Case_voc
    end_Case

    begin_ConjType
    ConjType_comp # cz, U
    ConjType_oper # cz, U
    end_ConjType
    begin_Connegative
    Connegative_yes # fi
    end_Connegative

    begin_Definite
    Definite_cons # U20
    Definite_def
    Definite_ind
    Definite_red
    Definite_two
    end_Definite

    begin_Degree
    Degree_abs
    Degree_cmp
    Degree_comp
    Degree_none
    Degree_pos
    Degree_sup
    Degree_com
    Degree_dim # du
    end_Degree

    begin_Derivation
    Derivation_minen # fi
    Derivation_sti # fi
    Derivation_inen # fi
    Derivation_lainen # fi
    Derivation_ja # fi
    Derivation_ton # fi
    Derivation_vs # fi
    Derivation_ttain # fi
    Derivation_ttaa # fi
    end_Derivation

    begin_Echo
    Echo_rdp # U
    Echo_ech # U
    end_Echo

    begin_Foreign
    Foreign_foreign # cz, fi, U
    Foreign_fscript # cz, fi, U
    Foreign_tscript # cz, U
    Foreign_yes # sl
    end_Foreign

    begin_Gender
    Gender_com
    Gender_fem
    Gender_masc
    Gender_neut
    Gender_dat_masc # bq, U
    Gender_dat_fem # bq, U
    Gender_erg_masc # bq
    Gender_erg_fem # bq
    Gender_psor_masc # cz, sl, U
    Gender_psor_fem # cz, sl, U
    Gender_psor_neut # sl
    end_Gender

    begin_Hyph
    Hyph_yes # cz, U
    end_Hyph

    begin_InfForm
    InfForm_one # fi
    InfForm_two # fi
    InfForm_three # fi
    end_InfForm

    begin_Mood
    Mood_cnd
    Mood_imp
    Mood_ind
    Mood_n
    Mood_pot
    Mood_sub
    Mood_opt
    end_Mood

    begin_NameType
    NameType_geo # U, cz
    NameType_prs # U, cz
    NameType_giv # U, cz
    NameType_sur # U, cz
    NameType_nat # U, cz
    NameType_com # U, cz
    NameType_pro # U, cz
    NameType_oth # U, cz
    end_NameType

    begin_Negative
    Negative_neg
    Negative_pos
    Negative_yes
    end_Negative

    begin_NounType
    NounType_com # U
    NounType_prop # U
    NounType_class # U
    end_NounType

    begin_Number
    Number_com
    Number_dual
    Number_none
    Number_plur
    Number_sing
    Number_ptan # bg
    Number_count # bg
    Number_abs_sing # bq, U
    Number_abs_plur # bq, U
    Number_dat_sing # bq, U
    Number_dat_plur # bq, U
    Number_erg_sing # bq, U
    Number_erg_plur # bq, U
    Number_psee_sing # U
    Number_psee_plur # U
    Number_psor_sing # cz, fi, sl, U
    Number_psor_plur # cz, fi, sl, U
    end_Number
    
    begin_NumForm
    NumForm_digit # cz, sl, U
    NumForm_roman # cz, sl, U
    NumForm_word # cz, sl, U
    end_NumForm

    begin_NumType
    NumType_card
    NumType_dist
    NumType_frac
    NumType_gen
    NumType_mult
    NumType_none
    NumType_ord
    NumType_sets
    end_NumType
    
    begin_NumValue
    NumValue_one # cz, U
    NumValue_two # cz, U
    NumValue_three # cz, U
    end_NumValue

    begin_PartForm
    PartForm_pres # fi
    PartForm_past # fi
    PartForm_agt # fi
    PartForm_neg # fi
    end_PartForm

    begin_PartType
    PartType_mod # U
    PartType_emp # U
    PartType_res # U
    PartType_inf # U
    PartType_vbp # U
    end_PartType

    begin_Person 
    Person_one
    Person_two
    Person_three
    Person_none
    Person_abs_one # bq, U
    Person_abs_two # bq, U
    Person_abs_three # bq, U
    Person_dat_one # bq, U
    Person_dat_two # bq, U
    Person_dat_three # bq, U
    Person_erg_one # bq, U
    Person_erg_two # bq, U
    Person_erg_three # bq, U
    Person_psor_one # fi, U
    Person_psor_two # fi, U
    Person_psor_three # fi, U
    end_Person

    begin_Polarity
    Polarity_neg # U20
    Polarity_pos # U20
    end_Polarity
    
    begin_Polite
    Polite_inf # bq, U
    Polite_pol # bq, U
    Polite_abs_inf # bq, U
    Polite_abs_pol # bq, U
    Polite_erg_inf # bq, U
    Polite_erg_pol # bq, U
    Polite_dat_inf # bq, U
    Polite_dat_pol # bq, U
    end_Polite

    begin_Poss
    Poss_yes
    end_Poss
    
    begin_Prefix
    Prefix_yes # U
    end_Prefix
    
    begin_PrepCase
    PrepCase_npr # cz
    PrepCase_pre # U
    end_PrepCase

    begin_PronType
    PronType_advPart
    PronType_art
    PronType_default
    PronType_dem
    PronType_ind
    PronType_int
    PronType_neg
    PronType_prs
    PronType_rcp
    PronType_rel
    PronType_tot
    PronType_clit
    PronType_exc # es, ca, it, fa
    end_PronType

    begin_PunctSide
    PunctSide_ini # U
    PunctSide_fin # U
    end_PunctSide

    begin_PunctType
    PunctType_peri # U
    PunctType_qest # U
    PunctType_excl # U
    PunctType_quot # U
    PunctType_brck # U
    PunctType_comm # U
    PunctType_colo # U
    PunctType_semi # U
    PunctType_dash # U
    end_PunctType

    begin_Reflex
    Reflex_yes
    end_Reflex

    begin_Style
    Style_arch # cz, fi, U
    Style_rare # cz, fi, U
    Style_poet # cz, U
    Style_norm # cz, U
    Style_coll # cz, U
    Style_vrnc # cz, U
    Style_sing # cz, U
    Style_expr # cz, U
    Style_derg # cz, U
    Style_vulg # cz, U
    Style_yes # fi, U
    end_Style

    begin_StyleVariant
    StyleVariant_styleShort # cz
    StyleVariant_styleBound # cz, sl
    end_StyleVariant
    
    begin_Tense
    Tense_fut
    Tense_imp
    Tense_past
    Tense_pres
    end_Tense

    begin_Typo
    Typo_yes
    end_Typo
    
    begin_VerbForm
    VerbForm_fin
    VerbForm_ger
    VerbForm_inf
    VerbForm_none
    VerbForm_part
    VerbForm_partFut
    VerbForm_partPast
    VerbForm_partPres
    VerbForm_sup
    VerbForm_trans
    VerbForm_conv # U20
    VerbForm_gdv # la
    end_VerbForm

    begin_VerbType
    VerbType_aux # U
    VerbType_cop # U
    VerbType_mod # U
    VerbType_light # U
    end_VerbType

    begin_Voice
    Voice_act
    Voice_cau
    Voice_pass
    Voice_mid # gkc
    Voice_int # hb
    end_Voice

