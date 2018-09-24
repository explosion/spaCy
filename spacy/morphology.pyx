# cython: infer_types
# coding: utf8
from __future__ import unicode_literals

from libc.string cimport memset
import ujson as json

from .attrs cimport POS, IS_SPACE
from .attrs import LEMMA, intify_attrs
from .parts_of_speech cimport SPACE
from .parts_of_speech import IDS as POS_IDS
from .lexeme cimport Lexeme
from .errors import Errors



def _normalize_props(props):
    """Transform deprecated string keys to correct names."""
    out = {}
    for key, value in props.items():
        if key == POS:
            if hasattr(value, 'upper'):
                value = value.upper()
            if value in POS_IDS:
                value = POS_IDS[value]
            out[key] = value
        elif isinstance(key, int):
            out[key] = value
        elif key.lower() == 'pos':
            out[POS] = POS_IDS[value.upper()]
        else:
            out[key] = value
    return out


cdef class Morphology:
    '''Store the possible morphological analyses for a language, and index them
    by hash.
    
    To save space on each token, tokens only know the hash of their morphological
    analysis, so queries of morphological attributes are delegated
    to this class.
    '''
    def __init__(self, StringStore string_store, tag_map, lemmatizer, exc=None):
        self.mem = Pool()
        self.strings = string_store
        self.tags = PreshMap()
        # Add special space symbol. We prefix with underscore, to make sure it
        # always sorts to the end.
        space_attrs = tag_map.get('SP', {POS: SPACE})
        if '_SP' not in tag_map:
            self.strings.add('_SP')
            tag_map = dict(tag_map)
            tag_map['_SP'] = space_attrs
        self.tag_names = tuple(sorted(tag_map.keys()))
        self.tag_map = {}
        self.lemmatizer = lemmatizer
        self.n_tags = len(tag_map)
        self.reverse_index = {}
        for i, (tag_str, attrs) in enumerate(sorted(tag_map.items())):
            self.tag_map[tag_str] = dict(attrs)
            self.reverse_index[i] = self.strings.add(tag_str)

        self._cache = PreshMapArray(self.n_tags)
        self.exc = {}
        if exc is not None:
            for (tag_str, orth_str), attrs in exc.items():
                self.add_special_case(tag_str, orth_str, attrs)
    
    def add(self, features):
        """Insert a morphological analysis in the morphology table, if not already
        present. Returns the hash of the new analysis.
        """
        features = intify_features(self.strings, features)
        cdef RichTagC tag = create_rich_tag(features)
        cdef hash_t key = self.insert(tag)
        return key

    def lemmatize(self, const univ_pos_t univ_pos, attr_t orth, morphology):
        if orth not in self.strings:
            return orth
        cdef unicode py_string = self.strings[orth]
        if self.lemmatizer is None:
            return self.strings.add(py_string.lower())
        cdef list lemma_strings
        cdef unicode lemma_string
        lemma_strings = self.lemmatizer(py_string, univ_pos, morphology)
        lemma_string = lemma_strings[0]
        lemma = self.strings.add(lemma_string)
        return lemma
 
    cdef hash_t insert(self, RichTagC tag) except 0:
        cdef hash_t key = hash_tag(tag)
        if self.tags.get(key) == NULL:
            tag_ptr = <RichTagC*>self.mem.alloc(1, sizeof(RichTagC))
            tag_ptr[0] = tag
            self.tags.set(key, <void*>tag_ptr)
        return key
    
    cdef int assign_untagged(self, TokenC* token) except -1:
        """Set morphological attributes on a token without a POS tag. Uses
        the lemmatizer's lookup() method, which looks up the string in the
        table provided by the language data as lemma_lookup (if available).
        """
        if token.lemma == 0:
            orth_str = self.strings[token.lex.orth]
            lemma = self.lemmatizer.lookup(orth_str)
            token.lemma = self.strings.add(lemma)

    cdef int assign_tag(self, TokenC* token, tag) except -1:
        if isinstance(tag, basestring):
            tag = self.strings.add(tag)
        if tag in self.reverse_index:
            tag_id = self.reverse_index[tag]
            self.assign_tag_id(token, tag_id)
        else:
            token.tag = tag

    cdef int assign_tag_id(self, TokenC* token, int tag_id) except -1:
        if tag_id > self.n_tags:
            raise ValueError(Errors.E014.format(tag=tag_id))
        # TODO: It's pretty arbitrary to put this logic here. I guess the
        # justification is that this is where the specific word and the tag
        # interact. Still, we should have a better way to enforce this rule, or
        # figure out why the statistical model fails. Related to Issue #220
        if Lexeme.c_check_flag(token.lex, IS_SPACE):
            tag_id = self.reverse_index[self.strings.add('_SP')]
        lemma = <attr_t>self._cache.get(tag_id, token.lex.orth)
        if lemma == 0:
            tag_str = self.tag_names[tag_id]
            features = dict(self.tag_map.get(tag_str, {}))
            pos = self.strings.as_int(features.pop('POS'))
            lemma = self.lemmatize(pos, token.lex.orth, features)
            self._cache.set(tag_id, token.lex.orth, lemma)
        token.lemma = lemma
        token.pos = pos
        token.tag = self.strings[tag_str]
        token.morph = self.add(attrs)

    cdef update_morph(self, hash_t morph, features):
        """Update a morphological analysis with new feature values."""
        tag = (<RichTagC*>self.tags.get(morph))[0]
        cdef univ_morph_t feature
        cdef int value
        for feature_, value in features.items():
            feature = self.strings.as_int(feature_)
            set_feature(&tag, feature, 1)
        morph = self.insert_tag(tag)
        return morph

    def to_bytes(self):
        json_tags = []
        for key in self.tags:
            tag_ptr = <RichTagC*>self.tags.get(key)
            if tag_ptr != NULL:
                json_tags.append(tag_to_json(tag_ptr[0]))
        raise json.dumps(json_tags)

    def from_bytes(self, byte_string):
        raise NotImplementedError

    def to_disk(self, path):
        raise NotImplementedError

    def from_disk(self, path):
        raise NotImplementedError


