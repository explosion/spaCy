from .structs cimport TokenC
from .strings cimport StringStore


cdef class Morphology:
    cdef readonly object strings
    cdef public object lemmatizer
    cdef public object tag_map
    cdef public object tag_names
    cdef public object tag_ids
    cdef public int n_tags

    cdef int assign_tag(self, StringStore strings, TokenC* token, int tag) except -1

    cdef int assign_from_dict(self, TokenC* token, props) except -1

#
#cpdef enum Feature_t:
#    Abbr
#    AdpType
#    AdvType
#    ConjType
#    Connegative
#    Derivation
#    Echo
#    Foreign
#    Gender_dat
#    Gender_erg
#    Gender_psor
#    Hyph
#    InfForm
#    NameType
#    NounType
#    NumberAbs
#    NumberDat
#    NumberErg
#    NumberPsee
#    NumberPsor
#    NumForm
#    NumValue
#    PartForm
#    PartType
#    Person_abs
#    Person_dat
#    Person_psor
#    Polite
#    Polite_abs
#    Polite_dat
#    Prefix
#    PrepCase
#    PunctSide
#    PunctType
#    Style
#    Typo
#    Variant
#    VerbType
#
#
#cpdef enum Animacy:
#    Anim
#    Inam
#
#
#cpdef enum Aspect:
#    Freq
#    Imp
#    Mod
#    None_
#    Perf
#
#
#cpdef enum Case1:
#    Nom
#    Gen
#    Acc
#    Dat
#    Voc
#    Abl
#    
#cdef enum Case2:
#    Abe
#    Abs
#    Ade
#    All
#    Cau
#    Com
#    Del
#    Dis
#
#cdef enum Case3:
#    Ela
#    Ess
#    Ill
#    Ine
#    Ins
#    Loc
#    Lat
#    Par
#
#cdef enum Case4:
#    Sub
#    Sup
#    Tem
#    Ter
#    Tra
#
#
#cpdef enum Definite:
#    Two
#    Def
#    Red
#    Ind
#
#
#cpdef enum Degree:
#    Cmp
#    Comp
#    None_
#    Pos
#    Sup
#    Abs
#    Com
#    Degree # du
#
#
#cpdef enum Gender:
#    Com
#    Fem
#    Masc
#    Neut
#
#
#cpdef enum Mood:
#    Cnd
#    Imp
#    Ind
#    N
#    Pot
#    Sub
#    Opt
#
#
#cpdef enum Negative:
#    Neg
#    Pos
#    Yes
#
#
#cpdef enum Number:
#    Com
#    Dual
#    None_
#    Plur
#    Sing
#    Ptan # bg
#    Count # bg
#
#
#cpdef enum NumType:
#    Card
#    Dist
#    Frac
#    Gen
#    Mult
#    None_
#    Ord
#    Sets
#
#
#cpdef enum Person:
#    One
#    Two
#    Three
#    None_
#
#
#cpdef enum Poss:
#    Yes
#
#
#cpdef enum PronType1:
#    AdvPart
#    Art
#    Default
#    Dem
#    Ind
#    Int
#    Neg
#
#cpdef enum PronType2:
#    Prs
#    Rcp
#    Rel
#    Tot
#    Clit
#    Exc # es, ca, it, fa
#    Clit # it
#
#
#cpdef enum Reflex:
#    Yes
#
#
#cpdef enum Tense:
#    Fut
#    Imp
#    Past
#    Pres
#
#cpdef enum VerbForm1:
#    Fin
#    Ger
#    Inf
#    None_
#    Part
#    PartFut
#    PartPast
#
#cpdef enum VerbForm2:
#    PartPres
#    Sup
#    Trans
#    Gdv # la
#
#
#cpdef enum Voice:
#    Act
#    Cau
#    Pass
#    Mid # gkc
#    Int # hb
#
#
#cpdef enum Abbr:
#    Yes # cz, fi, sl, U
#
#cpdef enum AdpType:
#    Prep # cz, U
#    Post # U
#    Voc # cz
#    Comprep # cz
#    Circ # U
#    Voc # U
#
#
#cpdef enum AdvType1:
#    # U
#    Man
#    Loc
#    Tim
#    Deg
#    Cau
#    Mod
#    Sta
#    Ex
#
#cpdef enum AdvType2:
#    Adadj
#
#cpdef enum ConjType:
#    Oper # cz, U
#    Comp # cz, U
#
#cpdef enum Connegative:
#    Yes # fi
#
#
#cpdef enum Derivation1:
#    Minen # fi
#    Sti # fi
#    Inen # fi
#    Lainen # fi
#    Ja # fi
#    Ton # fi
#    Vs # fi
#    Ttain # fi
#
#cpdef enum Derivation2:
#    Ttaa
#
#
#cpdef enum Echo:
#    Rdp # U
#    Ech # U
#
#
#cpdef enum Foreign:
#    Foreign # cz, fi, U
#    Fscript # cz, fi, U
#    Tscript # cz, U
#    Yes # sl
#
#
#cpdef enum Gender_dat:
#    Masc # bq, U
#    Fem # bq, U
#
#
#cpdef enum Gender_erg:
#    Masc # bq
#    Fem # bq
#
#
#cpdef enum Gender_psor:
#    Masc # cz, sl, U
#    Fem # cz, sl, U
#    Neut # sl
#
#
#cpdef enum Hyph:
#    Yes # cz, U
#
#
#cpdef enum InfForm:
#    One # fi
#    Two # fi
#    Three # fi
#
#
#cpdef enum NameType:
#    Geo # U, cz
#    Prs # U, cz
#    Giv # U, cz
#    Sur # U, cz
#    Nat # U, cz
#    Com # U, cz
#    Pro # U, cz
#    Oth # U, cz
#
#
#cpdef enum NounType:
#    Com # U
#    Prop # U
#    Class # U
#
#cpdef enum Number_abs:
#    Sing # bq, U
#    Plur # bq, U
#
#cpdef enum Number_dat:
#    Sing # bq, U
#    Plur # bq, U
#
#cpdef enum Number_erg:
#    Sing # bq, U
#    Plur # bq, U
#
#cpdef enum Number_psee:
#    Sing # U
#    Plur # U
#
#
#cpdef enum Number_psor:
#    Sing # cz, fi, sl, U
#    Plur # cz, fi, sl, U
#
#
#cpdef enum NumForm:
#    Digit # cz, sl, U
#    Roman # cz, sl, U
#    Word # cz, sl, U
#
#
#cpdef enum NumValue:
#    One # cz, U
#    Two # cz, U
#    Three # cz, U
#
#
#cpdef enum PartForm:
#    Pres # fi
#    Past # fi
#    Agt # fi
#    Neg # fi
#
#
#cpdef enum PartType:
#    Mod # U
#    Emp # U
#    Res # U
#    Inf # U
#    Vbp # U
#
#cpdef enum Person_abs:
#    One # bq, U
#    Two # bq, U
#    Three # bq, U
#
#
#cpdef enum Person_dat:
#    One # bq, U
#    Two # bq, U
#    Three # bq, U
#
#
#cpdef enum Person_erg:
#    One # bq, U
#    Two # bq, U
#    Three # bq, U
#
#
#cpdef enum Person_psor:
#    One # fi, U
#    Two # fi, U
#    Three # fi, U
#
#
#cpdef enum Polite:
#    Inf # bq, U
#    Pol # bq, U
#
#
#cpdef enum Polite_abs:
#    Inf # bq, U
#    Pol # bq, U
#
#
#cpdef enum Polite_erg:
#    Inf # bq, U
#    Pol # bq, U
#
#
#cpdef enum Polite_dat:
#    Inf # bq, U
#    Pol # bq, U
#
#
#cpdef enum Prefix:
#    Yes # U
#
#
#cpdef enum PrepCase:
#    Npr # cz
#    Pre # U
#
#
#cpdef enum PunctSide:
#    Ini # U
#    Fin # U
#
#cpdef enum PunctType1:
#    Peri # U
#    Qest # U
#    Excl # U
#    Quot # U
#    Brck # U
#    Comm # U
#    Colo # U
#    Semi # U
#
#cpdef enum PunctType2:
#    Dash # U
#
#
#cpdef enum Style1:
#    Arch # cz, fi, U
#    Rare # cz, fi, U
#    Poet # cz, U
#    Norm # cz, U
#    Coll # cz, U
#    Vrnc # cz, U
#    Sing # cz, U
#    Expr # cz, U
#
#
#cpdef enum Style2:
#    Derg # cz, U
#    Vulg # cz, U
#
#
#cpdef enum Typo:
#    Yes # fi, U
#
#
#cpdef enum Variant:
#    Short # cz
#    Bound # cz, sl
#
#
#cpdef enum VerbType:
#    Aux # U
#    Cop # U
#    Mod # U
#    Light # U
#

