# cython: infer_types
# coding: utf8
from __future__ import unicode_literals

from libc.string cimport memset
import srsly
from collections import Counter

from .compat import basestring_
from .strings import get_string_id
from . import symbols
from .attrs cimport POS, IS_SPACE
from .attrs import LEMMA, intify_attrs
from .parts_of_speech cimport SPACE
from .parts_of_speech import IDS as POS_IDS
from .lexeme cimport Lexeme
from .errors import Errors
from .util import ensure_path


cdef enum univ_field_t:
    Field_POS
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
    Field_Polarity
    Field_Polite
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
    Field_VerbType
    Field_Voice


def _normalize_props(props):
    """Transform deprecated string keys to correct names."""
    out = {}
    props = dict(props)
    for key in FIELDS:
        if key in props:
            value = str(props[key]).lower()
            # We don't have support for disjunctive int|rel features, so
            # just take the first one :(
            if "|" in value:
                value = value.split("|")[0]
            attr = '%s_%s' % (key, value)
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
        elif value is True:
            out[key] = value
        elif key.lower() == 'pos':
            out[POS] = POS_IDS[value.upper()]
        elif key.lower() != 'morph':
            out[key] = value
    return out


class MorphologyClassMap(object):
    def __init__(self, features):
        self.features = tuple(features)
        self.fields = []
        self.feat2field = {}
        seen_fields = set()
        for feature in features:
            field = feature.split("_", 1)[0]
            if field not in seen_fields:
                self.fields.append(field)
                seen_fields.add(field)
            self.feat2field[feature] = FIELDS[field]
        self.id2feat = {get_string_id(name): name for name in features}
        self.field2feats = {"POS": []}
        self.col2info = []
        self.attr2field = dict(LOWER_FIELDS.items())
        self.feat2offset = {}
        self.field2col = {}
        self.field2id = dict(FIELDS.items())
        self.fieldid2field = {field_id: field for field, field_id in FIELDS.items()}
        for feature in features:
            field = self.fields[self.feat2field[feature]]
            if field not in self.field2col:
                self.field2col[field] = len(self.col2info)
            if field != "POS" and field not in self.field2feats:
                self.col2info.append((field, 0, "NIL"))
            self.field2feats.setdefault(field, ["NIL"])
            offset = len(self.field2feats[field])
            self.field2feats[field].append(feature)
            self.col2info.append((field, offset, feature))
            self.feat2offset[feature] = offset

    @property
    def field_sizes(self):
        return [len(self.field2feats[field]) for field in self.fields]

    def get_field_offset(self, field):
        return self.field2col[field]


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
        self._feat_map = MorphologyClassMap(FEATURES)
        self.load_tag_map(tag_map)
        self.lemmatizer = lemmatizer

        self._cache = PreshMapArray(self.n_tags)
        self.exc = {}
        if exc is not None:
            for (tag, orth), attrs in exc.items():
                attrs = _normalize_props(attrs)
                self.add_special_case(
                    self.strings.as_string(tag), self.strings.as_string(orth), attrs)

    def load_tag_map(self, tag_map):
        # Add special space symbol. We prefix with underscore, to make sure it
        # always sorts to the end.
        if '_SP' in tag_map:
            space_attrs = tag_map.get('_SP')
        else:
            space_attrs = tag_map.get('SP', {POS: SPACE})
        if '_SP' not in tag_map:
            self.strings.add('_SP')
            tag_map = dict(tag_map)
            tag_map['_SP'] = space_attrs
        self.tag_map = {}
        self.reverse_index = {}
        for i, (tag_str, attrs) in enumerate(sorted(tag_map.items())):
            attrs = _normalize_props(attrs)
            self.add({self._feat_map.id2feat[feat] for feat in attrs
                      if feat in self._feat_map.id2feat})
            self.tag_map[tag_str] = dict(attrs)
            self.reverse_index[self.strings.add(tag_str)] = i
        self.tag_names = tuple(sorted(self.tag_map.keys()))
        self.n_tags = len(self.tag_map)
        self._cache = PreshMapArray(self.n_tags)

    def __reduce__(self):
        return (Morphology, (self.strings, self.tag_map, self.lemmatizer,
                self.exc), None, None)

    def add(self, features):
        """Insert a morphological analysis in the morphology table, if not already
        present. Returns the hash of the new analysis.
        """
        for f in features:
            if isinstance(f, basestring_):
                self.strings.add(f)
        string_features = features
        features = intify_features(features)
        cdef attr_t feature
        for feature in features:
            if feature != 0 and feature not in self._feat_map.id2feat:
                raise ValueError(Errors.E167.format(feat=self.strings[feature], feat_id=feature))
        cdef MorphAnalysisC tag
        tag = create_rich_tag(features)
        cdef hash_t key = self.insert(tag)
        return key

    def get(self, hash_t morph):
        tag = <MorphAnalysisC*>self.tags.get(morph)
        if tag == NULL:
            return []
        else:
            return tag_to_json(tag)

    cpdef update(self, hash_t morph, features):
        """Update a morphological analysis with new feature values."""
        tag = (<MorphAnalysisC*>self.tags.get(morph))[0]
        features = intify_features(features)
        cdef attr_t feature
        for feature in features:
            field = FEATURE_FIELDS[FEATURE_NAMES[feature]]
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
        self.add({self._feat_map.id2feat[feat] for feat in attrs
                 if feat in self._feat_map.id2feat})
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
            lemma = self.lemmatizer.lookup(orth_str, orth=token.lex.orth)
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
        token.morph = self.add(features)
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

    @classmethod
    def create_class_map(cls):
        return MorphologyClassMap(FEATURES)


