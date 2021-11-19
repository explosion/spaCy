import pytest

def test_long_text(lv_tokenizer):
    # Excerpt: European Convention on Human Rights
    text = """
Šo Konvenciju parakstījušās Eiropas Padomes dalībvalstu valdības,
Ievērodamas Vispārējo cilvēktiesību deklarāciju, ko Apvienoto
Nāciju Organizācijas Ģenerālā Asambleja pieņēmusi 1948. gada 10.
decembrī;
Ievērodamas, ka šī deklarācija paredz nodrošināt vispārēju un
efektīvu tajā pasludināto tiesību atzīšanu un ievērošanu;
Ievērodamas, ka Eiropas Padomes mērķis ir panākt lielāku vienotību
tās dalībvalstu starpā un ka viens no līdzekļiem, kā šo mērķi
sasniegt, ir cilvēka tiesību un pamatbrīvību ievērošana un turpmāka
īstenošana;
No jauna apliecinādamas patiesu pārliecību, ka šīs pamatbrīvības
ir taisnīguma un miera pamats visā pasaulē un ka tās vislabāk var
nodrošināt patiess demokrātisks politisks režīms no vienas puses un
vispārējo cilvēktiesību, uz kurām tās pamatojas, kopīga izpratne un
ievērošana no otras puses;
"""
    tokens = lv_tokenizer(text)
    assert len(tokens) == 140