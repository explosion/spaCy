# cython: infer_types
# coding: utf8
from __future__ import unicode_literals

from libc.string cimport memset
import srsly
from collections import Counter

from .strings import get_string_id
from . import symbols
from .attrs cimport POS, IS_SPACE
from .attrs import LEMMA, intify_attrs
from .parts_of_speech cimport SPACE
from .parts_of_speech import IDS as POS_IDS
from .lexeme cimport Lexeme
from .errors import Errors

cdef enum univ_field_t:
    Field_Abbr
    Field_AdpType
    Field_AdvType
    Field_Animacy
    Field_Aspect
    Field_Case
    Field_ConjType
    Field_Connegative
    Field_Definite
    Field_Degree
    Field_Derivation
    Field_Echo
    Field_Foreign
    Field_Gender
    Field_Hyph
    Field_InfForm
    Field_Mood
    Field_NameType
    Field_Negative
    Field_NounType
    Field_Number
    Field_NumForm
    Field_NumType
    Field_NumValue
    Field_PartForm
    Field_PartType
    Field_Person
    Field_Polite
    Field_Polarity
    Field_Poss
    Field_Prefix
    Field_PrepCase
    Field_PronType
    Field_PunctSide
    Field_PunctType
    Field_Reflex
    Field_Style
    Field_StyleVariant
    Field_Tense
    Field_Typo
    Field_VerbForm
    Field_Voice
    Field_VerbType


def _normalize_props(props):
    """Transform deprecated string keys to correct names."""
    out = {}
    props = dict(props)
    for key in FIELDS:
        if key in props:
            attr = '%s_%s' % (key, props[key])
            if attr in FEATURES:
                props.pop(key)
                props[attr] = True
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


def parse_feature(feature):
    field = FEATURE_FIELDS[feature]
    offset = FEATURE_OFFSETS[feature]
    return (field, offset)


def get_field_id(feature):
    return FEATURE_FIELDS[feature]


def get_field_size(field):
    return FIELD_SIZES[field]