cpdef univ_pos_t get_int_tag(pos_):
    return <univ_pos_t>0

cpdef intify_features(features):
    return {get_string_id(feature) for feature in features}

cdef hash_t hash_tag(MorphAnalysisC tag) nogil:
    return mrmr.hash64(&tag, sizeof(tag), 0)


cdef MorphAnalysisC create_rich_tag(features) except *:
    cdef MorphAnalysisC tag
    cdef attr_t feature
    memset(&tag, 0, sizeof(tag))
    for feature in features:
        field = FEATURE_FIELDS[FEATURE_NAMES[feature]]
        set_feature(&tag, field, feature, 1)
    return tag


cdef tag_to_json(const MorphAnalysisC* tag):
    return [FEATURE_NAMES[f] for f in list_features(tag)]


cdef MorphAnalysisC tag_from_json(json_tag):
    raise NotImplementedError


cdef list list_features(const MorphAnalysisC* tag):
    output = []
    if tag.abbr != 0:
        output.append(tag.abbr)
    if tag.adp_type != 0:
        output.append(tag.adp_type)
    if tag.adv_type != 0:
        output.append(tag.adv_type)
    if tag.animacy != 0:
        output.append(tag.animacy)
    if tag.aspect != 0:
        output.append(tag.aspect)
    if tag.case != 0:
        output.append(tag.case)
    if tag.conj_type != 0:
        output.append(tag.conj_type)
    if tag.connegative != 0:
        output.append(tag.connegative)
    if tag.definite != 0:
        output.append(tag.definite)
    if tag.degree != 0:
        output.append(tag.degree)
    if tag.derivation != 0:
        output.append(tag.derivation)
    if tag.echo != 0:
        output.append(tag.echo)
    if tag.foreign != 0:
        output.append(tag.foreign)
    if tag.gender != 0:
        output.append(tag.gender)
    if tag.hyph != 0:
        output.append(tag.hyph)
    if tag.inf_form != 0:
        output.append(tag.inf_form)
    if tag.mood != 0:
        output.append(tag.mood)
    if tag.negative != 0:
        output.append(tag.negative)
    if tag.number != 0:
        output.append(tag.number)
    if tag.name_type != 0:
        output.append(tag.name_type)
    if tag.noun_type != 0:
        output.append(tag.noun_type)
    if tag.part_form != 0:
        output.append(tag.part_form)
    if tag.part_type != 0:
        output.append(tag.part_type)
    if tag.person != 0:
        output.append(tag.person)
    if tag.polite != 0:
        output.append(tag.polite)
    if tag.polarity != 0:
        output.append(tag.polarity)
    if tag.poss != 0:
        output.append(tag.poss)
    if tag.prefix != 0:
        output.append(tag.prefix)
    if tag.prep_case != 0:
        output.append(tag.prep_case)
    if tag.pron_type != 0:
        output.append(tag.pron_type)
    if tag.punct_type != 0:
        output.append(tag.punct_type)
    if tag.reflex != 0:
        output.append(tag.reflex)
    if tag.style != 0:
        output.append(tag.style)
    if tag.style_variant != 0:
        output.append(tag.style_variant)
    if tag.typo != 0:
        output.append(tag.typo)
    if tag.verb_form != 0:
        output.append(tag.verb_form)
    if tag.voice != 0:
        output.append(tag.voice)
    if tag.verb_type != 0:
        output.append(tag.verb_type)
    return output


