# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA


TOKENIZER_EXCEPTIONS = {
    "accidentarse": [
        {ORTH: "accidentar", LEMMA: "accidentar", TAG: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "aceptarlo": [
        {ORTH: "aceptar", LEMMA: "aceptar", TAG: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "acompañarla": [
        {ORTH: "acompañar", LEMMA: "acompañar", TAG: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "advertirle": [
        {ORTH: "advertir", LEMMA: "advertir", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "al": [
        {ORTH: "a", LEMMA: "a", TAG: ADP},
        {ORTH: "el", LEMMA: "el", TAG: DET}
    ],

    "anunciarnos": [
        {ORTH: "anunciar", LEMMA: "anunciar", TAG: AUX},
        {ORTH: "nos", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "asegurándole": [
        {ORTH: "asegurando", LEMMA: "asegurar", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "considerarle": [
        {ORTH: "considerar", LEMMA: "considerar", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "decirle": [
        {ORTH: "decir", LEMMA: "decir", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "decirles": [
        {ORTH: "decir", LEMMA: "decir", TAG: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "decirte": [
        {ORTH: "Decir", LEMMA: "decir", TAG: AUX},
        {ORTH: "te", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "dejarla": [
        {ORTH: "dejar", LEMMA: "dejar", TAG: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "dejarnos": [
        {ORTH: "dejar", LEMMA: "dejar", TAG: AUX},
        {ORTH: "nos", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "dejándole": [
        {ORTH: "dejando", LEMMA: "dejar", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "del": [
        {ORTH: "de", LEMMA: "de", TAG: ADP},
        {ORTH: "el", LEMMA: "el", TAG: DET}
    ],

    "demostrarles": [
        {ORTH: "demostrar", LEMMA: "demostrar", TAG: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "diciéndole": [
        {ORTH: "diciendo", LEMMA: "decir", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "diciéndoles": [
        {ORTH: "diciendo", LEMMA: "decir", TAG: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "diferenciarse": [
        {ORTH: "diferenciar", LEMMA: "diferenciar", TAG: AUX},
        {ORTH: "se", LEMMA: "él", TAG: "PRON"}
    ],

    "divirtiéndome": [
        {ORTH: "divirtiendo", LEMMA: "divertir", TAG: AUX},
        {ORTH: "me", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "ensanchándose": [
        {ORTH: "ensanchando", LEMMA: "ensanchar", TAG: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "explicarles": [
        {ORTH: "explicar", LEMMA: "explicar", TAG: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "haberla": [
        {ORTH: "haber", LEMMA: "haber", TAG: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "haberlas": [
        {ORTH: "haber", LEMMA: "haber", TAG: AUX},
        {ORTH: "las", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "haberlo": [
        {ORTH: "haber", LEMMA: "haber", TAG: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "haberlos": [
        {ORTH: "haber", LEMMA: "haber", TAG: AUX},
        {ORTH: "los", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "haberme": [
        {ORTH: "haber", LEMMA: "haber", TAG: AUX},
        {ORTH: "me", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "haberse": [
        {ORTH: "haber", LEMMA: "haber", TAG: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "hacerle": [
        {ORTH: "hacer", LEMMA: "hacer", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "hacerles": [
        {ORTH: "hacer", LEMMA: "hacer", TAG: AUX},
        {ORTH: "les", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "hallarse": [
        {ORTH: "hallar", LEMMA: "hallar", TAG: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "imaginaros": [
        {ORTH: "imaginar", LEMMA: "imaginar", TAG: AUX},
        {ORTH: "os", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "insinuarle": [
        {ORTH: "insinuar", LEMMA: "insinuar", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "justificarla": [
        {ORTH: "justificar", LEMMA: "justificar", TAG: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "mantenerlas": [
        {ORTH: "mantener", LEMMA: "mantener", TAG: AUX},
        {ORTH: "las", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "mantenerlos": [
        {ORTH: "mantener", LEMMA: "mantener", TAG: AUX},
        {ORTH: "los", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "mantenerme": [
        {ORTH: "mantener", LEMMA: "mantener", TAG: AUX},
        {ORTH: "me", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "pasarte": [
        {ORTH: "pasar", LEMMA: "pasar", TAG: AUX},
        {ORTH: "te", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "pedirle": [
        {ORTH: "pedir", LEMMA: "pedir", TAG: AUX},
        {ORTH: "le", LEMMA: "él", TAG: "PRON"}
    ],

    "pel": [
        {ORTH: "per", LEMMA: "per", TAG: ADP},
        {ORTH: "el", LEMMA: "el", TAG: DET}
    ],

    "pidiéndonos": [
        {ORTH: "pidiendo", LEMMA: "pedir", TAG: AUX},
        {ORTH: "nos", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "poderle": [
        {ORTH: "poder", LEMMA: "poder", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "preguntarse": [
        {ORTH: "preguntar", LEMMA: "preguntar", TAG: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "preguntándose": [
        {ORTH: "preguntando", LEMMA: "preguntar", TAG: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "presentarla": [
        {ORTH: "presentar", LEMMA: "presentar", TAG: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "pudiéndolo": [
        {ORTH: "pudiendo", LEMMA: "poder", TAG: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "pudiéndose": [
        {ORTH: "pudiendo", LEMMA: "poder", TAG: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "quererle": [
        {ORTH: "querer", LEMMA: "querer", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "rasgarse": [
        {ORTH: "Rasgar", LEMMA: "rasgar", TAG: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "repetirlo": [
        {ORTH: "repetir", LEMMA: "repetir", TAG: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "robarle": [
        {ORTH: "robar", LEMMA: "robar", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "seguirlos": [
        {ORTH: "seguir", LEMMA: "seguir", TAG: AUX},
        {ORTH: "los", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "serle": [
        {ORTH: "ser", LEMMA: "ser", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "serlo": [
        {ORTH: "ser", LEMMA: "ser", TAG: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "señalándole": [
        {ORTH: "señalando", LEMMA: "señalar", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "suplicarle": [
        {ORTH: "suplicar", LEMMA: "suplicar", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "tenerlos": [
        {ORTH: "tener", LEMMA: "tener", TAG: AUX},
        {ORTH: "los", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "vengarse": [
        {ORTH: "vengar", LEMMA: "vengar", TAG: AUX},
        {ORTH: "se", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "verla": [
        {ORTH: "ver", LEMMA: "ver", TAG: AUX},
        {ORTH: "la", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "verle": [
        {ORTH: "ver", LEMMA: "ver", TAG: AUX},
        {ORTH: "le", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "volverlo": [
        {ORTH: "volver", LEMMA: "volver", TAG: AUX},
        {ORTH: "lo", LEMMA: PRON_LEMMA, TAG: "PRON"}
    ],

    "aprox.": [
        {ORTH: "aprox.", LEMMA: "aproximadamente"}
    ],

    "dna.": [
        {ORTH: "dna.", LEMMA: "docena"}
    ],

    "esq.": [
        {ORTH: "esq.", LEMMA: "esquina"}
    ],

    "pág.": [
        {ORTH: "pág.", LEMMA: "página"}
    ],

    "p.ej.": [
        {ORTH: "p.ej.", LEMMA: "por ejemplo"}
    ],

    "Ud.": [
        {ORTH: "Ud.", LEMMA: PRON_LEMMA, NORM: "usted"}
    ],

    "Vd.": [
        {ORTH: "Vd.", LEMMA: PRON_LEMMA, NORM: "usted"}
    ],

    "Uds.": [
        {ORTH: "Uds.", LEMMA: PRON_LEMMA, NORM: "ustedes"}
    ],

    "Vds.": [
        {ORTH: "Vds.", LEMMA: PRON_LEMMA, NORM: "ustedes"}
    ]
}


ORTH_ONLY = [
    "a.",
    "a.C.",
    "a.J.C.",
    "apdo.",
    "Av.",
    "Avda.",
    "b.",
    "c.",
    "Cía.",
    "d.",
    "e.",
    "etc.",
    "f.",
    "g.",
    "Gob.",
    "Gral.",
    "h.",
    "i.",
    "Ing.",
    "j.",
    "J.C.",
    "k.",
    "l.",
    "Lic.",
    "m.",
    "m.n.",
    "n.",
    "no.",
    "núm.",
    "o.",
    "p.",
    "P.D.",
    "Prof.",
    "Profa.",
    "q.",
    "q.e.p.d."
    "r.",
    "s.",
    "S.A.",
    "S.L.",
    "s.s.s.",
    "Sr.",
    "Sra.",
    "Srta.",
    "t.",
    "u.",
    "v.",
    "w.",
    "x.",
    "y.",
    "z."
]