def get_field_offset(field):
    return FIELD_OFFSETS[field]


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
            attrs = _normalize_props(attrs)
            self.tag_map[tag_str] = dict(attrs)
            self.reverse_index[self.strings.add(tag_str)] = i

        self._cache = PreshMapArray(self.n_tags)
        self.exc = {}
        if exc is not None:
            for (tag, orth), attrs in exc.items():
                self.add_special_case(
                    self.strings.as_string(tag), self.strings.as_string(orth), attrs)

    def __reduce__(self):
        return (Morphology, (self.strings, self.tag_map, self.lemmatizer,
                self.exc), None, None)

    def add(self, features):
        """Insert a morphological analysis in the morphology table, if not already
        present. Returns the hash of the new analysis.
        """
        features = intify_features(features)
        cdef attr_t feature
        for feature in features:
            if feature != 0 and feature not in FEATURE_NAMES:
                raise KeyError("Unknown feature: %d" % feature)
        cdef MorphAnalysisC tag
        tag = create_rich_tag(features)
        cdef hash_t key = self.insert(tag)
        return key

    def get(self, hash_t morph):
        tag = <MorphAnalysisC*>self.tags.get(morph)
        if tag == NULL:
            return []
        else:
            return tag_to_json(tag[0])
    
    cpdef update(self, hash_t morph, features):
        """Update a morphological analysis with new feature values."""
        tag = (<MorphAnalysisC*>self.tags.get(morph))[0]
        features = intify_features(features)
        cdef attr_t feature
        for feature in features:
            field = get_field_id(feature)
            set_feature(&tag, field, feature, 1)
        morph = self.insert(tag)
        return morph

    def lemmatize(self, const univ_pos_t univ_pos, attr_t orth, morphology):
        if orth not in self.strings:
            return orth
        cdef unicode py_string = self.strings[orth]
        if self.lemmatizer is None:
            return self.strings.add(py_string.lower())
        cdef list lemma_strings
        cdef unicode lemma_string
        # Normalize features into a dict keyed by the field, to make life easier
        # for the lemmatizer. Handles string-to-int conversion too.
        string_feats = {}
        for key, value in morphology.items():
            if value is True:
                name, value = self.strings.as_string(key).split('_', 1)
                string_feats[name] = value
            else:
                string_feats[self.strings.as_string(key)] = self.strings.as_string(value)
        lemma_strings = self.lemmatizer(py_string, univ_pos, string_feats)
        lemma_string = lemma_strings[0]
        lemma = self.strings.add(lemma_string)
        return lemma

    def add_special_case(self, unicode tag_str, unicode orth_str, attrs,
                         force=False):
        """Add a special-case rule to the morphological analyser. Tokens whose
        tag and orth match the rule will receive the specified properties.

        tag (unicode): The part-of-speech tag to key the exception.
        orth (unicode): The word-form to key the exception.
        """
        attrs = dict(attrs)
        attrs = _normalize_props(attrs)
        attrs = intify_attrs(attrs, self.strings, _do_deprecated=True)
        self.exc[(tag_str, self.strings.add(orth_str))] = attrs
 
    cdef hash_t insert(self, MorphAnalysisC tag) except 0:
        cdef hash_t key = hash_tag(tag)
        if self.tags.get(key) == NULL:
            tag_ptr = <MorphAnalysisC*>self.mem.alloc(1, sizeof(MorphAnalysisC))
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

    cdef int assign_tag(self, TokenC* token, tag_str) except -1:
        cdef attr_t tag = self.strings.as_int(tag_str)
        if tag in self.reverse_index:
            tag_id = self.reverse_index[tag]
            self.assign_tag_id(token, tag_id)
        else:
            token.tag = tag

    cdef int assign_tag_id(self, TokenC* token, int tag_id) except -1:
        if tag_id > self.n_tags:
            raise ValueError(Errors.E014.format(tag=tag_id))
        # Ensure spaces get tagged as space.
        # It seems pretty arbitrary to put this logic here, but there's really
        # nowhere better. I guess the justification is that this is where the
        # specific word and the tag interact. Still, we should have a better
        # way to enforce this rule, or figure out why the statistical model fails.
        # Related to Issue #220
        if Lexeme.c_check_flag(token.lex, IS_SPACE):
            tag_id = self.reverse_index[self.strings.add('_SP')]
        tag_str = self.tag_names[tag_id]
        features = dict(self.tag_map.get(tag_str, {}))
        if features:
            pos = self.strings.as_int(features.pop(POS))
        else:
            pos = 0
        cdef attr_t lemma = <attr_t>self._cache.get(tag_id, token.lex.orth)
        if lemma == 0:
            # Ugh, self.lemmatize has opposite arg order from self.lemmatizer :(
            lemma = self.lemmatize(pos, token.lex.orth, features)
            self._cache.set(tag_id, token.lex.orth, <void*>lemma)
        token.lemma = lemma
        token.pos = <univ_pos_t>pos
        token.tag = self.strings[tag_str]
        #token.morph = self.add(features)
        token.morph = 0
        if (self.tag_names[tag_id], token.lex.orth) in self.exc:
            self._assign_tag_from_exceptions(token, tag_id)

    cdef int _assign_tag_from_exceptions(self, TokenC* token, int tag_id) except -1:
        key = (self.tag_names[tag_id], token.lex.orth)
        cdef dict attrs
        attrs = self.exc[key]
        token.pos = attrs.get(POS, token.pos)
        token.lemma = attrs.get(LEMMA, token.lemma)

    def load_morph_exceptions(self, dict exc):
        # Map (form, pos) to attributes
        for tag_str, entries in exc.items():
            for form_str, attrs in entries.items():
                self.add_special_case(tag_str, form_str, attrs)

    def to_bytes(self):
        json_tags = []
        for key in self.tags:
            tag_ptr = <MorphAnalysisC*>self.tags.get(key)
            if tag_ptr != NULL:
                json_tags.append(tag_to_json(tag_ptr[0]))
        return srsly.json_dumps(json_tags)

    def from_bytes(self, byte_string):
        raise NotImplementedError

    def to_disk(self, path):
        raise NotImplementedError

    def from_disk(self, path):
        raise NotImplementedError


cpdef univ_pos_t get_int_tag(pos_):
    return <univ_pos_t>0

cpdef intify_features(features):
    return {get_string_id(feature) for feature in features}