cdef attr_t get_field(const MorphAnalysisC* tag, int field_id) nogil:
    field = <univ_field_t>field_id
    if field == Field_POS:
        return tag.pos
    if field == Field_Abbr:
        return tag.abbr
    elif field == Field_AdpType:
        return tag.adp_type
    elif field == Field_AdvType:
        return tag.adv_type
    elif field == Field_Animacy:
        return tag.animacy
    elif field == Field_Aspect:
        return tag.aspect
    elif field == Field_Case:
        return tag.case
    elif field == Field_ConjType:
        return tag.conj_type
    elif field == Field_Connegative:
        return tag.connegative
    elif field == Field_Definite:
        return tag.definite
    elif field == Field_Degree:
        return tag.degree
    elif field == Field_Derivation:
        return tag.derivation
    elif field == Field_Echo:
        return tag.echo
    elif field == Field_Foreign:
        return tag.foreign
    elif field == Field_Gender:
        return tag.gender
    elif field == Field_Hyph:
        return tag.hyph
    elif field == Field_InfForm:
        return tag.inf_form
    elif field == Field_Mood:
        return tag.mood
    elif field == Field_Negative:
        return tag.negative
    elif field == Field_Number:
        return tag.number
    elif field == Field_NameType:
        return tag.name_type
    elif field == Field_NounType:
        return tag.noun_type
    elif field == Field_NumForm:
        return tag.num_form
    elif field == Field_NumType:
        return tag.num_type
    elif field == Field_NumValue:
        return tag.num_value
    elif field == Field_PartForm:
        return tag.part_form
    elif field == Field_PartType:
        return tag.part_type
    elif field == Field_Person:
        return tag.person
    elif field == Field_Polite:
        return tag.polite
    elif field == Field_Polarity:
        return tag.polarity
    elif field == Field_Poss:
        return tag.poss
    elif field == Field_Prefix:
        return tag.prefix
    elif field == Field_PrepCase:
        return tag.prep_case
    elif field == Field_PronType:
        return tag.pron_type
    elif field == Field_PunctSide:
        return tag.punct_side
    elif field == Field_PunctType:
        return tag.punct_type
    elif field == Field_Reflex:
        return tag.reflex
    elif field == Field_Style:
        return tag.style
    elif field == Field_StyleVariant:
        return tag.style_variant
    elif field == Field_Tense:
        return tag.tense
    elif field == Field_Typo:
        return tag.typo
    elif field == Field_VerbForm:
        return tag.verb_form
    elif field == Field_Voice:
        return tag.voice
    elif field == Field_VerbType:
        return tag.verb_type
    else:
        raise ValueError(Errors.E168.format(field=field_id))


cdef int check_feature(const MorphAnalysisC* tag, attr_t feature) nogil:
    if tag.abbr == feature:
        return 1
    elif tag.adp_type == feature:
        return 1
    elif tag.adv_type == feature:
        return 1
    elif tag.animacy == feature:
        return 1
    elif tag.aspect == feature:
        return 1
    elif tag.case == feature:
        return 1
    elif tag.conj_type == feature:
        return 1
    elif tag.connegative == feature:
        return 1
    elif tag.definite == feature:
        return 1
    elif tag.degree == feature:
        return 1
    elif tag.derivation == feature:
        return 1
    elif tag.echo == feature:
        return 1
    elif tag.foreign == feature:
        return 1
    elif tag.gender == feature:
        return 1
    elif tag.hyph == feature:
        return 1
    elif tag.inf_form == feature:
        return 1
    elif tag.mood == feature:
        return 1
    elif tag.negative == feature:
        return 1
    elif tag.number == feature:
        return 1
    elif tag.name_type == feature:
        return 1
    elif tag.noun_type == feature:
        return 1
    elif tag.num_form == feature:
        return 1
    elif tag.num_type == feature:
        return 1
    elif tag.num_value == feature:
        return 1
    elif tag.part_form == feature:
        return 1
    elif tag.part_type == feature:
        return 1
    elif tag.person == feature:
        return 1
    elif tag.polite == feature:
        return 1
    elif tag.polarity == feature:
        return 1
    elif tag.poss == feature:
        return 1
    elif tag.prefix == feature:
        return 1
    elif tag.prep_case == feature:
        return 1
    elif tag.pron_type == feature:
        return 1
    elif tag.punct_side == feature:
        return 1
    elif tag.punct_type == feature:
        return 1
    elif tag.reflex == feature:
        return 1
    elif tag.style == feature:
        return 1
    elif tag.style_variant == feature:
        return 1
    elif tag.tense == feature:
        return 1
    elif tag.typo == feature:
        return 1
    elif tag.verb_form == feature:
        return 1
    elif tag.voice == feature:
        return 1
    elif tag.verb_type == feature:
        return 1
    else:
        return 0

