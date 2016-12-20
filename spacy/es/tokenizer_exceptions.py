# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA


TOKENIZER_EXCEPTIONS = {
    "accidentarse": [
        {ORTH: "accidentar", LEMMA: "accidentar", POS: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "aceptarlo": [
        {ORTH: "aceptar", LEMMA: "aceptar", POS: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "acompañarla": [
        {ORTH: "acompañar", LEMMA: "acompañar", POS: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "advertirle": [
        {ORTH: "advertir", LEMMA: "advertir", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "al": [
        {ORTH: "a", LEMMA: "a", POS: ADP},
        {ORTH: "el", LEMMA: "el", POS: DET}
    ],

    "anunciarnos": [
        {ORTH: "anunciar", LEMMA: "anunciar", POS: AUX},
        {ORTH: "nos", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "asegurándole": [
        {ORTH: "asegurando", LEMMA: "asegurar", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "considerarle": [
        {ORTH: "considerar", LEMMA: "considerar", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "decirle": [
        {ORTH: "decir", LEMMA: "decir", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "decirles": [
        {ORTH: "decir", LEMMA: "decir", POS: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "decirte": [
        {ORTH: "Decir", LEMMA: "decir", POS: AUX},
        {ORTH: "te", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "dejarla": [
        {ORTH: "dejar", LEMMA: "dejar", POS: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "dejarnos": [
        {ORTH: "dejar", LEMMA: "dejar", POS: AUX},
        {ORTH: "nos", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "dejándole": [
        {ORTH: "dejando", LEMMA: "dejar", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "del": [
        {ORTH: "de", LEMMA: "de", POS: ADP},
        {ORTH: "el", LEMMA: "el", POS: DET}
    ],

    "demostrarles": [
        {ORTH: "demostrar", LEMMA: "demostrar", POS: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "diciéndole": [
        {ORTH: "diciendo", LEMMA: "decir", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "diciéndoles": [
        {ORTH: "diciendo", LEMMA: "decir", POS: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "diferenciarse": [
        {ORTH: "diferenciar", LEMMA: "diferenciar", POS: AUX},
        {ORTH: "se", LEMMA: "él", POS: PRON}
    ],

    "divirtiéndome": [
        {ORTH: "divirtiendo", LEMMA: "divertir", POS: AUX},
        {ORTH: "me", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "ensanchándose": [
        {ORTH: "ensanchando", LEMMA: "ensanchar", POS: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "explicarles": [
        {ORTH: "explicar", LEMMA: "explicar", POS: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "haberla": [
        {ORTH: "haber", LEMMA: "haber", POS: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "haberlas": [
        {ORTH: "haber", LEMMA: "haber", POS: AUX},
        {ORTH: "las", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "haberlo": [
        {ORTH: "haber", LEMMA: "haber", POS: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "haberlos": [
        {ORTH: "haber", LEMMA: "haber", POS: AUX},
        {ORTH: "los", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "haberme": [
        {ORTH: "haber", LEMMA: "haber", POS: AUX},
        {ORTH: "me", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "haberse": [
        {ORTH: "haber", LEMMA: "haber", POS: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "hacerle": [
        {ORTH: "hacer", LEMMA: "hacer", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "hacerles": [
        {ORTH: "hacer", LEMMA: "hacer", POS: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "hallarse": [
        {ORTH: "hallar", LEMMA: "hallar", POS: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "imaginaros": [
        {ORTH: "imaginar", LEMMA: "imaginar", POS: AUX},
        {ORTH: "os", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "insinuarle": [
        {ORTH: "insinuar", LEMMA: "insinuar", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "justificarla": [
        {ORTH: "justificar", LEMMA: "justificar", POS: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "mantenerlas": [
        {ORTH: "mantener", LEMMA: "mantener", POS: AUX},
        {ORTH: "las", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "mantenerlos": [
        {ORTH: "mantener", LEMMA: "mantener", POS: AUX},
        {ORTH: "los", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "mantenerme": [
        {ORTH: "mantener", LEMMA: "mantener", POS: AUX},
        {ORTH: "me", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "pasarte": [
        {ORTH: "pasar", LEMMA: "pasar", POS: AUX},
        {ORTH: "te", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "pedirle": [
        {ORTH: "pedir", LEMMA: "pedir", POS: AUX},
        {ORTH: "le", LEMMA: "él", POS: PRON}
    ],

    "pel": [
        {ORTH: "per", LEMMA: "per", POS: ADP},
        {ORTH: "el", LEMMA: "el", POS: DET}
    ],

    "pidiéndonos": [
        {ORTH: "pidiendo", LEMMA: "pedir", POS: AUX},
        {ORTH: "nos", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "poderle": [
        {ORTH: "poder", LEMMA: "poder", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "preguntarse": [
        {ORTH: "preguntar", LEMMA: "preguntar", POS: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "preguntándose": [
        {ORTH: "preguntando", LEMMA: "preguntar", POS: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "presentarla": [
        {ORTH: "presentar", LEMMA: "presentar", POS: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "pudiéndolo": [
        {ORTH: "pudiendo", LEMMA: "poder", POS: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "pudiéndose": [
        {ORTH: "pudiendo", LEMMA: "poder", POS: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "quererle": [
        {ORTH: "querer", LEMMA: "querer", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "rasgarse": [
        {ORTH: "Rasgar", LEMMA: "rasgar", POS: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "repetirlo": [
        {ORTH: "repetir", LEMMA: "repetir", POS: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "robarle": [
        {ORTH: "robar", LEMMA: "robar", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "seguirlos": [
        {ORTH: "seguir", LEMMA: "seguir", POS: AUX},
        {ORTH: "los", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "serle": [
        {ORTH: "ser", LEMMA: "ser", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "serlo": [
        {ORTH: "ser", LEMMA: "ser", POS: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "señalándole": [
        {ORTH: "señalando", LEMMA: "señalar", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "suplicarle": [
        {ORTH: "suplicar", LEMMA: "suplicar", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "tenerlos": [
        {ORTH: "tener", LEMMA: "tener", POS: AUX},
        {ORTH: "los", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "vengarse": [
        {ORTH: "vengar", LEMMA: "vengar", POS: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "verla": [
        {ORTH: "ver", LEMMA: "ver", POS: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "verle": [
        {ORTH: "ver", LEMMA: "ver", POS: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, POS: PRON}
    ],

    "volverlo": [
        {ORTH: "volver", LEMMA: "volver", POS: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, POS: PRON}
    ]
}


ORTH_ONLY = [

]