cdef hash_t hash_tag(MorphAnalysisC tag) nogil:
    return mrmr.hash64(&tag, sizeof(tag), 0)


def get_feature_field(feature):
    cdef attr_t key = get_string_id(feature)
    return FEATURE_FIELDS[feature]


cdef MorphAnalysisC create_rich_tag(features) except *:
    cdef MorphAnalysisC tag
    cdef attr_t feature
    memset(&tag, 0, sizeof(tag))
    for feature in features:
        field = get_field_id(feature)
        set_feature(&tag, field, feature, 1)
    return tag


cdef tag_to_json(MorphAnalysisC tag):
    features = []
    if tag.abbr != 0:
        features.append(FEATURE_NAMES[tag.abbr])
    if tag.adp_type != 0:
        features.append(FEATURE_NAMES[tag.adp_type])
    if tag.adv_type != 0:
        features.append(FEATURE_NAMES[tag.adv_type])
    if tag.animacy != 0:
        features.append(FEATURE_NAMES[tag.animacy])
    if tag.aspect != 0:
        features.append(FEATURE_NAMES[tag.aspect])
    if tag.case != 0:
        features.append(FEATURE_NAMES[tag.case])
    if tag.conj_type != 0:
        features.append(FEATURE_NAMES[tag.conj_type])
    if tag.connegative != 0:
        features.append(FEATURE_NAMES[tag.connegative])
    if tag.definite != 0:
        features.append(FEATURE_NAMES[tag.definite])
    if tag.degree != 0:
        features.append(FEATURE_NAMES[tag.degree])
    if tag.derivation != 0:
        features.append(FEATURE_NAMES[tag.derivation])
    if tag.echo != 0:
        features.append(FEATURE_NAMES[tag.echo])
    if tag.foreign != 0:
        features.append(FEATURE_NAMES[tag.foreign])
    if tag.gender != 0:
        features.append(FEATURE_NAMES[tag.gender])
    if tag.hyph != 0:
        features.append(FEATURE_NAMES[tag.hyph])
    if tag.inf_form != 0:
        features.append(FEATURE_NAMES[tag.inf_form])
    if tag.mood != 0:
        features.append(FEATURE_NAMES[tag.mood])
    if tag.negative != 0:
        features.append(FEATURE_NAMES[tag.negative])
    if tag.number != 0:
        features.append(FEATURE_NAMES[tag.number])
    if tag.name_type != 0:
        features.append(FEATURE_NAMES[tag.name_type])
    if tag.noun_type != 0:
        features.append(FEATURE_NAMES[tag.noun_type])
    if tag.num_form != 0:
        features.append(FEATURE_NAMES[tag.num_form])
    if tag.num_type != 0:
        features.append(FEATURE_NAMES[tag.num_type])
    if tag.num_value != 0:
        features.append(FEATURE_NAMES[tag.num_value])
    if tag.part_form != 0:
        features.append(FEATURE_NAMES[tag.part_form])
    if tag.part_type != 0:
        features.append(FEATURE_NAMES[tag.part_type])
    if tag.person != 0:
        features.append(FEATURE_NAMES[tag.person])
    if tag.polite != 0:
        features.append(FEATURE_NAMES[tag.polite])
    if tag.polarity != 0:
        features.append(FEATURE_NAMES[tag.polarity])
    if tag.poss != 0:
        features.append(FEATURE_NAMES[tag.poss])
    if tag.prefix != 0:
        features.append(FEATURE_NAMES[tag.prefix])
    if tag.prep_case != 0:
        features.append(FEATURE_NAMES[tag.prep_case])
    if tag.pron_type != 0:
        features.append(FEATURE_NAMES[tag.pron_type])
    if tag.punct_side != 0:
        features.append(FEATURE_NAMES[tag.punct_side])
    if tag.punct_type != 0:
        features.append(FEATURE_NAMES[tag.punct_type])
    if tag.reflex != 0:
        features.append(FEATURE_NAMES[tag.reflex])
    if tag.style != 0:
        features.append(FEATURE_NAMES[tag.style])
    if tag.style_variant != 0:
        features.append(FEATURE_NAMES[tag.style_variant])
    if tag.tense != 0:
        features.append(FEATURE_NAMES[tag.tense])
    if tag.verb_form != 0:
        features.append(FEATURE_NAMES[tag.verb_form])
    if tag.voice != 0:
        features.append(FEATURE_NAMES[tag.voice])
    if tag.verb_type != 0:
        features.append(FEATURE_NAMES[tag.verb_type])
    return features