cpdef univ_pos_t get_int_tag(pos_):
    return <univ_pos_t>0

cpdef intify_features(StringStore strings, features):
    return {strings.as_int(feature) for feature in features}

cdef hash_t hash_tag(RichTagC tag) nogil:
    return mrmr.hash64(&tag, sizeof(tag), 0)

cdef RichTagC create_rich_tag(pos_, features):
    cdef RichTagC tag
    cdef univ_morph_t feature
    tag.pos = get_int_tag(pos_)
    for feature in features:
        set_feature(&tag, feature, 1)
    return tag

cdef tag_to_json(RichTagC tag):
    return {}

cdef RichTagC tag_from_json(json_tag):
    cdef RichTagC tag
    return tag
 
cdef int set_feature(RichTagC* tag, univ_morph_t feature, int value) nogil:
    if value == True:
        value_ = feature
    else:
        value_ = NIL
    if feature == NIL:
        pass
    if is_abbr_feature(feature):
        tag.abbr = value_
    elif is_adp_type_feature(feature):
        tag.adp_type = value_
    elif is_adv_type_feature(feature):
        tag.adv_type = value_
    elif is_animacy_feature(feature):
        tag.animacy = value_
    elif is_aspect_feature(feature):
        tag.aspect = value_
    elif is_case_feature(feature):
        tag.case = value_
    elif is_conj_type_feature(feature):
        tag.conj_type = value_
    elif is_connegative_feature(feature):
        tag.connegative = value_
    elif is_definite_feature(feature):
        tag.definite = value_
    elif is_degree_feature(feature):
        tag.degree = value_
    elif is_derivation_feature(feature):
        tag.derivation = value_
    elif is_echo_feature(feature):
        tag.echo = value_
    elif is_foreign_feature(feature):
        tag.foreign = value_
    elif is_gender_feature(feature):
        tag.gender = value_
    elif is_hyph_feature(feature):
        tag.hyph = value_
    elif is_inf_form_feature(feature):
        tag.inf_form = value_
    elif is_mood_feature(feature):
        tag.mood = value_
    elif is_negative_feature(feature):
        tag.negative = value_
    elif is_number_feature(feature):
        tag.number = value_
    elif is_name_type_feature(feature):
        tag.name_type = value_
    elif is_num_form_feature(feature):
        tag.num_form = value_
    elif is_num_value_feature(feature):
        tag.num_value = value_
    elif is_part_form_feature(feature):
        tag.part_form = value_
    elif is_part_type_feature(feature):
        tag.part_type = value_
    elif is_person_feature(feature):
        tag.person = value_
    elif is_polite_feature(feature):
        tag.polite = value_
    elif is_polarity_feature(feature):
        tag.polarity = value_
    elif is_poss_feature(feature):
        tag.poss = value_
    elif is_prefix_feature(feature):
        tag.prefix = value_
    elif is_prep_case_feature(feature):
        tag.prep_case = value_
    elif is_pron_type_feature(feature):
        tag.pron_type = value_
    elif is_punct_side_feature(feature):
        tag.punct_type = value_
    elif is_reflex_feature(feature):
        tag.reflex = value_
    elif is_style_feature(feature):
        tag.style = value_
    elif is_style_variant_feature(feature):
        tag.style_variant = value_
    elif is_tense_feature(feature):
        tag.tense = value_
    elif is_verb_form_feature(feature):
        tag.verb_form = value_
    elif is_voice_feature(feature):
        tag.voice = value_
    elif is_verb_type_feature(feature):
        tag.verb_type = value_
    else:
        with gil:
            raise ValueError("Unknown feature: %d" % feature)

