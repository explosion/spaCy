# cython: infer_types
# coding: utf8
from __future__ import unicode_literals

from libc.string cimport memset
import srsly

from .strings import get_string_id
from . import symbols
from .attrs cimport POS, IS_SPACE
from .attrs import LEMMA, intify_attrs
from .parts_of_speech cimport SPACE
from .parts_of_speech import IDS as POS_IDS
from .lexeme cimport Lexeme
from .errors import Errors



def _normalize_props(props):
    """Transform deprecated string keys to correct names."""
    out = {}
    props = dict(props)
    for key in FIELDS:
        if key in props:
            attr = '%s_%s' % (key, props[key])
            if attr in IDS:
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
    if not hasattr(feature, 'split'):
        feature = NAMES[feature]
    key, value = feature.split('_')
    begin = 'begin_%s' % key
    # Note that this includes a 0 offset for the field, for no entry
    offset = IDS[feature] - IDS[begin]
    field_id = FIELDS[key]
    return (field_id, offset)


def get_field_size(field):
    begin = 'begin_%s' % field
    end = 'end_%s' % field
    # Extra field for no entry -- always 0
    return IDS[end] - IDS[begin]


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
        cdef univ_morph_t feature
        for feature in features:
            if feature != 0 and feature not in NAMES:
                print(list(NAMES.keys())[:10])
                print(NAMES.get(feature-1), NAMES.get(feature+1))
                raise KeyError("Unknown feature: %d" % feature)
        cdef RichTagC tag
        tag = create_rich_tag(features)
        cdef hash_t key = self.insert(tag)
        return key

    def get(self, hash_t morph):
        tag = <RichTagC*>self.tags.get(morph)
        if tag == NULL:
            return []
        else:
            return tag_to_json(tag[0])
    
    cpdef update(self, hash_t morph, features):
        """Update a morphological analysis with new feature values."""
        tag = (<RichTagC*>self.tags.get(morph))[0]
        features = intify_features(features)
        cdef univ_morph_t feature
        for feature in features:
            set_feature(&tag, feature, 1)
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
        lemma_strings = self.lemmatizer(py_string, univ_pos, morphology)
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
            tag_ptr = <RichTagC*>self.tags.get(key)
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
    return {IDS.get(feature, feature) for feature in features}

cdef hash_t hash_tag(RichTagC tag) nogil:
    return mrmr.hash64(&tag, sizeof(tag), 0)

cdef RichTagC create_rich_tag(features) except *:
    cdef RichTagC tag
    cdef univ_morph_t feature
    memset(&tag, 0, sizeof(tag))
    for feature in features:
        set_feature(&tag, feature, 1)
    return tag

cdef tag_to_json(RichTagC tag):
    features = []
    if tag.abbr != 0:
        features.append(NAMES[tag.abbr])
    if tag.adp_type != 0:
        features.append(NAMES[tag.adp_type])
    if tag.adv_type != 0:
        features.append(NAMES[tag.adv_type])
    if tag.animacy != 0:
        features.append(NAMES[tag.animacy])
    if tag.aspect != 0:
        features.append(NAMES[tag.aspect])
    if tag.case != 0:
        features.append(NAMES[tag.case])
    if tag.conj_type != 0:
        features.append(NAMES[tag.conj_type])
    if tag.connegative != 0:
        features.append(NAMES[tag.connegative])
    if tag.definite != 0:
        features.append(NAMES[tag.definite])
    if tag.degree != 0:
        features.append(NAMES[tag.degree])
    if tag.derivation != 0:
        features.append(NAMES[tag.derivation])
    if tag.echo != 0:
        features.append(NAMES[tag.echo])
    if tag.foreign != 0:
        features.append(NAMES[tag.foreign])
    if tag.gender != 0:
        features.append(NAMES[tag.gender])
    if tag.hyph != 0:
        features.append(NAMES[tag.hyph])
    if tag.inf_form != 0:
        features.append(NAMES[tag.inf_form])
    if tag.mood != 0:
        features.append(NAMES[tag.mood])
    if tag.negative != 0:
        features.append(NAMES[tag.negative])
    if tag.number != 0:
        features.append(NAMES[tag.number])
    if tag.name_type != 0:
        features.append(NAMES[tag.name_type])
    if tag.noun_type != 0:
        features.append(NAMES[tag.noun_type])
    if tag.num_form != 0:
        features.append(NAMES[tag.num_form])
    if tag.num_type != 0:
        features.append(NAMES[tag.num_type])
    if tag.num_value != 0:
        features.append(NAMES[tag.num_value])
    if tag.part_form != 0:
        features.append(NAMES[tag.part_form])
    if tag.part_type != 0:
        features.append(NAMES[tag.part_type])
    if tag.person != 0:
        features.append(NAMES[tag.person])
    if tag.polite != 0:
        features.append(NAMES[tag.polite])
    if tag.polarity != 0:
        features.append(NAMES[tag.polarity])
    if tag.poss != 0:
        features.append(NAMES[tag.poss])
    if tag.prefix != 0:
        features.append(NAMES[tag.prefix])
    if tag.prep_case != 0:
        features.append(NAMES[tag.prep_case])
    if tag.pron_type != 0:
        features.append(NAMES[tag.pron_type])
    if tag.punct_side != 0:
        features.append(NAMES[tag.punct_side])
    if tag.punct_type != 0:
        features.append(NAMES[tag.punct_type])
    if tag.reflex != 0:
        features.append(NAMES[tag.reflex])
    if tag.style != 0:
        features.append(NAMES[tag.style])
    if tag.style_variant != 0:
        features.append(NAMES[tag.style_variant])
    if tag.tense != 0:
        features.append(NAMES[tag.tense])
    if tag.verb_form != 0:
        features.append(NAMES[tag.verb_form])
    if tag.voice != 0:
        features.append(NAMES[tag.voice])
    if tag.verb_type != 0:
        features.append(NAMES[tag.verb_type])
    return features

