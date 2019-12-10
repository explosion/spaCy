cdef enum symbol_t:
    NIL
    IS_ALPHA
    IS_ASCII
    IS_DIGIT
    IS_LOWER
    IS_PUNCT
    IS_SPACE
    IS_TITLE
    IS_UPPER
    LIKE_URL
    LIKE_NUM
    LIKE_EMAIL
    IS_STOP
    IS_OOV
    IS_BRACKET
    IS_QUOTE
    IS_LEFT_PUNCT
    IS_RIGHT_PUNCT
    IS_CURRENCY

    FLAG19 = 19
    FLAG20
    FLAG21
    FLAG22
    FLAG23
    FLAG24
    FLAG25
    FLAG26
    FLAG27
    FLAG28
    FLAG29
    FLAG30
    FLAG31
    FLAG32
    FLAG33
    FLAG34
    FLAG35
    FLAG36
    FLAG37
    FLAG38
    FLAG39
    FLAG40
    FLAG41
    FLAG42
    FLAG43
    FLAG44
    FLAG45
    FLAG46
    FLAG47
    FLAG48
    FLAG49
    FLAG50
    FLAG51
    FLAG52
    FLAG53
    FLAG54
    FLAG55
    FLAG56
    FLAG57
    FLAG58
    FLAG59
    FLAG60
    FLAG61
    FLAG62
    FLAG63

    ID
    ORTH
    LOWER
    NORM
    SHAPE
    PREFIX
    SUFFIX

    LENGTH
    CLUSTER
    LEMMA
    POS
    TAG
    DEP
    ENT_IOB
    ENT_TYPE
    HEAD
    SENT_START
    SPACY
    PROB
    LANG

    ADJ
    ADP
    ADV
    AUX
    CONJ
    CCONJ # U20
    DET
    INTJ
    NOUN
    NUM
    PART
    PRON
    PROPN
    PUNCT
    SCONJ
    SYM
    VERB
    X
    EOL
    SPACE

    Animacy_anim
    Animacy_inan
    Animacy_hum # U20
    Animacy_nhum
    Aspect_freq
    Aspect_imp
    Aspect_mod
    Aspect_none
    Aspect_perf
    Aspect_iter # U20
    Aspect_hab # U20
    Case_abe
    Case_abl
    Case_abs
    Case_acc
    Case_ade
    Case_all
    Case_cau
    Case_com
    Case_cmp # U20
    Case_dat
    Case_del
    Case_dis
    Case_ela
    Case_equ # U20
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
    Definite_two
    Definite_def
    Definite_red
    Definite_cons # U20
    Definite_ind
    Definite_spec # U20
    Degree_cmp
    Degree_comp
    Degree_none
    Degree_pos
    Degree_sup
    Degree_abs
    Degree_com
    Degree_dim # du
    Degree_equ # U20
    Evident_nfh # U20
    Gender_com
    Gender_fem
    Gender_masc
    Gender_neut
    Mood_cnd
    Mood_imp
    Mood_ind
    Mood_n
    Mood_pot
    Mood_sub
    Mood_opt
    Mood_prp # U20
    Mood_adm # U20
    Negative_neg
    Negative_pos
    Negative_yes
    Polarity_neg # U20
    Polarity_pos # U20
    Number_com
    Number_dual
    Number_none
    Number_plur
    Number_sing
    Number_ptan # bg
    Number_count # bg, U20
    Number_tri # U20
    NumType_card
    NumType_dist
    NumType_frac
    NumType_gen
    NumType_mult
    NumType_none
    NumType_ord
    NumType_sets
    Person_one
    Person_two
    Person_three
    Person_none
    Poss_yes
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
    PronType_exc # es, ca, it, fa, U20
    PronType_emp # U20
    Reflex_yes
    Tense_fut
    Tense_imp
    Tense_past
    Tense_pres
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
    VerbForm_vnoun # U20
    Voice_act
    Voice_cau
    Voice_pass
    Voice_mid # gkc, U20
    Voice_int # hb
    Voice_antip # U20
    Voice_dir # U20
    Voice_inv # U20
    Abbr_yes # cz, fi, sl, U
    AdpType_prep # cz, U
    AdpType_post # U
    AdpType_voc # cz
    AdpType_comprep # cz
    AdpType_circ # U
    AdvType_man
    AdvType_loc
    AdvType_tim
    AdvType_deg
    AdvType_cau
    AdvType_mod
    AdvType_sta
    AdvType_ex
    AdvType_adadj
    ConjType_oper # cz, U
    ConjType_comp # cz, U
    Connegative_yes # fi
    Derivation_minen # fi
    Derivation_sti # fi
    Derivation_inen # fi
    Derivation_lainen # fi
    Derivation_ja # fi
    Derivation_ton # fi
    Derivation_vs # fi
    Derivation_ttain # fi
    Derivation_ttaa # fi
    Echo_rdp # U
    Echo_ech # U
    Foreign_foreign # cz, fi, U
    Foreign_fscript # cz, fi, U
    Foreign_tscript # cz, U
    Foreign_yes # sl
    Gender_dat_masc # bq, U
    Gender_dat_fem # bq, U
    Gender_erg_masc # bq
    Gender_erg_fem # bq
    Gender_psor_masc # cz, sl, U
    Gender_psor_fem # cz, sl, U
    Gender_psor_neut # sl
    Hyph_yes # cz, U
    InfForm_one # fi
    InfForm_two # fi
    InfForm_three # fi
    NameType_geo # U, cz
    NameType_prs # U, cz
    NameType_giv # U, cz
    NameType_sur # U, cz
    NameType_nat # U, cz
    NameType_com # U, cz
    NameType_pro # U, cz
    NameType_oth # U, cz
    NounType_com # U
    NounType_prop # U
    NounType_class # U
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
    Number_pauc # U20
    Number_grpa # U20
    Number_grpl # U20
    Number_inv # U20
    NumForm_digit # cz, sl, U
    NumForm_roman # cz, sl, U
    NumForm_word # cz, sl, U
    NumValue_one # cz, U
    NumValue_two # cz, U
    NumValue_three # cz, U
    PartForm_pres # fi
    PartForm_past # fi
    PartForm_agt # fi
    PartForm_neg # fi
    PartType_mod # U
    PartType_emp # U
    PartType_res # U
    PartType_inf # U
    PartType_vbp # U
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
    Person_zero # U20
    Person_four # U20
    Polite_inf # bq, U
    Polite_pol # bq, U
    Polite_abs_inf # bq, U
    Polite_abs_pol # bq, U
    Polite_erg_inf # bq, U
    Polite_erg_pol # bq, U
    Polite_dat_inf # bq, U
    Polite_dat_pol # bq, U
    Polite_infm # U20
    Polite_form # U20
    Polite_form_elev # U20
    Polite_form_humb # U20
    Prefix_yes # U
    PrepCase_npr # cz
    PrepCase_pre # U
    PunctSide_ini # U
    PunctSide_fin # U
    PunctType_peri # U
    PunctType_qest # U
    PunctType_excl # U
    PunctType_quot # U
    PunctType_brck # U
    PunctType_comm # U
    PunctType_colo # U
    PunctType_semi # U
    PunctType_dash # U
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
    StyleVariant_styleShort # cz
    StyleVariant_styleBound # cz, sl
    VerbType_aux # U
    VerbType_cop # U
    VerbType_mod # U
    VerbType_light # U

    PERSON
    NORP
    FACILITY
    ORG
    GPE
    LOC
    PRODUCT
    EVENT
    WORK_OF_ART
    LANGUAGE
    LAW

    DATE
    TIME
    PERCENT
    MONEY
    QUANTITY
    ORDINAL
    CARDINAL

    acomp
    advcl
    advmod
    agent
    amod
    appos
    attr
    aux
    auxpass
    cc
    ccomp
    complm
    conj
    cop # U20
    csubj
    csubjpass
    dep
    det
    dobj
    expl
    hmod
    hyph
    infmod
    intj
    iobj
    mark
    meta
    neg
    nmod
    nn
    npadvmod
    nsubj
    nsubjpass
    num
    number
    oprd
    obj # U20
    obl # U20
    parataxis
    partmod
    pcomp
    pobj
    poss
    possessive
    preconj
    prep
    prt
    punct
    quantmod
    relcl
    rcmod
    root
    xcomp

    acl

    ENT_KB_ID