cdef int is_abbr_feature(univ_morph_t abbr) nogil:
    return 0

cdef int is_adp_type_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_adv_type_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_animacy_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_aspect_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_case_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_conj_type_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_connegative_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_definite_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_degree_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_derivation_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_echo_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_foreign_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_gender_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_hyph_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_inf_form_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_mood_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_negative_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_number_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_name_type_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_num_form_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_num_type_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_num_value_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_part_form_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_part_type_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_person_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_polite_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_polarity_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_poss_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_prefix_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_prep_case_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_pron_type_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_punct_side_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_punct_type_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_reflex_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_style_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_style_variant_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_tense_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_verb_form_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_voice_feature(univ_morph_t feature) nogil:
    return 0

cdef int is_verb_type_feature(univ_morph_t feature) nogil:
    return 0




IDS = {
    "Animacy_anim": Animacy_anim,
    "Animacy_inan": Animacy_inan,
    "Animacy_hum": Animacy_hum, # U20
    "Animacy_nhum": Animacy_nhum,
    "Aspect_freq": Aspect_freq,
    "Aspect_imp": Aspect_imp,
    "Aspect_mod": Aspect_mod,
    "Aspect_none": Aspect_none,
    "Aspect_perf": Aspect_perf,
    "Case_abe": Case_abe,
    "Case_abl": Case_abl,
    "Case_abs": Case_abs,
    "Case_acc": Case_acc,
    "Case_ade": Case_ade,
    "Case_all": Case_all,
    "Case_cau": Case_cau,
    "Case_com": Case_com,
    "Case_dat": Case_dat,
    "Case_del": Case_del,
    "Case_dis": Case_dis,
    "Case_ela": Case_ela,
    "Case_ess": Case_ess,
    "Case_gen": Case_gen,
    "Case_ill": Case_ill,
    "Case_ine": Case_ine,
    "Case_ins": Case_ins,
    "Case_loc": Case_loc,
    "Case_lat": Case_lat,
    "Case_nom": Case_nom,
    "Case_par": Case_par,
    "Case_sub": Case_sub,
    "Case_sup": Case_sup,
    "Case_tem": Case_tem,
    "Case_ter": Case_ter,
    "Case_tra": Case_tra,
    "Case_voc": Case_voc,
    "Definite_two": Definite_two,
    "Definite_def": Definite_def,
    "Definite_red": Definite_red,
    "Definite_cons": Definite_cons,  # U20
    "Definite_ind": Definite_ind,
    "Degree_cmp": Degree_cmp,
    "Degree_comp": Degree_comp,
    "Degree_none": Degree_none,
    "Degree_pos": Degree_pos,
    "Degree_sup": Degree_sup,
    "Degree_abs": Degree_abs,
    "Degree_com": Degree_com,
    "Degree_dim ": Degree_dim,  # du
    "Gender_com": Gender_com,
    "Gender_fem": Gender_fem,
    "Gender_masc": Gender_masc,
    "Gender_neut": Gender_neut,
    "Mood_cnd": Mood_cnd,
    "Mood_imp": Mood_imp,
    "Mood_ind": Mood_ind,
    "Mood_n": Mood_n,
    "Mood_pot": Mood_pot,
    "Mood_sub": Mood_sub,
    "Mood_opt": Mood_opt,
    "Negative_neg": Negative_neg,
    "Negative_pos": Negative_pos,
    "Negative_yes": Negative_yes,
    "Polarity_neg": Polarity_neg,  # U20
    "Polarity_pos": Polarity_pos,  # U20
    "Number_com": Number_com,
    "Number_dual": Number_dual,
    "Number_none": Number_none,
    "Number_plur": Number_plur,
    "Number_sing": Number_sing,
    "Number_ptan ": Number_ptan,  # bg
    "Number_count ": Number_count,  # bg
    "NumType_card": NumType_card,
    "NumType_dist": NumType_dist,
    "NumType_frac": NumType_frac,
    "NumType_gen": NumType_gen,
    "NumType_mult": NumType_mult,
    "NumType_none": NumType_none,
    "NumType_ord": NumType_ord,
    "NumType_sets": NumType_sets,
    "Person_one": Person_one,
    "Person_two": Person_two,
    "Person_three": Person_three,
    "Person_none": Person_none,
    "Poss_yes": Poss_yes,
    "PronType_advPart": PronType_advPart,
    "PronType_art": PronType_art,
    "PronType_default": PronType_default,
    "PronType_dem": PronType_dem,
    "PronType_ind": PronType_ind,
    "PronType_int": PronType_int,
    "PronType_neg": PronType_neg,
    "PronType_prs": PronType_prs,
    "PronType_rcp": PronType_rcp,
    "PronType_rel": PronType_rel,
    "PronType_tot": PronType_tot,
    "PronType_clit": PronType_clit,
    "PronType_exc ": PronType_exc,  # es, ca, it, fa,
    "Reflex_yes": Reflex_yes,
    "Tense_fut": Tense_fut,
    "Tense_imp": Tense_imp,
    "Tense_past": Tense_past,
    "Tense_pres": Tense_pres,
    "VerbForm_fin": VerbForm_fin,
    "VerbForm_ger": VerbForm_ger,
    "VerbForm_inf": VerbForm_inf,
    "VerbForm_none": VerbForm_none,
    "VerbForm_part": VerbForm_part,
    "VerbForm_partFut": VerbForm_partFut,
    "VerbForm_partPast": VerbForm_partPast,
    "VerbForm_partPres": VerbForm_partPres,
    "VerbForm_sup": VerbForm_sup,
    "VerbForm_trans": VerbForm_trans,
    "VerbForm_conv": VerbForm_conv,  # U20
    "VerbForm_gdv ": VerbForm_gdv,  # la,
    "Voice_act": Voice_act,
    "Voice_cau": Voice_cau,
    "Voice_pass": Voice_pass,
    "Voice_mid ": Voice_mid,  # gkc,
    "Voice_int ": Voice_int,  # hb,
    "Abbr_yes ": Abbr_yes,  # cz, fi, sl, U,
    "AdpType_prep ": AdpType_prep,  # cz, U,
    "AdpType_post ": AdpType_post,  # U,
    "AdpType_voc ": AdpType_voc,  # cz,
    "AdpType_comprep ": AdpType_comprep,  # cz,
    "AdpType_circ ": AdpType_circ,  # U,
    "AdvType_man": AdvType_man,
    "AdvType_loc": AdvType_loc,
    "AdvType_tim": AdvType_tim,
    "AdvType_deg": AdvType_deg,
    "AdvType_cau": AdvType_cau,
    "AdvType_mod": AdvType_mod,
    "AdvType_sta": AdvType_sta,
    "AdvType_ex": AdvType_ex,
    "AdvType_adadj": AdvType_adadj,
    "ConjType_oper ": ConjType_oper,  # cz, U,
    "ConjType_comp ": ConjType_comp,  # cz, U,
    "Connegative_yes ": Connegative_yes,  # fi,
    "Derivation_minen ": Derivation_minen,  # fi,
    "Derivation_sti ": Derivation_sti,  # fi,
    "Derivation_inen ": Derivation_inen,  # fi,
    "Derivation_lainen ": Derivation_lainen,  # fi,
    "Derivation_ja ": Derivation_ja,  # fi,
    "Derivation_ton ": Derivation_ton,  # fi,
    "Derivation_vs ": Derivation_vs,  # fi,
    "Derivation_ttain ": Derivation_ttain,  # fi,
    "Derivation_ttaa ": Derivation_ttaa,  # fi,
    "Echo_rdp ": Echo_rdp,  # U,
    "Echo_ech ": Echo_ech,  # U,
    "Foreign_foreign ": Foreign_foreign,  # cz, fi, U,
    "Foreign_fscript ": Foreign_fscript,  # cz, fi, U,
    "Foreign_tscript ": Foreign_tscript,  # cz, U,
    "Foreign_yes ": Foreign_yes,  # sl,
    "Gender_dat_masc ": Gender_dat_masc,  # bq, U,
    "Gender_dat_fem ": Gender_dat_fem,  # bq, U,
    "Gender_erg_masc ": Gender_erg_masc,  # bq,
    "Gender_erg_fem ": Gender_erg_fem,  # bq,
    "Gender_psor_masc ": Gender_psor_masc,  # cz, sl, U,
    "Gender_psor_fem ": Gender_psor_fem,  # cz, sl, U,
    "Gender_psor_neut ": Gender_psor_neut,  # sl,
    "Hyph_yes ": Hyph_yes,  # cz, U,
    "InfForm_one ": InfForm_one,  # fi,
    "InfForm_two ": InfForm_two,  # fi,
    "InfForm_three ": InfForm_three,  # fi,
    "NameType_geo ": NameType_geo,  # U, cz,
    "NameType_prs ": NameType_prs,  # U, cz,
    "NameType_giv ": NameType_giv,  # U, cz,
    "NameType_sur ": NameType_sur,  # U, cz,
    "NameType_nat ": NameType_nat,  # U, cz,
    "NameType_com ": NameType_com,  # U, cz,
    "NameType_pro ": NameType_pro,  # U, cz,
    "NameType_oth ": NameType_oth,  # U, cz,
    "NounType_com ": NounType_com,  # U,
    "NounType_prop ": NounType_prop,  # U,
    "NounType_class ": NounType_class,  # U,
    "Number_abs_sing ": Number_abs_sing,  # bq, U,
    "Number_abs_plur ": Number_abs_plur,  # bq, U,
    "Number_dat_sing ": Number_dat_sing,  # bq, U,
    "Number_dat_plur ": Number_dat_plur,  # bq, U,
    "Number_erg_sing ": Number_erg_sing,  # bq, U,
    "Number_erg_plur ": Number_erg_plur,  # bq, U,
    "Number_psee_sing ": Number_psee_sing,  # U,
    "Number_psee_plur ": Number_psee_plur,  # U,
    "Number_psor_sing ": Number_psor_sing,  # cz, fi, sl, U,
    "Number_psor_plur ": Number_psor_plur,  # cz, fi, sl, U,
    "NumForm_digit ": NumForm_digit,  # cz, sl, U,
    "NumForm_roman ": NumForm_roman,  # cz, sl, U,
    "NumForm_word ": NumForm_word,  # cz, sl, U,
    "NumValue_one ": NumValue_one,  # cz, U,
    "NumValue_two ": NumValue_two,  # cz, U,
    "NumValue_three ": NumValue_three,  # cz, U,
    "PartForm_pres ": PartForm_pres,  # fi,
    "PartForm_past ": PartForm_past,  # fi,
    "PartForm_agt ": PartForm_agt,  # fi,
    "PartForm_neg ": PartForm_neg,  # fi,
    "PartType_mod ": PartType_mod,  # U,
    "PartType_emp ": PartType_emp,  # U,
    "PartType_res ": PartType_res,  # U,
    "PartType_inf ": PartType_inf,  # U,
    "PartType_vbp ": PartType_vbp,  # U,
    "Person_abs_one ": Person_abs_one,  # bq, U,
    "Person_abs_two ": Person_abs_two,  # bq, U,
    "Person_abs_three ": Person_abs_three,  # bq, U,
    "Person_dat_one ": Person_dat_one,  # bq, U,
    "Person_dat_two ": Person_dat_two,  # bq, U,
    "Person_dat_three ": Person_dat_three,  # bq, U,
    "Person_erg_one ": Person_erg_one,  # bq, U,
    "Person_erg_two ": Person_erg_two,  # bq, U,
    "Person_erg_three ": Person_erg_three,  # bq, U,
    "Person_psor_one ": Person_psor_one,  # fi, U,
    "Person_psor_two ": Person_psor_two,  # fi, U,
    "Person_psor_three ": Person_psor_three,  # fi, U,
    "Polite_inf ": Polite_inf,  # bq, U,
    "Polite_pol ": Polite_pol,  # bq, U,
    "Polite_abs_inf ": Polite_abs_inf,  # bq, U,
    "Polite_abs_pol ": Polite_abs_pol,  # bq, U,
    "Polite_erg_inf ": Polite_erg_inf,  # bq, U,
    "Polite_erg_pol ": Polite_erg_pol,  # bq, U,
    "Polite_dat_inf ": Polite_dat_inf,  # bq, U,
    "Polite_dat_pol ": Polite_dat_pol,  # bq, U,
    "Prefix_yes ": Prefix_yes,  # U,
    "PrepCase_npr ": PrepCase_npr,  # cz,
    "PrepCase_pre ": PrepCase_pre,  # U,
    "PunctSide_ini ": PunctSide_ini,  # U,
    "PunctSide_fin ": PunctSide_fin,  # U,
    "PunctType_peri ": PunctType_peri,  # U,
    "PunctType_qest ": PunctType_qest,  # U,
    "PunctType_excl ": PunctType_excl,  # U,
    "PunctType_quot ": PunctType_quot,  # U,
    "PunctType_brck ": PunctType_brck,  # U,
    "PunctType_comm ": PunctType_comm,  # U,
    "PunctType_colo ": PunctType_colo,  # U,
    "PunctType_semi ": PunctType_semi,  # U,
    "PunctType_dash ": PunctType_dash,  # U,
    "Style_arch ": Style_arch,  # cz, fi, U,
    "Style_rare ": Style_rare,  # cz, fi, U,
    "Style_poet ": Style_poet,  # cz, U,
    "Style_norm ": Style_norm,  # cz, U,
    "Style_coll ": Style_coll,  # cz, U,
    "Style_vrnc ": Style_vrnc,  # cz, U,
    "Style_sing ": Style_sing,  # cz, U,
    "Style_expr ": Style_expr,  # cz, U,
    "Style_derg ": Style_derg,  # cz, U,
    "Style_vulg ": Style_vulg,  # cz, U,
    "Style_yes ": Style_yes,  # fi, U,
    "StyleVariant_styleShort ": StyleVariant_styleShort,  # cz,
    "StyleVariant_styleBound ": StyleVariant_styleBound,  # cz, sl,
    "VerbType_aux ": VerbType_aux,  # U,
    "VerbType_cop ": VerbType_cop,  # U,
    "VerbType_mod ": VerbType_mod,  # U,
    "VerbType_light ": VerbType_light,  # U,
}


NAMES = [key for key, value in sorted(IDS.items(), key=lambda item: item[1])]
# Unfortunate hack here, to work around problem with long cpdef enum
# (which is generating an enormous amount of C++ in Cython 0.24+)
# We keep the enum cdef, and just make sure the names are available to Python
locals().update(IDS)