cdef RichTagC tag_from_json(json_tag):
    cdef RichTagC tag
    return tag
 
cdef int set_feature(RichTagC* tag, univ_morph_t feature, int value) except -1:
    if value == True:
        value_ = feature
    else:
        value_ = NIL
    if feature == NIL:
        pass
    elif is_abbr_feature(feature):
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
    elif is_noun_type_feature(feature):
        tag.noun_type = value_
    elif is_num_form_feature(feature):
        tag.num_form = value_
    elif is_num_type_feature(feature):
        tag.num_type = value_
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
        tag.punct_side = value_
    elif is_punct_type_feature(feature):
        tag.punct_type = value_
    elif is_reflex_feature(feature):
        tag.reflex = value_
    elif is_style_feature(feature):
        tag.style = value_
    elif is_style_variant_feature(feature):
        tag.style_variant = value_
    elif is_tense_feature(feature):
        tag.tense = value_
    elif is_typo_feature(feature):
        tag.typo = value_
    elif is_verb_form_feature(feature):
        tag.verb_form = value_
    elif is_voice_feature(feature):
        tag.voice = value_
    elif is_verb_type_feature(feature):
        tag.verb_type = value_
    else:
        raise ValueError("Unknown feature: %s (%d)" % (NAMES.get(feature), feature))

cdef int is_abbr_feature(univ_morph_t feature) nogil:
    return feature >= begin_Abbr  and feature <= end_Abbr

cdef int is_adp_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_AdpType and feature <= end_AdpType

cdef int is_adv_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_AdvType and feature <= end_AdvType

cdef int is_animacy_feature(univ_morph_t feature) nogil:
    return feature >= begin_Animacy and feature <= end_Animacy

cdef int is_aspect_feature(univ_morph_t feature) nogil:
    return feature >= begin_Aspect and feature <= end_Aspect

cdef int is_case_feature(univ_morph_t feature) nogil:
    return feature >= begin_Case and feature <= end_Case

cdef int is_conj_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_ConjType and feature <= end_ConjType

cdef int is_connegative_feature(univ_morph_t feature) nogil:
    return feature >= begin_Connegative and feature <= end_Connegative

cdef int is_definite_feature(univ_morph_t feature) nogil:
    return feature >= begin_Definite and feature <= end_Definite

cdef int is_degree_feature(univ_morph_t feature) nogil:
    return feature >= begin_Degree and feature <= end_Degree

cdef int is_derivation_feature(univ_morph_t feature) nogil:
    return feature >= begin_Derivation and feature <= end_Derivation

cdef int is_echo_feature(univ_morph_t feature) nogil:
    return feature >= begin_Echo and feature <= end_Echo

cdef int is_foreign_feature(univ_morph_t feature) nogil:
    return feature >= begin_Foreign and feature <= end_Foreign

cdef int is_gender_feature(univ_morph_t feature) nogil:
    return feature >= begin_Gender and feature <= end_Gender