cpdef enum Value_t:
    Animacy_Anim
    Animacy_Inam
    Aspect_Freq
    Aspect_Imp
    Aspect_Mod
    Aspect_None_
    Aspect_Perf
    Case_Abe
    Case_Abl
    Case_Abs
    Case_Acc
    Case_Ade
    Case_All
    Case_Cau
    Case_Com
    Case_Dat
    Case_Del
    Case_Dis
    Case_Ela
    Case_Ess
    Case_Gen
    Case_Ill
    Case_Ine
    Case_Ins
    Case_Loc
    Case_Lat
    Case_Nom
    Case_Par
    Case_Sub
    Case_Sup
    Case_Tem
    Case_Ter
    Case_Tra
    Case_Voc
    Definite_Two
    Definite_Def
    Definite_Red
    Definite_Ind
    Degree_Cmp
    Degree_Comp
    Degree_None
    Degree_Pos
    Degree_Sup
    Degree_Abs
    Degree_Com
    Degree_Dim # du
    Gender_Com
    Gender_Fem
    Gender_Masc
    Gender_Neut
    Mood_Cnd
    Mood_Imp
    Mood_Ind
    Mood_N
    Mood_Pot
    Mood_Sub
    Mood_Opt
    Negative_Neg
    Negative_Pos
    Negative_Yes
    Number_Com
    Number_Dual
    Number_None
    Number_Plur
    Number_Sing
    Number_Ptan # bg
    Number_Count # bg
    NumType_Card
    NumType_Dist
    NumType_Frac
    NumType_Gen
    NumType_Mult
    NumType_None
    NumType_Ord
    NumType_Sets
    Person_One
    Person_Two
    Person_Three
    Person_None
    Poss_Yes
    PronType_AdvPart
    PronType_Art
    PronType_Default
    PronType_Dem
    PronType_Ind
    PronType_Int
    PronType_Neg
    PronType_Prs
    PronType_Rcp
    PronType_Rel
    PronType_Tot
    PronType_Clit
    PronType_Exc # es, ca, it, fa
    Reflex_Yes
    Tense_Fut
    Tense_Imp
    Tense_Past
    Tense_Pres
    VerbForm_Fin
    VerbForm_Ger
    VerbForm_Inf
    VerbForm_None
    VerbForm_Part
    VerbForm_PartFut
    VerbForm_PartPast
    VerbForm_PartPres
    VerbForm_Sup
    VerbForm_Trans
    VerbForm_Gdv # la
    Voice_Act
    Voice_Cau
    Voice_Pass
    Voice_Mid # gkc
    Voice_Int # hb
    Abbr_Yes # cz, fi, sl, U
    AdpType_Prep # cz, U
    AdpType_Post # U
    AdpType_Voc # cz
    AdpType_Comprep # cz
    AdpType_Circ # U
    AdvType_Man
    AdvType_Loc
    AdvType_Tim
    AdvType_Deg
    AdvType_Cau
    AdvType_Mod
    AdvType_Sta
    AdvType_Ex
    AdvType_Adadj
    ConjType_Oper # cz, U
    ConjType_Comp # cz, U
    Connegative_Yes # fi
    Derivation_Minen # fi
    Derivation_Sti # fi
    Derivation_Inen # fi
    Derivation_Lainen # fi
    Derivation_Ja # fi
    Derivation_Ton # fi
    Derivation_Vs # fi
    Derivation_Ttain # fi
    Derivation_Ttaa # fi
    Echo_Rdp # U
    Echo_Ech # U
    Foreign_Foreign # cz, fi, U
    Foreign_Fscript # cz, fi, U
    Foreign_Tscript # cz, U
    Foreign_Yes # sl
    Gender_dat_Masc # bq, U
    Gender_dat_Fem # bq, U
    Gender_erg_Masc # bq
    Gender_erg_Fem # bq
    Gender_psor_Masc # cz, sl, U
    Gender_psor_Fem # cz, sl, U
    Gender_psor_Neut # sl
    Hyph_Yes # cz, U
    InfForm_One # fi
    InfForm_Two # fi
    InfForm_Three # fi
    NameType_Geo # U, cz
    NameType_Prs # U, cz
    NameType_Giv # U, cz
    NameType_Sur # U, cz
    NameType_Nat # U, cz
    NameType_Com # U, cz
    NameType_Pro # U, cz
    NameType_Oth # U, cz
    NounType_Com # U
    NounType_Prop # U
    NounType_Class # U
    Number_abs_Sing # bq, U
    Number_abs_Plur # bq, U
    Number_dat_Sing # bq, U
    Number_dat_Plur # bq, U
    Number_erg_Sing # bq, U
    Number_erg_Plur # bq, U
    Number_psee_Sing # U
    Number_psee_Plur # U
    Number_psor_Sing # cz, fi, sl, U
    Number_psor_Plur # cz, fi, sl, U
    NumForm_Digit # cz, sl, U
    NumForm_Roman # cz, sl, U
    NumForm_Word # cz, sl, U
    NumValue_One # cz, U
    NumValue_Two # cz, U
    NumValue_Three # cz, U
    PartForm_Pres # fi
    PartForm_Past # fi
    PartForm_Agt # fi
    PartForm_Neg # fi
    PartType_Mod # U
    PartType_Emp # U
    PartType_Res # U
    PartType_Inf # U
    PartType_Vbp # U
    Person_abs_One # bq, U
    Person_abs_Two # bq, U
    Person_abs_Three # bq, U
    Person_dat_One # bq, U
    Person_dat_Two # bq, U
    Person_dat_Three # bq, U
    Person_erg_One # bq, U
    Person_erg_Two # bq, U
    Person_erg_Three # bq, U
    Person_psor_One # fi, U
    Person_psor_Two # fi, U
    Person_psor_Three # fi, U
    Polite_Inf # bq, U
    Polite_Pol # bq, U
    Polite_abs_Inf # bq, U
    Polite_abs_Pol # bq, U
    Polite_erg_Inf # bq, U
    Polite_erg_Pol # bq, U
    Polite_dat_Inf # bq, U
    Polite_dat_Pol # bq, U
    Prefix_Yes # U
    PrepCase_Npr # cz
    PrepCase_Pre # U
    PunctSide_Ini # U
    PunctSide_Fin # U
    PunctType_Peri # U
    PunctType_Qest # U
    PunctType_Excl # U
    PunctType_Quot # U
    PunctType_Brck # U
    PunctType_Comm # U
    PunctType_Colo # U
    PunctType_Semi # U
    PunctType_Dash # U
    Style_Arch # cz, fi, U
    Style_Rare # cz, fi, U
    Style_Poet # cz, U
    Style_Norm # cz, U
    Style_Coll # cz, U
    Style_Vrnc # cz, U
    Style_Sing # cz, U
    Style_Expr # cz, U
    Style_Derg # cz, U
    Style_Vulg # cz, U
    Style_Yes # fi, U
    StyleVariant_StyleShort # cz
    StyleVariant_StyleBound # cz, sl
    VerbType_Aux # U
    VerbType_Cop # U
    VerbType_Mod # U
    VerbType_Light # U