cdef int set_feature(MorphAnalysisC* tag,
        univ_field_t field, attr_t feature, int value) except -1:
    if value == True:
        value_ = feature
    else:
        value_ = 0
    prev_value = get_field(tag, field)
    if prev_value != 0 and value_ == 0 and field != Field_POS:
        tag.length -= 1
    elif prev_value == 0 and value_ != 0 and field != Field_POS:
        tag.length += 1
    if feature == 0:
        pass
    elif field == Field_POS:
        tag.pos = get_string_id(FEATURE_NAMES[value_].split('_')[1])
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
        raise ValueError(Errors.E167.format(field=FEATURE_NAMES.get(feature), field_id=feature))


FIELDS = {
    'POS': Field_POS,
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
    'VerbType': Field_VerbType,
    'Voice': Field_Voice,
}

LOWER_FIELDS = {
    'pos': Field_POS,
    'abbr': Field_Abbr,
    'adp_type': Field_AdpType,
    'adv_type': Field_AdvType,
    'animacy': Field_Animacy,
    'aspect': Field_Aspect,
    'case': Field_Case,
    'conj_type': Field_ConjType,
    'connegative': Field_Connegative,
    'definite': Field_Definite,
    'degree': Field_Degree,
    'derivation': Field_Derivation,
    'echo': Field_Echo,
    'foreign': Field_Foreign,
    'gender': Field_Gender,
    'hyph': Field_Hyph,
    'inf_form': Field_InfForm,
    'mood': Field_Mood,
    'name_type': Field_NameType,
    'negative': Field_Negative,
    'noun_type': Field_NounType,
    'number': Field_Number,
    'num_form': Field_NumForm,
    'num_type': Field_NumType,
    'num_value': Field_NumValue,
    'part_form': Field_PartForm,
    'part_type': Field_PartType,
    'person': Field_Person,
    'polarity': Field_Polarity,
    'polite': Field_Polite,
    'poss': Field_Poss,
    'prefix': Field_Prefix,
    'prep_case': Field_PrepCase,
    'pron_type': Field_PronType,
    'punct_side': Field_PunctSide,
    'punct_type': Field_PunctType,
    'reflex': Field_Reflex,
    'style': Field_Style,
    'style_variant': Field_StyleVariant,
    'tense': Field_Tense,
    'typo': Field_Typo,
    'verb_form': Field_VerbForm,
    'verb_type': Field_VerbType,
    'voice': Field_Voice,
}


FEATURES = [
   "POS_ADJ",
   "POS_ADP",
   "POS_ADV",
   "POS_AUX",
   "POS_CONJ",
   "POS_CCONJ",
   "POS_DET",
   "POS_INTJ",
   "POS_NOUN",
   "POS_NUM",
   "POS_PART",
   "POS_PRON",
   "POS_PROPN",
   "POS_PUNCT",
   "POS_SCONJ",
   "POS_SYM",
   "POS_VERB",
   "POS_X",
   "POS_EOL",
   "POS_SPACE",
   "Abbr_yes",
   "AdpType_circ",
   "AdpType_comprep",
   "AdpType_prep",
   "AdpType_post",
   "AdpType_voc",
   "AdvType_adadj",
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
   "Aspect_hab",
   "Aspect_imp",
   "Aspect_iter",
   "Aspect_perf",
   "Aspect_prog",
   "Aspect_prosp",
   "Aspect_none",
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
   "NumForm_combi",
   "NumType_card",
   "NumType_dist",
   "NumType_frac",
   "NumType_gen",
   "NumType_mult",
   "NumType_none",
   "NumType_ord",
   "NumType_sets",
   "NumType_dual",
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

FEATURE_NAMES = {get_string_id(f): f for f in FEATURES}
FEATURE_FIELDS = {f: FIELDS[f.split('_', 1)[0]] for f in FEATURES}