cdef int is_hyph_feature(univ_morph_t feature) nogil:
    return feature >= begin_Hyph and feature <= end_Hyph

cdef int is_inf_form_feature(univ_morph_t feature) nogil:
    return feature >= begin_InfForm and feature <= end_InfForm

cdef int is_mood_feature(univ_morph_t feature) nogil:
    return feature >= begin_Mood and feature <= end_Mood

cdef int is_name_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_NameType and feature < end_NameType

cdef int is_negative_feature(univ_morph_t feature) nogil:
    return feature >= begin_Negative and feature <= end_Negative

cdef int is_noun_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_NounType and feature <= end_NounType

cdef int is_number_feature(univ_morph_t feature) nogil:
    return feature >= begin_Number and feature <= end_Number

cdef int is_num_form_feature(univ_morph_t feature) nogil:
    return feature >= begin_NumForm and feature <= end_NumForm

cdef int is_num_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_NumType and feature <= end_NumType

cdef int is_num_value_feature(univ_morph_t feature) nogil:
    return feature >= begin_NumValue and feature <= end_NumValue

cdef int is_part_form_feature(univ_morph_t feature) nogil:
    return feature >= begin_PartForm and feature <= end_PartForm

cdef int is_part_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_PartType and feature <= end_PartType

cdef int is_person_feature(univ_morph_t feature) nogil:
    return feature >= begin_Person and feature <= end_Person

cdef int is_polite_feature(univ_morph_t feature) nogil:
    return feature >= begin_Polite and feature <= end_Polite

cdef int is_polarity_feature(univ_morph_t feature) nogil:
    return feature >= begin_Polarity and feature <= end_Polarity

cdef int is_poss_feature(univ_morph_t feature) nogil:
    return feature >= begin_Poss and feature <= end_Poss

cdef int is_prefix_feature(univ_morph_t feature) nogil:
    return feature >= begin_Prefix and feature <= end_Prefix

cdef int is_prep_case_feature(univ_morph_t feature) nogil:
    return feature >= begin_PrepCase and feature <= end_PrepCase

cdef int is_pron_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_PronType and feature <= end_PronType

cdef int is_punct_side_feature(univ_morph_t feature) nogil:
    return feature >= begin_PunctSide and feature <= end_PunctSide

cdef int is_punct_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_PunctType and feature <= end_PunctType

cdef int is_reflex_feature(univ_morph_t feature) nogil:
    return feature >= begin_Reflex and feature <= end_Reflex

cdef int is_style_feature(univ_morph_t feature) nogil:
    return feature >= begin_Style and feature <= end_Style

cdef int is_style_variant_feature(univ_morph_t feature) nogil:
    return feature >= begin_StyleVariant and feature <= end_StyleVariant

cdef int is_tense_feature(univ_morph_t feature) nogil:
    return feature >= begin_Tense and feature <= end_Tense

cdef int is_typo_feature(univ_morph_t feature) nogil:
    return feature >= begin_Typo and feature <= end_Typo

cdef int is_verb_form_feature(univ_morph_t feature) nogil:
    return feature >= begin_VerbForm and feature <= end_VerbForm

cdef int is_voice_feature(univ_morph_t feature) nogil:
    return feature >= begin_Voice and feature <= end_Voice

cdef int is_verb_type_feature(univ_morph_t feature) nogil:
    return feature >= begin_VerbType and feature <= end_VerbType


FIELDS = {
    'Abbr': 0,
    'AdpType': 1,
    'AdvType': 2,
    'Animacy': 3,
    'Aspect': 4,
    'Case': 5,
    'ConjType': 6,
    'Connegative': 7,
    'Definite': 8,
    'Degree': 9,
    'Derivation': 10,
    'Echo': 11,
    'Foreign': 12,
    'Gender': 13,
    'Hyph': 14,
    'InfForm': 15,
    'Mood': 16,
    'NameType': 17,
    'Negative': 18,
    'Number': 19,
    'NumForm': 20,
    'NumType': 21,
    'NumValue': 22,
    'PartForm': 23,
    'PartType': 24,
    'Person': 25,
    'Polite': 26,
    'Polarity': 27,
    'Poss': 28,
    'Prefix': 29,
    'PrepCase': 30,
    'PronType': 31,
    'PunctSide': 32,
    'PunctType': 33,
    'Reflex': 34,
    'Style': 35,
    'StyleVariant': 36,
    'Tense': 37,
    'Typo': 38,
    'VerbForm': 39,
    'Voice': 40,
    'VerbType': 41
}

