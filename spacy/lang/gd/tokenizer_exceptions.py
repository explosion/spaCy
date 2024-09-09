from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

"""
 All rules and exceptions were taken from the "Gaelic Orthographic Conventions
of 2009" (GOC) and from the "Annotated Reference Corpus of Scottish Gaelic" (ARCOSG). I did
my best to ensure this tokenizer would lead to text as close as possible to the
tokenization of the ARCOSG and the conventions in the GOC.


ARCOSG: https://github.com/Gaelic-Algorithmic-Research-Group/ARCOSG
GOC: https://www.gaidhlig.scot/wp-content/uploads/2021/03/GOC-2009-English.pdf
"""

# Compound words
_exc = {
    "càil": [{ORTH: "cà", NORM: "càite"}, {ORTH: "il", NORM: "bheil"}],
    "sna": [{ORTH: "s", NORM: "anns"}, {ORTH: "na", NORM: "na"}],
    "orra": [{ORTH: "orr", NORM: "air"}, {ORTH: "a", NORM: "do"}],
    "fiùs": [{ORTH: "fiù", NORM: "fiù"}, {ORTH: "s", NORM: "'s"}],
}


# Hyphenations that are alternative forms of words
for exc_data in [
    {ORTH: "fa-near", NORM: "fainear"},
    {ORTH: "Fa-near", NORM: "Fainear"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


# Abreviations and shortened words
for exc_data in [
    {ORTH: "'", NORM: "a"},
    {ORTH: "'S", NORM: "Agus"},
    {ORTH: "'s", NORM: "agus"},
    {ORTH: "B'", NORM: "Bu"},
    {ORTH: "b'", NORM: "bu"},
    {ORTH: "D'", NORM: "Do"},
    {ORTH: "d'", NORM: "do"},
    {ORTH: "'M", NORM: "Am"},
    {ORTH: "'m", NORM: "am"},
    {ORTH: "M'", NORM: "Mo"},
    {ORTH: "m'", NORM: "mo"},
    {ORTH: "'n", NORM: "an"},
    {ORTH: "'N", NORM: "An"},
    {ORTH: "Th'", NORM: "Tha"},
    {ORTH: "th'", NORM: "tha"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


# Words with a leading apostrophe
for orth in """
  'ac
  'Ac
  'ad
  'Ad
  'ar
  'Ar
  'bhuannachd
  'Bhuannachd
  'd
  'D
  'eil
  'Eil
  'eug
  'Eug
  'g
  'G
  'ga
  'Ga
  'gad
  'Gad
  'gam
  'Gam
  'gan
  'Gan
  'gar
  'Gar
  'gur
  'Gur
  'ic
  'Ic
  'il
  'Il
  'ill'
  'Ill'
  'ille
  'Ille
  'illean
  'Illean
  'iodh
  'Iodh
  'l
  'L
  'm
  'M
  'n
  'N
  'na
  'Na
  'nad
  'Nad
  'nam
  'Nam
  'nan
  'Nan
  'nar
  'Nar
  'neil
  'Neil
  'nise
  'Nise
  'nuair
  'Nuair
  'nur
  'Nur
  's
  'S
  'sa
  'Sa
  'sa'
  'Sa'
  'san
  'San
  'sann
  'Sann
  'se
  'Se
  'sna
  'Sna
  'son
  'Son
  'urchaidh
  'Urchaidh
  """.split():
    _exc[orth] = [{ORTH: orth}]

# Words with a trailing or middling apostrophe
for orth in """
  a'
  A'
  a'd
  A'd
  a'm
  A'm
  a's
  A's
  ac'
  Ac'
  agads'
  Agads'
  agams'
  Agams'
  aig'
  Aig'
  annams'
  Annams'
  ars'
  Ars'
  b'
  B'
  ball'
  Ball'
  bioraicht'
  Bioraicht'
  bh'
  Bh'
  bhail'
  Bhail'
  bhall'
  Bhall'
  bheath'
  Bheath'
  bhliadhn'
  Bhliadhn'
  bliadhn'
  Bliadhn'
  bonnant'
  Bonnant'
  brist'
  Brist'
  bàt'
  Bàt'
  c'à
  C'à
  camp'
  Camp'
  chalp'
  Chalp'
  champ'
  Champ'
  chomhairl'
  Chomhairl'
  chual'
  Chual'
  chuimhn'
  Chuimhn'
  colaisd'
  Colaisd'
  comhl'
  Comhl'
  comhairl'
  Comhairl'
  creids'
  Creids'
  cual'
  Cual'
  cuimhn'
  Cuimhn'
  cuin'
  Cuin'
  cà'
  Cà'
  càit'
  Càit'
  d'
  D'
  d'readh
  D'readh
  d'reaghadh
  D'reaghadh
  daoin'
  Daoin'
  deimhinn'
  Deimhinn'
  de'n
  De'n
  dh'
  Dh'
  dhaib'
  Dhaib'
  dhaoin'
  Dhaoin'
  dhòmhs'
  Dhòmhs'
  dhu'sa
  Dhu'sa
  dhuin'
  Dhuin'
  do'n
  Do'n
  duin'
  Duin'
  dòch'
  Dòch'
  dùint'
  Dùint'
  eil'
  Eil'
  f'a
  F'a
  fac'
  Fac'
  fad'
  Fad'
  fhac'
  Fhac'
  fhad'
  Fhad'
  fhaid'
  Fhaid'
  fhaisg'
  Fhaisg'
  fhiosd'
  Fhiosd'
  fàilt'
  Fàilt'
  g'
  G'
  gàir'
  Gàir'
  ghill'
  Ghill'
  gill'
  Gill'
  inns'
  Inns'
  innt'
  Innt'
  ionnsaicht'
  Ionnsaicht'
  leams'
  Leams'
  leoth'
  Leoth'
  lobht'
  Lobht'
  m'
  M'
  m'a
  M'a
  m's
  M's
  mhuth'
  Mhuth'
  mhòr'
  Mhòr'
  mis'
  Mis'
  mu'n
  Mu'n
  mòr'
  Mòr'
  oirr'
  Oirr'
  o'n
  O'n
  phàp'
  Phàp'
  pàp'
  Pàp'
  pòs'
  Pòs'
  prionns'
  Prionns'
  r'
  R'
  riums'
  Riums'
  riuth'
  Riuth'
  ro'n
  Ro'n
  sa'
  Sa'
  sgoil'
  Sgoil'
  sgìr'
  Sgìr'
  sheòrs'
  Sheòrs'
  sin'
  Sin'
  stall'
  Stall'
  sìod'
  Sìod'
  sònraicht'
  Sònraicht'
  t'
  T'
  taigh'
  Taigh'
  tein'
  Tein'
  teoth'
  Teoth'
  th'
  Th'
  thoilicht'
  Thoilicht'
  thuc'
  Thuc'
  thuigs'
  Thuigs'
  thus'
  Thus'
  thàna'
  Thàna'
  toilicht'
  Toilicht'
  tro'
  Tro'
  uisg'
  Uisg'
  àit'
  Àit'
  òg'
  Òg'
  """.split():
    _exc[orth] = [{ORTH: orth}]


# Hyphenations that should remain as single tokens
for orth in """
'n-dràsda
'N-dràsda
-bhliadhn'
-bhliadhn'
a-bhos
A-bhos
a-bhòn-dè
A-bhòn-dè
a-cheart
A-cheart
a-chèile
A-chèile
a-deas
A-deas
a-mach
A-mach
a-mhàin
A-mhàin
a-muigh
A-muigh
a-màireach
A-màireach
a-nall
A-nall
a-neist
A-neist
a-ni
A-ni
a-nis
A-nis
a-nisd
A-nisd
a-nise
A-nise
a-nist
A-nist
a-niste
A-niste
a-nochd
A-nochd
a-nuas
A-nuas
a-null
A-null
a-raoir
A-raoir
a-riamh
A-riamh
a-rithist
A-rithist
a-rèiste
A-rèiste
a-rìs
A-rìs
a-seo
A-seo
a-sin
A-sin
a-sineach
A-sineach
a-siud
A-siud
a-staigh
A-staigh
a-steach
A-steach
a-tuath
A-tuath
aca-san
Aca-san
agad-sa
Agad-sa
agam-sa
Agam-sa
aghaidh-bhualaich
Aghaidh-bhualaich
aice-se
Aice-se
aige-san
Aige-san
ainmeannan-àite
Ainmeannan-àite
air-san
Air-san
am-bliadhna
Am-bliadhna
am-màireach
Am-màireach
amp-head
Amp-head
an-diugh
An-diugh
an-dràsd
An-dràsd
an-dràsda
An-dràsda
an-dràst
An-dràst
an-dràsta
An-dràsta
an-dè
An-dè
an-dé
An-dé
an-nise
An-nise
an-nochd
An-nochd
an-raoir
An-raoir
an-uiridh
An-uiridh
an-àbhaisteach
An-àbhaisteach
an-àird
An-àird
an-àirde
An-àirde
an-àrda
An-àrda
ana-ceartas
Ana-ceartas
ana-seo
Ana-seo
ana-sin
Ana-sin
ana-siud
Ana-siud
annam-s'
Annam-s'
ao-coltach
Ao-coltach
aobhar-sa
Aobhar-sa
aois-léinn
Aois-léinn
aona-ghnothaich
Aona-ghnothaich
ar-a-mach
Ar-a-mach
ard-easbaig
Ard-easbaig
ard-luchd-poilitics
Ard-luchd-poilitics
ath-bhaile
Ath-bhaile
ath-bheòthachadh
Ath-bheòthachadh
ath-bhliadhna
Ath-bhliadhna
ath-ghiollachd
Ath-ghiollachd
ath-nuadhais
Ath-nuadhais
ath-sgrùdadh
Ath-sgrùdadh
ath-thriop
Ath-thriop
athair-san
Athair-san
baile-ciùird
Baile-ciùird
ball-coise
Ball-coise
ball-pàrlamaid
Ball-pàrlamaid
ball-sampaill
Ball-sampaill
balla-mara
Balla-mara
ban-chompanach
Ban-chompanach
ban-fhuamhaire
Ban-fhuamhaire
ban-ghillìosach
Ban-ghillìosach
ban-righ'nn
Ban-righ'nn
ban-rìgh
Ban-rìgh
bana-bhàird
Bana-bhàird
bana-chompanaich
Bana-chompanaich
bana-phòsda
Bana-phòsda
banas-taighe
Banas-taighe
beairt-fhuaigheil
Beairt-fhuaigheil
beairt-fuaigheil
Beairt-fuaigheil
bean-gairm
Bean-gairm
bean-phòsta
Bean-phòsta
bean-taighe
Bean-taighe
beul-aithris
Beul-aithris
beò-shlàint
Beò-shlàint
beò-shlàint'
Beò-shlàint'
beò-shlàinte
Beò-shlàinte
bhaga-sgoil
Bhaga-sgoil
bhall-pàrlamaid
Bhall-pàrlamaid
bhan-chompanach
Bhan-chompanach
bhan-dòmhnallach
Bhan-dòmhnallach
bhan-phrionnsa
Bhan-phrionnsa
bhan-righinn
Bhan-righinn
bhan-sheinneadair
Bhan-sheinneadair
bharr-iall
Bharr-iall
bhata-làidir
Bhata-làidir
bhath-room
Bhath-room
bheachd-sa
Bheachd-sa
bheachd-san
Bheachd-san
bheairt-fhighe
Bheairt-fhighe
bheairtean-fuaigheil
Bheairtean-fuaigheil
bheinn-sheilg
Bheinn-sheilg
bheul-aithris
Bheul-aithris
bheò-ghlacadh
Bheò-ghlacadh
bhith-beò
Bhith-beò
bhithinn-sa
Bhithinn-sa
bhogsa-chiùil
Bhogsa-chiùil
bhonn-stéidh
Bhonn-stéidh
bhràithrean-sa
Bhràithrean-sa
bhuain-mhòine
Bhuain-mhòine
bhun-sheòrsa
Bhun-sheòrsa
bhàn-righinn
Bhàn-righinn
bhàn-rinn
Bhàn-rinn
bhàn-rìgh
Bhàn-rìgh
bhàta-aiseig
Bhàta-aiseig
bhàta-sa
Bhàta-sa
bird-watcher
Bird-watcher
bith-beò
Bith-beò
bithinn-sa
Bithinn-sa
bliadhna-sa
Bliadhna-sa
bogha-saighead
Bogha-saighead
boma-peatroil
Boma-peatroil
bristeadh-a-mach
Bristeadh-a-mach
buidhean-cathrannais
Buidhean-cathrannais
buille-a-mach
Buille-a-mach
buille-shaor
Buille-shaor
bun-adhbharan
Bun-adhbharan
bun-chomharraidhean
Bun-chomharraidhean
bun-fhiosrachadh
Bun-fhiosrachadh
bun-sgoil
Bun-sgoil
bun-stèidh
Bun-stèidh
bàt-aiseig
Bàt-aiseig
bàta-aiseig
Bàta-aiseig
bàta-bathair
Bàta-bathair
cainnt-san
Cainnt-san
cal-mac
Cal-mac
carraighean-cuimhne
Carraighean-cuimhne
cead-telebhisean
Cead-telebhisean
ceann-cinnidh
Ceann-cinnidh
ceann-suidhe
Ceann-suidhe
chanain-sa
Chanain-sa
chaolas-arcach
Chaolas-arcach
charge-adh
Charge-adh
cheala-deug
Cheala-deug
chealla-deug
Chealla-deug
cheann-cinnidh
Cheann-cinnidh
cheann-feadhna
Cheann-feadhna
cheann-suidhe
Cheann-suidhe
chearc-fhraoich
Chearc-fhraoich
chearcall-meadhain
Chearcall-meadhain
chearcall-mheadhain
Chearcall-mheadhain
chlann-nighean
Chlann-nighean
chlàr-ama
Chlàr-ama
chlò-bhuaileadh
Chlò-bhuaileadh
chlò-bhualadh
Chlò-bhualadh
cho-chreutairean
Cho-chreutairean
cho-dhùin
Cho-dhùin
cho-dhùnadh
Cho-dhùnadh
cho-dhùnaidhean
Cho-dhùnaidhean
cho-fhaireachdainn
Cho-fhaireachdainn
cho-labhairt
Cho-labhairt
cho-obraiche
Cho-obraiche
cho-roinn
Cho-roinn
chom-pàirt
Chom-pàirt
chorra-ghritheach
Chorra-ghritheach
chrann-snàth
Chrann-snàth
chreach-s'
Chreach-s'
chrith-thalmhainn
Chrith-thalmhainn
chàch-a-chéile
Chàch-a-chéile
cinn-chuspair
Cinn-chuspair
cinn-iùil
Cinn-iùil
cion-doighe
Cion-doighe
clachan-meallain
Clachan-meallain
clann-sgoile
Clann-sgoile
claon-fhaireachdainn
Claon-fhaireachdainn
claon-shamhail
Claon-shamhail
cluicheadairean-meadhain
Cluicheadairean-meadhain
clàran-ama
Clàran-ama
cléir-seanchain
Cléir-seanchain
clò-bhualadair
Clò-bhualadair
clò-bhualadh
Clò-bhualadh
co-aimsireach
Co-aimsireach
co-bhanntachd
Co-bhanntachd
co-bhuannachd
Co-bhuannachd
co-buannachd
Co-buannachd
co-cheangail
Co-cheangail
co-cheangailte
Co-cheangailte
co-cheangal
Co-cheangal
co-chreutairean
Co-chreutairean
co-chruinneachadh
Co-chruinneachadh
co-dhiu
Co-dhiu
co-dhiubh
Co-dhiubh
co-dhiù
Co-dhiù
co-dhiùbh
Co-dhiùbh
co-dhùnadh
Co-dhùnadh
co-dhùnaidhean
Co-dhùnaidhean
co-fhaireachadh
Co-fhaireachadh
co-fhaireachdainn
Co-fhaireachdainn
co-impirean
Co-impirean
co-ionad
Co-ionad
co-ionann
Co-ionann
co-labhairt
Co-labhairt
co-labhairtean
Co-labhairtean
co-obrachadh
Co-obrachadh
co-sheirm
Co-sheirm
co-theacs
Co-theacs
coimeas-meudachd
Coimeas-meudachd
cola-deug
Cola-deug
com-pàirt
Com-pàirt
cope-adh
Cope-adh
crann-aodaich
Crann-aodaich
crann-snàth
Crann-snàth
crann-tarsainn
Crann-tarsainn
craobh-sgaoileadh
Craobh-sgaoileadh
crith-thalmhainn
Crith-thalmhainn
cruth-rannsachadh
Cruth-rannsachadh
cuid-eigin
Cuid-eigin
cumail-san
Cumail-san
cur-gu-buil
Cur-gu-buil
cur-seachad
Cur-seachad
cur-seachadan
Cur-seachadan
cìs-comhairle
Cìs-comhairle
cò-dhunadh
Cò-dhunadh
còmhlan-ciùil
Còmhlan-ciùil
cùis-lagh
Cùis-lagh
cùl-chàineadh
Cùl-chàineadh
cùl-shleamhnach
Cùl-shleamhnach
cùl-taic
Cùl-taic
da-rìreabh
Da-rìreabh
da-rìreadh
Da-rìreadh
da-rìribh
Da-rìribh
deagh-ghean
Deagh-ghean
dearg-fhuileach
Dearg-fhuileach
deireadh-sheachdain
Deireadh-sheachdain
deoch-làidir
Deoch-làidir
dha-rìreabh
Dha-rìreabh
dha-rìribh
Dha-rìribh
dhaibh-san
Dhaibh-san
dhe-salin-adh
Dhe-salin-adh
dhe-salt-adh
Dhe-salt-adh
dheidhinn-sa
Dheidhinn-sa
dhol-sìos
Dhol-sìos
dhomh-s'
Dhomh-s'
dhuine-dubh
Dhuine-dubh
dhà-san
Dhà-san
dhòigh-beatha
Dhòigh-beatha
di-sathairne
Di-sathairne
dian-amharc
Dian-amharc
dlùth-cheangal
Dlùth-cheangal
do-chreidsinneach
Do-chreidsinneach
do-labhairt
Do-labhairt
do-sheachant'
Do-sheachant'
dol-a-mach
Dol-a-mach
dol-air-adhart
Dol-air-adhart
dubh-chàineadh
Dubh-chàineadh
dubh-ghorm
Dubh-ghorm
dà-chultarach
Dà-chultarach
dà-reug
Dà-reug
dàn-mòr
Dàn-mòr
dì-moladh
Dì-moladh
dòigh-beatha
Dòigh-beatha
dòighean-beatha
Dòighean-beatha
e-mail
E-mail
eadar-dhealachadh
Eadar-dhealachadh
eadar-dhealachaidhean
Eadar-dhealachaidhean
eadar-dhealaichte
Eadar-dhealaichte
eadar-nàiseanta
Eadar-nàiseanta
earbainn-s
Earbainn-s
eàrr-ràdh
Eàrr-ràdh
eòrp-innseanach
Eòrp-innseanach
fa-leth
Fa-leth
fa-near
Fa-near
fad-as
Fad-as
fad-thréimhseach
Fad-thréimhseach
feadaig-mhonaidh
Feadaig-mhonaidh
fealla-dhà
Fealla-dhà
fear-a-ropa
Fear-a-ropa
fear-ceasnachaidh
Fear-ceasnachaidh
fear-faire
Fear-faire
fear-gairm
Fear-gairm
fear-glèidhidh
Fear-glèidhidh
fear-labhairt
Fear-labhairt
fear-naidheachd
Fear-naidheachd
fear-pòsta
Fear-pòsta
fear-sgrùdaidh
Fear-sgrùdaidh
fear-teagaisg
Fear-teagaisg
fear-trèinidh
Fear-trèinidh
fear-éisteachd
Fear-éisteachd
feed-adh
Feed-adh
fhear-ghlèidhidh
Fhear-ghlèidhidh
fhear-gleidhidh
Fhear-gleidhidh
fhear-glèidhidh
Fhear-glèidhidh
fhear-labhairt
Fhear-labhairt
fhear-leughaidh
Fhear-leughaidh
fhear-sa
Fhear-sa
fhear-sgrùdaidh
Fhear-sgrùdaidh
fhir-cinnidh
Fhir-cinnidh
fhéin-ìomhaigh
Fhéin-ìomhaigh
fhìor-luachmhor
Fhìor-luachmhor
fois-fhòirneirt
Fois-fhòirneirt
fàs-bheairtean
Fàs-bheairtean
féin-mhisneachd
Féin-mhisneachd
féin-mholadh
Féin-mholadh
fìor-thàbhachdach
Fìor-thàbhachdach
ge-ta
Ge-ta
ge-tà
Ge-tà
ged-tà
Ged-tà
geàrr-chunntais
Geàrr-chunntais
geàrr-chunntas
Geàrr-chunntas
geàrr-thréimhseach
Geàrr-thréimhseach
ghuth-thàmh
Ghuth-thàmh
glain'-amhairc
Glain'-amhairc
glas-ghuib
Glas-ghuib
gnàth-bhriathrachas
Gnàth-bhriathrachas
gàrradh-crìche
Gàrradh-crìche
h-
H-
h-ana-miannaibh
H-ana-miannaibh
h-uile
H-uile
hó-ró
Hó-ró
iar-mhinistear
Iar-mhinistear
inneal-spreadhaidh
Inneal-spreadhaidh
ionad-còmhnaidh
Ionad-còmhnaidh
join-adh
Join-adh
latha-an-diugh
Latha-an-diugh
leam-sa
Leam-sa
leas-adh
Leas-adh
lease-adh
Lease-adh
leat-sa
Leat-sa
leotha-san
Leotha-san
leth-char
Leth-char
leth-cheud
Leth-cheud
leth-ghàidhealtachd
Leth-ghàidhealtachd
leth-pocannan
Leth-pocannan
leth-sgeulan
Leth-sgeulan
leth-uair
Leth-uair
leughadh-ne
Leughadh-ne
lighiche-sprèidh
Lighiche-sprèidh
linn-an-òir
Linn-an-òir
litir-aonta
Litir-aonta
loma-làn
Loma-làn
lost-s'
Lost-s'
luchd-altram
Luchd-altram
luchd-altruim
Luchd-altruim
luchd-amhairc
Luchd-amhairc
luchd-ciùil
Luchd-ciùil
luchd-cruinneachaidh
Luchd-cruinneachaidh
luchd-dìon
Luchd-dìon
luchd-ealain
Luchd-ealain
luchd-einnseanaraidh
Luchd-einnseanaraidh
luchd-glèidhteachais
Luchd-glèidhteachais
luchd-gnìomhachais
Luchd-gnìomhachais
luchd-iomairt
Luchd-iomairt
luchd-lagh
Luchd-lagh
luchd-lagha
Luchd-lagha
luchd-leanmhainn
Luchd-leanmhainn
luchd-litreachais
Luchd-litreachais
luchd-obrach
Luchd-obrach
luchd-reic
Luchd-reic
luchd-sgrùdaidh
Luchd-sgrùdaidh
luchd-teagaisg
Luchd-teagaisg
luchd-turais
Luchd-turais
luchd-éisdeachd
Luchd-éisdeachd
luchd-éisteachd
Luchd-éisteachd
là-an-diugh
Là-an-diugh
làmh-chuideachaidh
Làmh-chuideachaidh
làmh-sgrìobhainn
Làmh-sgrìobhainn
làmh-sgrìobhainnean
Làmh-sgrìobhainnean
làmh-sgrìobhta
Làmh-sgrìobhta
làn-bheachd
Làn-bheachd
làn-ghàidhealtachd
Làn-ghàidhealtachd
làn-thuigse
Làn-thuigse
làn-ùine
Làn-ùine
làrna-mhàireach
Làrna-mhàireach
lìn-bheaga
Lìn-bheaga
lùth-chleasan
Lùth-chleasan
ma-ta
Ma-ta
ma-tha
Ma-tha
ma-thà
Ma-thà
ma-tà
Ma-tà
mac-an-duine
Mac-an-duine
mac-léinn
Mac-léinn
mac-meanmna
Mac-meanmna
maighstir-sgoile
Maighstir-sgoile
maor-chladaich
Maor-chladaich
maor-fearainn
Maor-fearainn
mar-thà
Mar-thà
marbh-riaghailt
Marbh-riaghailt
meadhan-aoiseil
Meadhan-aoiseil
meadhan-latha
Meadhan-latha
meadhan-oidhche
Meadhan-oidhche
meal-an-naidheachd
Meal-an-naidheachd
mean-fhàs
Mean-fhàs
mhac-meanmna
Mhac-meanmna
mheadhain-latha
Mheadhain-latha
mheadhain-oidhche
Mheadhain-oidhche
mheadhan-oidhche
Mheadhan-oidhche
mheantraiginn-sa
Mheantraiginn-sa
mhi-rùn
Mhi-rùn
mhic-an-duine
Mhic-an-duine
mhoraltachd-sa
Mhoraltachd-sa
mhuir-làn
Mhuir-làn
mhuir-sgèin
Mhuir-sgèin
mhàthair-san
Mhàthair-san
mhì-chinnt
Mhì-chinnt
mhì-chneasda
Mhì-chneasda
mhì-chòrdadh
Mhì-chòrdadh
mhì-riaraichte
Mhì-riaraichte
mhì-shocair
Mhì-shocair
mhòr-chuid
Mhòr-chuid
mhòr-shluagh
Mhòr-shluagh
mhòr-shluaigh
Mhòr-shluaigh
mhór-amharas
Mhór-amharas
mhór-chuid
Mhór-chuid
mhór-shluaigh
Mhór-shluaigh
mi-chneasda
Mi-chneasda
mi-rùn
Mi-rùn
mic-léinn
Mic-léinn
mion-chànain
Mion-chànain
mion-fhios
Mion-fhios
mion-fhiosrach
Mion-fhiosrach
mion-sgrùdadh
Mion-sgrùdadh
muir-meadhon-thireach
Muir-meadhon-thireach
mèinnean-talmhainn
Mèinnean-talmhainn
mì-chinnt
Mì-chinnt
mì-choltach
Mì-choltach
mì-dhòigh
Mì-dhòigh
mì-fhair
Mì-fhair
mì-fhortanach
Mì-fhortanach
mì-laghail
Mì-laghail
mì-nàdarra
Mì-nàdarra
mì-nàdarrach
Mì-nàdarrach
mì-rùin
Mì-rùin
mì-shealbhach
Mì-shealbhach
mì-thlachd
Mì-thlachd
mòr-shluagh
Mòr-shluagh
mór-bhuannachd
Mór-bhuannachd
mór-chuid
Mór-chuid
mór-roinn
Mór-roinn
n-
N-
neach-casaid
Neach-casaid
neach-cathrach
Neach-cathrach
neach-gairm
Neach-gairm
neo-chiontach
Neo-chiontach
neo-eisimeileach
Neo-eisimeileach
neo-iomlan
Neo-iomlan
neo-àbhaisteach
Neo-àbhaisteach
nua-bhàrdachd
Nua-bhàrdachd
nì-eigin
Nì-eigin
obair-sa
Obair-sa
oifigear-stiùiridh
Oifigear-stiùiridh
oirbh-se
Oirbh-se
ola-thruis
Ola-thruis
orm-sa
Orm-sa
orra-san
Orra-san
phiuthar-chéile
Phiuthar-chéile
phort-adhair
Phort-adhair
phump-adh
Phump-adh
phàipeir-naidheachd
Phàipeir-naidheachd
phòcaid-thòine
Phòcaid-thòine
pole-aichean
Pole-aichean
port-adhair
Port-adhair
proove-adh
Proove-adh
pàipear-naidheachd
Pàipear-naidheachd
pàipearan-naidheachd
Pàipearan-naidheachd
radio-beò
Radio-beò
rithe-se
Rithe-se
rium-sa
Rium-sa
ro-chumhang
Ro-chumhang
ro-eòlach
Ro-eòlach
ro-innleachd
Ro-innleachd
ro-làimh
Ro-làimh
ro-shealladh
Ro-shealladh
roth-thoisich
Roth-thoisich
rèidio-beò
Rèidio-beò
rùm-cùil
Rùm-cùil
sadadh-a-steach
Sadadh-a-steach
samhradh-a-chaidh
Samhradh-a-chaidh
saor-làithean
Saor-làithean
sead-fhighe
Sead-fhighe
sean-ghnàthas
Sean-ghnàthas
seana-bhliadhn'
Seana-bhliadhn'
seirbhis-aisig
Seirbhis-aisig
seòl-mara
Seòl-mara
seòmar-cadail
Seòmar-cadail
sgeulachdan-gaisge
Sgeulachdan-gaisge
sgoil-marcaidheachd
Sgoil-marcaidheachd
sgìr-easbaig
Sgìr-easbaig
sgìre-easbaig
Sgìre-easbaig
sheann-fhasanta
Sheann-fhasanta
shlatan-connaidh
Shlatan-connaidh
shon-sa
Shon-sa
shàr-sgoilear
Shàr-sgoilear
sibh-se
Sibh-se
snodha-gàire
Snodha-gàire
so-labhairt
So-labhairt
soch-mhalairteach
Soch-mhalairteach
spor-gunna
Spor-gunna
sàr-bheachdan
Sàr-bheachdan
sìor-dhol
Sìor-dhol
sùil-air-ais
Sùil-air-ais
sùil-mhara
Sùil-mhara
t-
T-
taigh-cuibhle
Taigh-cuibhle
taigh-céilidh
Taigh-céilidh
taigh-sa
Taigh-sa
taigh-sheinnse
Taigh-sheinnse
taigh-tasgaidh
Taigh-tasgaidh
taigh-tughaidh
Taigh-tughaidh
taigh-òsda
Taigh-òsda
taigh-òsta
Taigh-òsta
taighean-aoigheachd
Taighean-aoigheachd
taobh-sa
Taobh-sa
teachd-an-tìr
Teachd-an-tìr
teaghlach-chànanan
Teaghlach-chànanan
thaicean-airgid
Thaicean-airgid
thaighean-altraim
Thaighean-altraim
thonn-gheal
Thonn-gheal
thuigse-san
Thuigse-san
tigh-croiteir
Tigh-croiteir
tigh-còmhnaidh
Tigh-còmhnaidh
tigh-seinnse
Tigh-seinnse
tigh-sheinnse
Tigh-sheinnse
tighearnan-fearainn
Tighearnan-fearainn
togail-cridhe
Togail-cridhe
travel-adh
Travel-adh
triob-sa
Triob-sa
tro-chèile
Tro-chèile
troimh-a-chéile
Troimh-a-chéile
troimh-chèile
Troimh-chèile
troimhe-chéile
Troimhe-chéile
tuathanas-éisg
Tuathanas-éisg
tè-labhairt
Tè-labhairt
tìr-mhóir
Tìr-mhóir
tìr-mòr
Tìr-mòr
ugam-s'
Ugam-s'
ugam-sa
Ugam-sa
uige-san
Uige-san
uile-gu-lèir
Uile-gu-lèir
uile-tuigseach
Uile-tuigseach
use-agadh
Use-agadh
watch-adh
Watch-adh
weld-adh
Weld-adh
àrd-cheannard
Àrd-cheannard
àrd-chomhairliche
Àrd-chomhairliche
àrd-chonstabal
Àrd-chonstabal
àrd-dhuine
Àrd-dhuine
àrd-ionmhair
Àrd-ionmhair
àrd-oifigear
Àrd-oifigear
àrd-oifigeir
Àrd-oifigeir
àrd-sgoil
Àrd-sgoil
àrd-ìre
Àrd-ìre
àrd-ùrlair
Àrd-ùrlair
àrd-ùrlar
Àrd-ùrlar
às-creideach
Às-creideach
àtha-cheilpe
Àtha-cheilpe
ìre-sa
Ìre-sa
ìre-se
Ìre-se
òg-mhios
Òg-mhios
òige-sa
Òige-sa
òrd-mhòr
Òrd-mhòr""".split():
    _exc[orth] = [{ORTH: orth}]

# Multiple words that should remain as one token
for orth in """'n diugh
'N diugh
'n dà
'N dà
'n iar
'N iar
'n seo
'N seo
'n uairsin
'N uairsin
a a sineach
A a sineach
a b'
A b'
a bhos
A bhos
a bhàn
A bhàn
a bhòn raoir
A bhòn raoir
a bhòn uiridh
A bhòn uiridh
a bhòn-dè
A bhòn-dè
a bhòn-raoir
A bhòn-raoir
a bhòn-uiridh
A bhòn-uiridh
a bu'
A bu'
a chaoidh
A chaoidh
a cheana
A cheana
a chionn
A chionn
a chionn 's
A chionn 's
a chuile
A chuile
a chèil
A chèil
a chèile
A chèile
a chéile
A chéile
a deas
A deas
a dh'
A dh'
a h-uile
A h-uile
a mach
A mach
a muigh
A muigh
a màireach
A màireach
a nall
A nall
a neisd
A neisd
a nis
A nis
a nisd
A nisd
a nise
A nise
a niste
A niste
a nochd
A nochd
a nuas
A nuas
a null
A null
a raoir
A raoir
a riamh
A riamh
a rithist
A rithist
a s
A s
a seo
A seo
a seothach
A seothach
a shineach
A shineach
a sin
A sin
a sineach
A sineach
a staidh
A staidh
a staigh
A staigh
a steach
A steach
a stigh
A stigh
a tuath
A tuath
a uiridh
A uiridh
a' diugh
A' diugh
a' s
A' s
air bith
Air bith
air choireigin
Air choireigin
air choireigin-ach
Air choireigin-ach
air choreigin
Air choreigin
air dheireadh
Air dheireadh
air falbh
Air falbh
air neo
Air neo
air thùs
Air thùs
am a màireach muigh
Am a màireach muigh
am bliadhna
Am bliadhna
am muigh
Am muigh
an am
An am
an aodann bàn
An aodann bàn
an ath bhliadhna
An ath bhliadhna
an ath oidhch'
An ath oidhch'
an ath oidhche
An ath oidhche
an ath sheachdain
An ath sheachdain
an ath sheachdainn
An ath sheachdainn
an ath-bhliadhna
An ath-bhliadhna
an ath-oidhch'
An ath-oidhch'
an ath-oidhche
An ath-oidhche
an ath-sheachdain
An ath-sheachdain
an ath-sheachdainn
An ath-sheachdainn
an ceart-uair
An ceart-uair
an ceartuair
An ceartuair
an còmhnaidh
An còmhnaidh
an de
An de
an deas
An deas
an diugh
An diugh
an dràsda
An dràsda
an dràsta
An dràsta
an dè
An dè
an ear
An ear
an earair
An earair
an earar
An earar
an earras
An earras
an iar
An iar
an iaras
An iaras
an làrna-mhàireach
An làrna-mhàireach
an raoir
An raoir
an sean
An sean
an seo
An seo
an seothach
An seothach
an sin
An sin
an sineach
An sineach
an siod
An siod
an siud
An siud
an siudach
An siudach
an toiseach
An toiseach
an uair
An uair
an uair sin
An uair sin
an uairsin
An uairsin
an uirigh
An uirigh
an àird
An àird
an àirde
An àirde
an ìre mhath
An ìre mhath
ana nàdarra
Ana nàdarra
ann a
Ann a
ann a sheo
Ann a sheo
ann a sheothach
Ann a sheothach
ann a shin
Ann a shin
ann a shineach
Ann a shineach
ann a shiodach
Ann a shiodach
ann a shiud
Ann a shiud
ann a shiudach
Ann a shiudach
ann a'
Ann a'
ann a' shiudach
Ann a' shiudach
ann a-seo
Ann a-seo
ann a-seothach
Ann a-seothach
ann a-sin
Ann a-sin
ann a-sineach
Ann a-sineach
ann a-siud
Ann a-siud
ann am
Ann am
ann an
Ann an
ann an seo
Ann an seo
ann an shin
Ann an shin
ann an shiud
Ann an shiud
ann an sin
Ann an sin
ann an siud
Ann an siud
ann seo
Ann seo
anns a' bhad
Anns a' bhad
anns an
Anns an
ath-oidhch'
Ath-oidhch'
ban-righ 'nn
Ban-righ 'nn
bho thoiseach
Bho thoiseach
bhon 'n
Bhon 'n
bhon a'
Bhon a'
bhon an
Bhon an
bhrist '
Bhrist '
buille a-mach
Buille a-mach
bun os cionn
Bun os cionn
car son
Car son
ceann a tuath
Ceann a tuath
cia mheud
Cia mheud
coille chaoil
Coille chaoil
cò mheud
Cò mheud
có dhiubh
Có dhiubh
d' rachadh
D' rachadh
dhen an
Dhen an
do n
Do n
dè mar
Dè mar
dé mar
Dé mar
eilean tiridhe
Eilean tiridhe
fa leth
Fa leth
fad as
Fad as
fo dheireadh
Fo dheireadh
fon a'
Fon a'
fon an
Fon an
gar bith
Gar bith
gar bith có
Gar bith có
ge 's bith
Ge 's bith
ge b' e air bith
Ge b' e air bith
ge be
Ge be
ge brith
Ge brith
ge brì
Ge brì
gleann dail
Gleann dail
gleann ois
Gleann ois
gu bè gu dè
Gu bè gu dè
gu dè
Gu dè
gu dé
Gu dé
gu ruige
Gu ruige
ho ro gheallaidh
Ho ro gheallaidh
ma dheireadh
Ma dheireadh
ma dheireadh thall
Ma dheireadh thall
ma sgaoil
Ma sgaoil
ma tha
Ma tha
mar an ceudna
Mar an ceudna
mar bu trice
Mar bu trice
mar tha
Mar tha
meadhan aoiseil
Meadhan aoiseil
mu 'n
Mu 'n
mu chuairt
Mu chuairt
mu dheas
Mu dheas
mu dheireadh
Mu dheireadh
mu dheireadh thall
Mu dheireadh thall
mu n
Mu n
mu thràth
Mu thràth
mun a'
Mun a'
mun an
Mun an
na b'
Na b'
na bu
Na bu
na iad
Na iad
nach maireann
Nach maireann
o'n uairsin
O'n uairsin
oidhch '
Oidhch '
on a'
On a'
on an
On an
pholl a' ghrùthain
Pholl a' ghrùthain
roinn eorpa
Roinn eorpa
ron a'
Ron a'
ron an
Ron an
ruaidh mhònaidh
Ruaidh mhònaidh
ruith thairis
Ruith thairis
sa bhad
Sa bhad
sadadh a-mach
Sadadh a-mach
sadadh a-steach
Sadadh a-steach
sam bidh
Sam bidh
sam bith
Sam bith
srath chluaidh
Srath chluaidh
taobh a-muigh
Taobh a-muigh
taobh an ear
Taobh an ear
taobh an iar
Taobh an iar
tria san ngaoidhilcc nalbanaigh
Tria san ngaoidhilcc nalbanaigh
tron a'
Tron a'
tron an
Tron an
tuilleadh 's a chòir
Tuilleadh 's a chòir
tuilleadh sa chòir
Tuilleadh sa chòir""".split(
    "\n"
):
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