cdef MorphAnalysisC tag_from_json(json_tag):
    cdef MorphAnalysisC tag
    return tag
 
cdef int set_feature(MorphAnalysisC* tag,
        univ_field_t field, attr_t feature, int value) except -1:
    if value == True:
        value_ = feature
    else:
        value_ = 0
    if feature == 0:
        pass
    elif field == Field_Abbr:
        tag.abbr = value_
    elif field == Field_AdpType:
        tag.adp_type = value_
    elif field == Field_AdvType:
        tag.adv_type = value_
    elif field == Field_Animacy:
        tag.animacy = value_
    elif field == Field_Aspect:
        tag.aspect = value_
    elif field == Field_Case:
        tag.case = value_
    elif field == Field_ConjType:
        tag.conj_type = value_
    elif field == Field_Connegative:
        tag.connegative = value_
    elif field == Field_Definite:
        tag.definite = value_
    elif field == Field_Degree:
        tag.degree = value_
    elif field == Field_Derivation:
        tag.derivation = value_
    elif field == Field_Echo:
        tag.echo = value_
    elif field == Field_Foreign:
        tag.foreign = value_
    elif field == Field_Gender:
        tag.gender = value_
    elif field == Field_Hyph:
        tag.hyph = value_
    elif field == Field_InfForm:
        tag.inf_form = value_
    elif field == Field_Mood:
        tag.mood = value_
    elif field == Field_Negative:
        tag.negative = value_
    elif field == Field_Number:
        tag.number = value_
    elif field == Field_NameType:
        tag.name_type = value_
    elif field == Field_NounType:
        tag.noun_type = value_
    elif field == Field_NumForm:
        tag.num_form = value_
    elif field == Field_NumType:
        tag.num_type = value_
    elif field == Field_NumValue:
        tag.num_value = value_
    elif field == Field_PartForm:
        tag.part_form = value_
    elif field == Field_PartType:
        tag.part_type = value_
    elif field == Field_Person:
        tag.person = value_
    elif field == Field_Polite:
        tag.polite = value_
    elif field == Field_Polarity:
        tag.polarity = value_
    elif field == Field_Poss:
        tag.poss = value_
    elif field == Field_Prefix:
        tag.prefix = value_
    elif field == Field_PrepCase:
        tag.prep_case = value_
    elif field == Field_PronType:
        tag.pron_type = value_
    elif field == Field_PunctSide:
        tag.punct_side = value_
    elif field == Field_PunctType:
        tag.punct_type = value_
    elif field == Field_Reflex:
        tag.reflex = value_
    elif field == Field_Style:
        tag.style = value_
    elif field == Field_StyleVariant:
        tag.style_variant = value_
    elif field == Field_Tense:
        tag.tense = value_
    elif field == Field_Typo:
        tag.typo = value_
    elif field == Field_VerbForm:
        tag.verb_form = value_
    elif field == Field_Voice:
        tag.voice = value_
    elif field == Field_VerbType:
        tag.verb_type = value_
    else:
        raise ValueError("Unknown feature: %s (%d)" % (FEATURE_NAMES.get(feature), feature))