IDS = {
   "begin_Abbr": begin_Abbr,
   "Abbr_yes": Abbr_yes ,
   "end_Abbr": end_Abbr,
   "begin_AdpType": begin_AdpType,
   "AdpType_circ": AdpType_circ,
   "AdpType_comprep": AdpType_comprep,
   "AdpType_prep ": AdpType_prep ,
   "AdpType_post": AdpType_post,
   "AdpType_voc": AdpType_voc,
   "end_AdpType": end_AdpType,
   "begin_AdvType": begin_AdvType,
   "AdvType_adadj": AdvType_adadj,
   "AdvType_cau": AdvType_cau,
   "AdvType_deg": AdvType_deg,
   "AdvType_ex": AdvType_ex,
   "AdvType_loc": AdvType_loc,
   "AdvType_man": AdvType_man,
   "AdvType_mod": AdvType_mod,
   "AdvType_sta": AdvType_sta,
   "AdvType_tim": AdvType_tim,
   "end_AdvType": end_AdvType,
   "begin_Animacy": begin_Animacy,
   "Animacy_anim": Animacy_anim,
   "Animacy_hum": Animacy_hum,
   "Animacy_inan": Animacy_inan,
   "Animacy_nhum": Animacy_nhum,
   "end_Animacy": end_Animacy,
   "begin_Aspect": begin_Aspect,
   "Aspect_freq": Aspect_freq,
   "Aspect_imp": Aspect_imp,
   "Aspect_mod": Aspect_mod,
   "Aspect_none": Aspect_none,
   "Aspect_perf": Aspect_perf,
   "end_Aspect": end_Aspect,
   "begin_Case": begin_Case,
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
   "end_Case": end_Case,
   "begin_ConjType": begin_ConjType,
   "ConjType_comp ": ConjType_comp ,
   "ConjType_oper": ConjType_oper,
   "end_ConjType": end_ConjType,
   "begin_Connegative": begin_Connegative,
   "Connegative_yes": Connegative_yes,
   "end_Connegative": end_Connegative,
   "begin_Definite": begin_Definite,
   "Definite_cons": Definite_cons,
   "Definite_def": Definite_def,
   "Definite_ind": Definite_ind,
   "Definite_red": Definite_red,
   "Definite_two": Definite_two,
   "end_Definite": end_Definite,
   "begin_Degree": begin_Degree,
   "Degree_abs": Degree_abs,
   "Degree_cmp": Degree_cmp,
   "Degree_comp": Degree_comp,
   "Degree_none": Degree_none,
   "Degree_pos": Degree_pos,
   "Degree_sup": Degree_sup,
   "Degree_com": Degree_com,
   "Degree_dim": Degree_dim,
   "end_Degree": end_Degree,
   "begin_Derivation": begin_Derivation,
   "Derivation_minen": Derivation_minen,
   "Derivation_sti": Derivation_sti,
   "Derivation_inen": Derivation_inen,
   "Derivation_lainen": Derivation_lainen,
   "Derivation_ja": Derivation_ja,
   "Derivation_ton": Derivation_ton,
   "Derivation_vs": Derivation_vs,
   "Derivation_ttain": Derivation_ttain,
   "Derivation_ttaa": Derivation_ttaa,
   "end_Derivation": end_Derivation,
   "begin_Echo": begin_Echo,
   "Echo_rdp": Echo_rdp,
   "Echo_ech": Echo_ech,
   "end_Echo": end_Echo,
   "begin_Foreign": begin_Foreign,
   "Foreign_foreign": Foreign_foreign,
   "Foreign_fscript": Foreign_fscript,
   "Foreign_tscript": Foreign_tscript,
   "Foreign_yes": Foreign_yes,
   "end_Foreign": end_Foreign,
   "begin_Gender": begin_Gender,
   "Gender_com": Gender_com,
   "Gender_fem": Gender_fem,
   "Gender_masc": Gender_masc,
   "Gender_neut": Gender_neut,
   "Gender_dat_masc": Gender_dat_masc,
   "Gender_dat_fem": Gender_dat_fem,
   "Gender_erg_masc": Gender_erg_masc,
   "Gender_erg_fem": Gender_erg_fem,
   "Gender_psor_masc": Gender_psor_masc,
   "Gender_psor_fem": Gender_psor_fem,
   "Gender_psor_neut": Gender_psor_neut,
   "end_Gender": end_Gender,
   "begin_Hyph": begin_Hyph,
   "Hyph_yes": Hyph_yes,
   "end_Hyph": end_Hyph,
   "begin_InfForm": begin_InfForm,
   "InfForm_one": InfForm_one,
   "InfForm_two": InfForm_two,
   "InfForm_three": InfForm_three,
   "end_InfForm": end_InfForm,
   "begin_Mood": begin_Mood,
   "Mood_cnd": Mood_cnd,
   "Mood_imp": Mood_imp,
   "Mood_ind": Mood_ind,
   "Mood_n": Mood_n,
   "Mood_pot": Mood_pot,
   "Mood_sub": Mood_sub,
   "Mood_opt": Mood_opt,
   "end_Mood": end_Mood,
   "begin_NameType": begin_NameType,
   "NameType_geo": NameType_geo,
   "NameType_prs": NameType_prs,
   "NameType_giv": NameType_giv,
   "NameType_sur": NameType_sur,
   "NameType_nat": NameType_nat,
   "NameType_com": NameType_com,
   "NameType_pro": NameType_pro,
   "NameType_oth": NameType_oth,
   "end_NameType": end_NameType,
   "begin_Negative": begin_Negative,
   "Negative_neg": Negative_neg,
   "Negative_pos": Negative_pos,
   "Negative_yes": Negative_yes,
   "end_Negative": end_Negative,
   "begin_NounType": begin_NounType,
   "NounType_com": NounType_com,
   "NounType_prop": NounType_prop,
   "NounType_class": NounType_class,
   "end_NounType": end_NounType,
   "begin_Number": begin_Number,
   "Number_com": Number_com,
   "Number_dual": Number_dual,
   "Number_none": Number_none,
   "Number_plur": Number_plur,
   "Number_sing": Number_sing,
   "Number_ptan": Number_ptan,
   "Number_count": Number_count,
   "Number_abs_sing": Number_abs_sing,
   "Number_abs_plur": Number_abs_plur,
   "Number_dat_sing": Number_dat_sing,
   "Number_dat_plur": Number_dat_plur,
   "Number_erg_sing": Number_erg_sing,
   "Number_erg_plur": Number_erg_plur,
   "Number_psee_sing": Number_psee_sing,
   "Number_psee_plur": Number_psee_plur,
   "Number_psor_sing": Number_psor_sing,
   "Number_psor_plur": Number_psor_plur,
   "end_Number": end_Number,
   "begin_NumForm": begin_NumForm,
   "NumForm_digit": NumForm_digit,
   "NumForm_roman": NumForm_roman,
   "NumForm_word": NumForm_word,
   "end_NumForm": end_NumForm,
   "begin_NumType": begin_NumType,
   "NumType_card": NumType_card,
   "NumType_dist": NumType_dist,
   "NumType_frac": NumType_frac,
   "NumType_gen": NumType_gen,
   "NumType_mult": NumType_mult,
   "NumType_none": NumType_none,
   "NumType_ord": NumType_ord,
   "NumType_sets": NumType_sets,
   "end_NumType": end_NumType,
   "begin_NumValue": begin_NumValue,
   "NumValue_one": NumValue_one,
   "NumValue_two": NumValue_two,
   "NumValue_three": NumValue_three,
   "end_NumValue": end_NumValue,
   "begin_PartForm": begin_PartForm,
   "PartForm_pres": PartForm_pres,
   "PartForm_past": PartForm_past,
   "PartForm_agt": PartForm_agt,
   "PartForm_neg": PartForm_neg,
   "end_PartForm": end_PartForm,
   "begin_PartType": begin_PartType,
   "PartType_mod": PartType_mod,
   "PartType_emp": PartType_emp,
   "PartType_res": PartType_res,
   "PartType_inf": PartType_inf,
   "PartType_vbp": PartType_vbp,
   "end_PartType": end_PartType,

   "begin_Person": begin_Person,
   "Person_one": Person_one,
   "Person_two": Person_two,
   "Person_three": Person_three,
   "Person_none": Person_none,
   "Person_abs_one": Person_abs_one,
   "Person_abs_two": Person_abs_two,
   "Person_abs_three": Person_abs_three,
   "Person_dat_one": Person_dat_one,
   "Person_dat_two": Person_dat_two,
   "Person_dat_three": Person_dat_three,
   "Person_erg_one": Person_erg_one,
   "Person_erg_two": Person_erg_two,
   "Person_erg_three": Person_erg_three,
   "Person_psor_one": Person_psor_one,
   "Person_psor_two": Person_psor_two,
   "Person_psor_three": Person_psor_three,
   "end_Person": end_Person,
   "begin_Polarity": begin_Polarity,
   "Polarity_neg": Polarity_neg,
   "Polarity_pos": Polarity_pos,
   "end_Polarity": end_Polarity,
   "begin_Polite": begin_Polite,
   "Polite_inf": Polite_inf,
   "Polite_pol": Polite_pol,
   "Polite_abs_inf": Polite_abs_inf,
   "Polite_abs_pol": Polite_abs_pol,
   "Polite_erg_inf": Polite_erg_inf,
   "Polite_erg_pol": Polite_erg_pol,
   "Polite_dat_inf": Polite_dat_inf,
   "Polite_dat_pol": Polite_dat_pol,
   "end_Polite": end_Polite,
   "begin_Poss": begin_Poss,
   "Poss_yes": Poss_yes,
   "end_Poss": end_Poss,
   "begin_Prefix": begin_Prefix,
   "Prefix_yes": Prefix_yes,
   "end_Prefix": end_Prefix,
   "begin_PrepCase": begin_PrepCase,
   "PrepCase_npr": PrepCase_npr,
   "PrepCase_pre": PrepCase_pre,
   "end_PrepCase": end_PrepCase,
   "begin_PronType": begin_PronType,
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
   "PronType_exc": PronType_exc,
   "end_PronType": end_PronType,
   "begin_PunctSide": begin_PunctSide,
   "PunctSide_ini": PunctSide_ini,
   "PunctSide_fin": PunctSide_fin,
   "end_PunctSide": end_PunctSide,
   "begin_PunctType": begin_PunctType,
   "PunctType_peri": PunctType_peri,
   "PunctType_qest": PunctType_qest,
   "PunctType_excl": PunctType_excl,
   "PunctType_quot": PunctType_quot,
   "PunctType_brck": PunctType_brck,
   "PunctType_comm": PunctType_comm,
   "PunctType_colo": PunctType_colo,
   "PunctType_semi": PunctType_semi,
   "PunctType_dash": PunctType_dash,
   "end_PunctType": end_PunctType,
   "begin_Reflex": begin_Reflex,
   "Reflex_yes": Reflex_yes,
   "end_Reflex": end_Reflex,
   "begin_Style": begin_Style,
   "Style_arch": Style_arch,
   "Style_rare": Style_rare,
   "Style_poet": Style_poet,
   "Style_norm": Style_norm,
   "Style_coll": Style_coll,
   "Style_vrnc": Style_vrnc,
   "Style_sing": Style_sing,
   "Style_expr": Style_expr,
   "Style_derg": Style_derg,
   "Style_vulg": Style_vulg,
   "Style_yes": Style_yes,
   "end_Style": end_Style,
   "begin_StyleVariant": begin_StyleVariant,
   "StyleVariant_styleShort": StyleVariant_styleShort,
   "StyleVariant_styleBound": StyleVariant_styleBound,
   "end_StyleVariant": end_StyleVariant,
   "begin_Tense": begin_Tense,
   "Tense_fut": Tense_fut,
   "Tense_imp": Tense_imp,
   "Tense_past": Tense_past,
   "Tense_pres": Tense_pres,
   "end_Tense": end_Tense,
   "begin_Typo": begin_Typo,
   "Typo_yes": Typo_yes,
   "end_Typo": end_Typo,
   "begin_VerbForm": begin_VerbForm,
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
   "VerbForm_conv": VerbForm_conv,
   "VerbForm_gdv": VerbForm_gdv,
   "end_VerbForm": end_VerbForm,
   "begin_VerbType": begin_VerbType,
   "VerbType_aux": VerbType_aux,
   "VerbType_cop": VerbType_cop,
   "VerbType_mod": VerbType_mod,
   "VerbType_light": VerbType_light,
   "end_VerbType": end_VerbType,
   "begin_Voice": begin_Voice,
   "Voice_act": Voice_act,
   "Voice_cau": Voice_cau,
   "Voice_pass": Voice_pass,
   "Voice_mid": Voice_mid,
   "Voice_int": Voice_int,
   "end_Voice": end_Voice,
}


FIELD_SIZES = [get_field_size(field) for field in FIELDS]

NAMES = {value: key for key, value in IDS.items()}
# Unfortunate hack here, to work around problem with long cpdef enum
# (which is generating an enormous amount of C++ in Cython 0.24+)
# We keep the enum cdef, and just make sure the names are available to Python
locals().update(IDS)
