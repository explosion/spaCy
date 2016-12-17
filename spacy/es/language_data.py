# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA
from ..language_data import TOKENIZER_PREFIXES
from ..language_data import TOKENIZER_SUFFIXES
from ..language_data import TOKENIZER_INFIXES


TAG_MAP = {

}


STOP_WORDS = set("""
actualmente acuerdo adelante ademas además adrede afirmó agregó ahi ahora ahí
al algo alguna algunas alguno algunos algún alli allí alrededor ambos ampleamos
antano antaño ante anterior antes apenas aproximadamente aquel aquella aquellas
aquello aquellos aqui aquél aquélla aquéllas aquéllos aquí arriba arribaabajo
aseguró asi así atras aun aunque ayer añadió aún

bajo bastante bien breve buen buena buenas bueno buenos

cada casi cerca cierta ciertas cierto ciertos cinco claro comentó como con
conmigo conocer conseguimos conseguir considera consideró consigo consigue
consiguen consigues contigo contra cosas creo cual cuales cualquier cuando
cuanta cuantas cuanto cuantos cuatro cuenta cuál cuáles cuándo cuánta cuántas
cuánto cuántos cómo

da dado dan dar de debajo debe deben debido decir dejó del delante demasiado
demás dentro deprisa desde despacio despues después detras detrás dia dias dice
dicen dicho dieron diferente diferentes dijeron dijo dio donde dos durante día
días dónde

ejemplo el ella ellas ello ellos embargo empleais emplean emplear empleas
empleo en encima encuentra enfrente enseguida entonces entre era eramos eran
eras eres es esa esas ese eso esos esta estaba estaban estado estados estais
estamos estan estar estará estas este esto estos estoy estuvo está están ex
excepto existe existen explicó expresó él ésa ésas ése ésos ésta éstas éste
éstos

fin final fue fuera fueron fui fuimos

general gran grandes gueno

ha haber habia habla hablan habrá había habían hace haceis hacemos hacen hacer
hacerlo haces hacia haciendo hago han hasta hay haya he hecho hemos hicieron
hizo horas hoy hubo

igual incluso indicó informo informó intenta intentais intentamos intentan
intentar intentas intento ir

junto

la lado largo las le lejos les llegó lleva llevar lo los luego lugar

mal manera manifestó mas mayor me mediante medio mejor mencionó menos menudo mi
mia mias mientras mio mios mis misma mismas mismo mismos modo momento mucha
muchas mucho muchos muy más mí mía mías mío míos

nada nadie ni ninguna ningunas ninguno ningunos ningún no nos nosotras nosotros
nuestra nuestras nuestro nuestros nueva nuevas nuevo nuevos nunca

ocho os otra otras otro otros

pais para parece parte partir pasada pasado paìs peor pero pesar poca pocas
poco pocos podeis podemos poder podria podriais podriamos podrian podrias podrá
podrán podría podrían poner por porque posible primer primera primero primeros
principalmente pronto propia propias propio propios proximo próximo próximos
pudo pueda puede pueden puedo pues

qeu que quedó queremos quien quienes quiere quiza quizas quizá quizás quién quiénes qué

raras realizado realizar realizó repente respecto

sabe sabeis sabemos saben saber sabes salvo se sea sean segun segunda segundo
según seis ser sera será serán sería señaló si sido siempre siendo siete sigue
siguiente sin sino sobre sois sola solamente solas solo solos somos son soy
soyos su supuesto sus suya suyas suyo sé sí sólo

tal tambien también tampoco tan tanto tarde te temprano tendrá tendrán teneis
tenemos tener tenga tengo tenido tenía tercera ti tiempo tiene tienen toda
todas todavia todavía todo todos total trabaja trabajais trabajamos trabajan
trabajar trabajas trabajo tras trata través tres tu tus tuvo tuya tuyas tuyo
tuyos tú

ultimo un una unas uno unos usa usais usamos usan usar usas uso usted ustedes
última últimas último últimos

va vais valor vamos van varias varios vaya veces ver verdad verdadera verdadero
vez vosotras vosotros voy vuestra vuestras vuestro vuestros

ya yo
""".split())


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
