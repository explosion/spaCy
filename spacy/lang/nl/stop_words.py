# The original stop words list (added in f46ffe3) was taken from
# http://www.damienvanholten.com/downloads/dutch-stop-words.txt
# and consisted of about 100 tokens.
# In order to achieve parity with some of the better-supported
# languages, e.g., English, French, and German, this original list has been
# extended with 200 additional tokens. The main source of inspiration was
# https://raw.githubusercontent.com/stopwords-iso/stopwords-nl/master/stopwords-nl.txt.
# However, quite a bit of manual editing has taken place as well.
# Tokens whose status as a stop word is not entirely clear were admitted or
# rejected by deferring to their counterparts in the stop words lists for English
# and French. Similarly, those lists were used to identify and fill in gaps so
# that -- in principle -- each token contained in the English stop words list
# should have a Dutch counterpart here.


STOP_WORDS = set(
    """
aan af al alle alles allebei alleen allen als altijd ander anders andere anderen aangaande aangezien achter achterna
afgelopen aldus alhoewel anderzijds

ben bij bijna bijvoorbeeld behalve beide beiden beneden bent bepaald beter betere betreffende binnen binnenin boven
bovenal bovendien bovenstaand buiten

daar dan dat de der den deze die dit doch doen door dus daarheen daarin daarna daarnet daarom daarop des dezelfde dezen
dien dikwijls doet doorgaand doorgaans

een eens en er echter enige eerder eerst eerste eersten effe eigen elk elke enkel enkele enz erdoor etc even eveneens
evenwel

ff

ge geen geweest gauw gedurende gegeven gehad geheel gekund geleden gelijk gemogen geven geweest gewoon gewoonweg
geworden gij

haar had heb hebben heeft hem het hier hij hoe hun hadden hare hebt hele hen hierbeneden hierboven hierin hoewel hun

iemand iets ik in is idd ieder ikke ikzelf indien inmiddels inz inzake

ja je jou jouw jullie jezelf jij jijzelf jouwe juist

kan kon kunnen klaar konden krachtens kunnen kunt

lang later liet liever

maar me meer men met mij mijn moet mag mede meer meesten mezelf mijzelf min minder misschien mocht mochten moest moesten
moet moeten mogelijk mogen

na naar niet niets nog nu nabij nadat net nogal nooit nr nu

of om omdat ons ook op over omhoog omlaag omstreeks omtrent omver onder ondertussen ongeveer onszelf onze ooit opdat
opnieuw opzij over overigens

pas pp precies prof publ

reeds rond rondom

sedert sinds sindsdien slechts sommige spoedig steeds

‘t 't te tegen toch toen tot tamelijk ten tenzij ter terwijl thans tijdens toe totdat tussen

u uit uw uitgezonderd uwe uwen

van veel voor vaak vanaf vandaan vanuit vanwege veeleer verder verre vervolgens vgl volgens vooraf vooral vooralsnog
voorbij voordat voordien voorheen voorop voort voorts vooruit vrij vroeg

want waren was wat we wel werd wezen wie wij wil worden waar waarom wanneer want weer weg wegens weinig weinige weldra
welk welke welken werd werden wiens wier wilde wordt

zal ze zei zelf zich zij zijn zo zonder zou zeer zeker zekere zelfde zelfs zichzelf zijnde zijne zo’n zoals zodra zouden
 zoveel zowat zulk zulke zulks zullen zult
""".split()
)
