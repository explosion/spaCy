# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups

# Lemma data source:
# http://st2.zargan.com/duyuru/Zargan_Linguistic_Resources_for_Turkish.html - Bilgin, O. (2016). Biçimbilimsel Bakımdan Karmaşık Türkçe Kelimelerin İşlenmesinde Frekans Etkileri (yayınlanmamış yüksek lisans tezi). Boğaziçi Üniversitesi, İstanbul. Erişim: http://st2.zargan.com/public/resources/turkish/frequency_effects_in_turkish.pdf


class TurkishDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "tr"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    resources = {"lemma_lookup": "lemma_lookup.json"}


class Turkish(Language):
    lang = "tr"
    Defaults = TurkishDefaults


__all__ = ["Turkish"]