FIELDS = {
    'Abbr': Field_Abbr,
    'AdpType': Field_AdpType,
    'AdvType': Field_AdvType,
    'Animacy': Field_Animacy,
    'Aspect': Field_Aspect,
    'Case': Field_Case,
    'ConjType': Field_ConjType,
    'Connegative': Field_Connegative,
    'Definite': Field_Definite,
    'Degree': Field_Degree,
    'Derivation': Field_Derivation,
    'Echo': Field_Echo,
    'Foreign': Field_Foreign,
    'Gender': Field_Gender,
    'Hyph': Field_Hyph,
    'InfForm': Field_InfForm,
    'Mood': Field_Mood,
    'NameType': Field_NameType,
    'Negative': Field_Negative,
    'NounType': Field_NounType,
    'Number': Field_Number,
    'NumForm': Field_NumForm,
    'NumType': Field_NumType,
    'NumValue': Field_NumValue,
    'PartForm': Field_PartForm,
    'PartType': Field_PartType,
    'Person': Field_Person,
    'Polite': Field_Polite,
    'Polarity': Field_Polarity,
    'Poss': Field_Poss,
    'Prefix': Field_Prefix,
    'PrepCase': Field_PrepCase,
    'PronType': Field_PronType,
    'PunctSide': Field_PunctSide,
    'PunctType': Field_PunctType,
    'Reflex': Field_Reflex,
    'Style': Field_Style,
    'StyleVariant': Field_StyleVariant,
    'Tense': Field_Tense,
    'Typo': Field_Typo,
    'VerbForm': Field_VerbForm,
    'Voice': Field_Voice,
    'VerbType': Field_VerbType
}

