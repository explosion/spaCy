cpdef enum symbol_t:
    EMPTY_VALUE
    Attr_is_alpha
    Attr_is_ascii
    Attr_is_digit
    Attr_is_lower
    Attr_is_punct
    Attr_is_space
    Attr_is_title
    Attr_is_upper
    Attr_like_url
    Attr_like_num
    Attr_like_email
    Attr_is_stop
    Attr_is_oov
    
    Attr_flag14
    Attr_flag15
    Attr_flag16
    Attr_flag17
    Attr_flag18
    Attr_flag19
    Attr_flag20
    Attr_flag21
    Attr_flag22
    Attr_flag23
    Attr_flag24
    Attr_flag25
    Attr_flag26
    Attr_flag27
    Attr_flag28
    Attr_flag29
    Attr_flag30
    Attr_flag31
    Attr_flag32
    Attr_flag33
    Attr_flag34
    Attr_flag35
    Attr_flag36
    Attr_flag37
    Attr_flag38
    Attr_flag39
    Attr_flag40
    Attr_flag41
    Attr_flag42
    Attr_flag43
    Attr_flag44
    Attr_flag45
    Attr_flag46
    Attr_flag47
    Attr_flag48
    Attr_flag49
    Attr_flag50
    Attr_flag51
    Attr_flag52
    Attr_flag53
    Attr_flag54
    Attr_flag55
    Attr_flag56
    Attr_flag57
    Attr_flag58
    Attr_flag59
    Attr_flag60
    Attr_flag61
    Attr_flag62
    Attr_flag63

    Attr_id
    Attr_orth
    Attr_lower
    Attr_norm
    Attr_shape
    Attr_prefix
    Attr_suffix

    Attr_length
    Attr_cluster
    Attr_lemma
    Attr_pos
    Attr_tag
    Attr_dep
    Attr_ent_iob
    Attr_ent_type
    Attr_head
    Attr_spacy
    Attr_prob

    POS_adj
    POS_adp
    POS_adv
    POS_aux
    POS_conj
    POS_det
    POS_intj
    POS_noun
    POS_num
    POS_part
    POS_pron
    POS_propn
    POS_punct
    POS_sconj
    POS_sym
    POS_verb
    POS_x
    POS_eol
    POS_space

    Animacy_anim
    Animacy_inam
    Aspect_freq
    Aspect_imp
    Aspect_mod
    Aspect_none
    Aspect_perf
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
    Definite_two
    Definite_def
    Definite_red
    Definite_ind
    Degree_cmp
    Degree_comp
    Degree_none
    Degree_pos
    Degree_sup
    Degree_abs
    Degree_com
    Degree_dim # du
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
    Negative_neg
    Negative_pos
    Negative_yes
    Number_com
    Number_dual
    Number_none
    Number_plur
    Number_sing
    Number_ptan # bg
    Number_count # bg
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
    PronType_exc # es, ca, it, fa
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
    VerbForm_gdv # la
    Voice_act
    Voice_cau
    Voice_pass
    Voice_mid # gkc
    Voice_int # hb
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
    Polite_inf # bq, U
    Polite_pol # bq, U
    Polite_abs_inf # bq, U
    Polite_abs_pol # bq, U
    Polite_erg_inf # bq, U
    Polite_erg_pol # bq, U
    Polite_dat_inf # bq, U
    Polite_dat_pol # bq, U
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

    Name_person
    Name_norp
    Name_facility
    Name_org
    Name_gpe
    Name_loc
    Name_product
    Name_event
    Name_work_of_art
    Name_language

    Unit_date
    Unit_time
    Unit_percent
    Unit_money
    Unit_quantity
    Unit_ordinal
    Unit_cardinal

    Dep_acomp
    Dep_advcl
    Dep_advmod
    Dep_agent
    Dep_amod
    Dep_appos
    Dep_attr
    Dep_aux
    Dep_auxpass
    Dep_cc
    Dep_ccomp
    Dep_complm
    Dep_conj
    Dep_csubj
    Dep_csubjpass
    Dep_dep
    Dep_det
    Dep_dobj
    Dep_expl
    Dep_hmod
    Dep_hyph
    Dep_infmod
    Dep_intj
    Dep_iobj
    Dep_mark
    Dep_meta
    Dep_neg
    Dep_nmod
    Dep_nn
    Dep_npadvmod
    Dep_nsubj
    Dep_nsubjpass
    Dep_num
    Dep_number
    Dep_oprd
    Dep_parataxis
    Dep_partmod
    Dep_pcomp
    Dep_pobj
    Dep_poss
    Dep_possessive
    Dep_preconj
    Dep_prep
    Dep_prt
    Dep_punct
    Dep_quantmod
    Dep_rcmod
    Dep_root
    Dep_xcomp