FEATURES = [
   "Abbr_yes",
   "AdpType_circ",
   "AdpType_comprep",
   "AdpType_prep ",
   "AdpType_post",
   "AdpType_voc",
   "AdvType_adadj,"
   "AdvType_cau",
   "AdvType_deg",
   "AdvType_ex",
   "AdvType_loc",
   "AdvType_man",
   "AdvType_mod",
   "AdvType_sta",
   "AdvType_tim",
   "Animacy_anim",
   "Animacy_hum",
   "Animacy_inan",
   "Animacy_nhum",
   "Aspect_freq",
   "Aspect_imp",
   "Aspect_mod",
   "Aspect_none",
   "Aspect_perf",
   "Case_abe",
   "Case_abl",
   "Case_abs",
   "Case_acc",
   "Case_ade",
   "Case_all",
   "Case_cau",
   "Case_com",
   "Case_dat",
   "Case_del",
   "Case_dis",
   "Case_ela",
   "Case_ess",
   "Case_gen",
   "Case_ill",
   "Case_ine",
   "Case_ins",
   "Case_loc",
   "Case_lat",
   "Case_nom",
   "Case_par",
   "Case_sub",
   "Case_sup",
   "Case_tem",
   "Case_ter",
   "Case_tra",
   "Case_voc",
   "ConjType_comp",
   "ConjType_oper",
   "Connegative_yes",
   "Definite_cons",
   "Definite_def",
   "Definite_ind",
   "Definite_red",
   "Definite_two",
   "Degree_abs",
   "Degree_cmp",
   "Degree_comp",
   "Degree_none",
   "Degree_pos",
   "Degree_sup",
   "Degree_com",
   "Degree_dim",
   "Derivation_minen",
   "Derivation_sti",
   "Derivation_inen",
   "Derivation_lainen",
   "Derivation_ja",
   "Derivation_ton",
   "Derivation_vs",
   "Derivation_ttain",
   "Derivation_ttaa",
   "Echo_rdp",
   "Echo_ech",
   "Foreign_foreign",
   "Foreign_fscript",
   "Foreign_tscript",
   "Foreign_yes",
   "Gender_com",
   "Gender_fem",
   "Gender_masc",
   "Gender_neut",
   "Gender_dat_masc",
   "Gender_dat_fem",
   "Gender_erg_masc",
   "Gender_erg_fem",
   "Gender_psor_masc",
   "Gender_psor_fem",
   "Gender_psor_neut",
   "Hyph_yes",
   "InfForm_one",
   "InfForm_two",
   "InfForm_three",
   "Mood_cnd",
   "Mood_imp",
   "Mood_ind",
   "Mood_n",
   "Mood_pot",
   "Mood_sub",
   "Mood_opt",
   "NameType_geo",
   "NameType_prs",
   "NameType_giv",
   "NameType_sur",
   "NameType_nat",
   "NameType_com",
   "NameType_pro",
   "NameType_oth",
   "Negative_neg",
   "Negative_pos",
   "Negative_yes",
   "NounType_com",
   "NounType_prop",
   "NounType_class",
   "Number_com",
   "Number_dual",
   "Number_none",
   "Number_plur",
   "Number_sing",
   "Number_ptan",
   "Number_count",
   "Number_abs_sing",
   "Number_abs_plur",
   "Number_dat_sing",
   "Number_dat_plur",
   "Number_erg_sing",
   "Number_erg_plur",
   "Number_psee_sing",
   "Number_psee_plur",
   "Number_psor_sing",
   "Number_psor_plur",
   "NumForm_digit",
   "NumForm_roman",
   "NumForm_word",
   "NumType_card",
   "NumType_dist",
   "NumType_frac",
   "NumType_gen",
   "NumType_mult",
   "NumType_none",
   "NumType_ord",
   "NumType_sets",
   "NumValue_one",
   "NumValue_two",
   "NumValue_three",
   "PartForm_pres",
   "PartForm_past",
   "PartForm_agt",
   "PartForm_neg",
   "PartType_mod",
   "PartType_emp",
   "PartType_res",
   "PartType_inf",
   "PartType_vbp",
   "Person_one",
   "Person_two",
   "Person_three",
   "Person_none",
   "Person_abs_one",
   "Person_abs_two",
   "Person_abs_three",
   "Person_dat_one",
   "Person_dat_two",
   "Person_dat_three",
   "Person_erg_one",
   "Person_erg_two",
   "Person_erg_three",
   "Person_psor_one",
   "Person_psor_two",
   "Person_psor_three",
   "Polarity_neg",
   "Polarity_pos",
   "Polite_inf",
   "Polite_pol",
   "Polite_abs_inf",
   "Polite_abs_pol",
   "Polite_erg_inf",
   "Polite_erg_pol",
   "Polite_dat_inf",
   "Polite_dat_pol",
   "Poss_yes",
   "Prefix_yes",
   "PrepCase_npr",
   "PrepCase_pre",
   "PronType_advPart",
   "PronType_art",
   "PronType_default",
   "PronType_dem",
   "PronType_ind",
   "PronType_int",
   "PronType_neg",
   "PronType_prs",
   "PronType_rcp",
   "PronType_rel",
   "PronType_tot",
   "PronType_clit",
   "PronType_exc",
   "PunctSide_ini",
   "PunctSide_fin",
   "PunctType_peri",
   "PunctType_qest",
   "PunctType_excl",
   "PunctType_quot",
   "PunctType_brck",
   "PunctType_comm",
   "PunctType_colo",
   "PunctType_semi",
   "PunctType_dash",
   "Reflex_yes",
   "Style_arch",
   "Style_rare",
   "Style_poet",
   "Style_norm",
   "Style_coll",
   "Style_vrnc",
   "Style_sing",
   "Style_expr",
   "Style_derg",
   "Style_vulg",
   "Style_yes",
   "StyleVariant_styleShort",
   "StyleVariant_styleBound",
   "Tense_fut",
   "Tense_imp",
   "Tense_past",
   "Tense_pres",
   "Typo_yes",
   "VerbForm_fin",
   "VerbForm_ger",
   "VerbForm_inf",
   "VerbForm_none",
   "VerbForm_part",
   "VerbForm_partFut",
   "VerbForm_partPast",
   "VerbForm_partPres",
   "VerbForm_sup",
   "VerbForm_trans",
   "VerbForm_conv",
   "VerbForm_gdv",
   "VerbType_aux",
   "VerbType_cop",
   "VerbType_mod",
   "VerbType_light",
   "Voice_act",
   "Voice_cau",
   "Voice_pass",
   "Voice_mid",
   "Voice_int",
]

FEATURE_NAMES = {get_string_id(name): name for name in FEATURES}

FEATURE_FIELDS = {feature: FIELDS[feature.split('_', 1)[0]] for feature in FEATURES}
for feat_id, name in FEATURE_NAMES.items():
    FEATURE_FIELDS[feat_id] = FEATURE_FIELDS[name]

FIELD_SIZES = Counter(FEATURE_FIELDS.values())
FEATURE_OFFSETS = {}
FIELD_OFFSETS = {}
_seen_fields = Counter()
for i, feature in enumerate(FEATURES):
    field = FEATURE_FIELDS[feature]
    FEATURE_OFFSETS[feature] = _seen_fields[field]
    if _seen_fields == 0:
        FIELD_OFFSETS[field] = i
    _seen_fields[field] += 1 
