from ...attrs import LIKE_NUM
from ...attrs import IS_CURRENCY
import unicodedata


_num_words = set(
    """
    nič ničla nula ena dva tri štiri pet šest sedem osem
    devet deset enajst dvanajst trinajst štirinajst petnajst
    šestnajst sedemnajst osemnajst devetnajst dvajset trideset štirideset
    petdeset šestdest sedemdeset osemdeset devedeset sto tisoč
    milijon bilijon trilijon kvadrilijon nešteto
    
    dvoje troje trije štirje 
    """.split()
)

_ordinal_words = set(
    """
    prvi drugi tretji četrti peti šesti sedmi osmi
    deveti deseti enajsti dvanajsti trinajsti štirinajsti
    petnajsti šestnajsti sedemnajsti osemnajsti devetnajsti
    dvajseti trideseti štirideseti petdeseti šestdeseti sedemdeseti
    osemdeseti devetdeseti stoti tisoči milijonti bilijonti
    trilijonti kvadrilijonti nešteti
    
    prva druga tretja četrta peta šesta sedma osma
    deveta deseta enajsta dvanajsta trinajsta štirnajsta
    petnajsta šestnajsta sedemnajsta osemnajsta devetnajsta
    dvajseta trideseta štirideseta petdeseta šestdeseta sedemdeseta
    osemdeseta devetdeseta stota tisoča milijonta bilijonta
    trilijonta kvadrilijonta nešteta
    
    prvo drugo tretje četrto peto šestro sedmo osmo
    deveto deseto enajsto dvanajsto trinajsto štirnajsto
    petnajsto šestnajsto sedemnajsto osemnajsto devetnajsto
    dvajseto trideseto štirideseto petdeseto šestdeseto sedemdeseto
    osemdeseto devetdeseto stoto tisočo milijonto bilijonto
    trilijonto kvadrilijonto nešteto
    
    prvega drugega tretjega četrtega petega šestega sedmega osmega
    devega desetega enajstega dvanajstega trinajstega štirnajstega
    petnajstega šestnajstega sedemnajstega osemnajstega devetnajstega
    dvajsetega tridesetega štiridesetega petdesetega šestdesetega sedemdesetega
    osemdesetega devetdesetega stotega tisočega milijontega bilijontega
    trilijontega kvadrilijontega neštetega
    
    prvemu drugemu tretjemu četrtemu petemu šestemu sedmemu osmemu
    devetemu desetemu enajstemu dvanajstemu trinajstemu štirnajstemu
    petnajstemu šestnajstemu sedemnajstemu osemnajstemu devetnajstemu
    dvajsetemu tridesetemu štiridesetemu petdesetemu šestdesetemu sedemdesetemu
    osemdesetemu devetdesetemu stotemu tisočemu milijontemu bilijontemu
    trilijontemu kvadrilijontemu neštetemu
    
    prvim drugim tretjim četrtim petim šestim sedtim osmim
    devetim desetim enajstim dvanajstim trinajstim štirnajstim
    petnajstim šestnajstim sedemnajstim osemnajstim devetnajstim
    dvajsetim tridesetim štiridesetim petdesetim šestdesetim sedemdesetim
    osemdesetim devetdesetim stotim tisočim milijontim bilijontim
    trilijontim kvadrilijontim neštetim
    
    prvem drugem tretjem četrtem petem šestem sedem osmem
    devetem desetem enajstem dvanajstem trinajstem štirnajstem
    petnajstem šestnajstem sedemnajstem osemnajstem devetnajstem
    dvajsetem tridesetem štiridesetem petdesetem šestdesetem sedemdesetem
    osemdesetem devetdesetem stotem tisočem milijontem bilijontem
    trilijontem kvadrilijontem neštetem
    """.split()
)

_currency_words = set(
    """
    evro evra evri evre evrov evru evroma evrom evrih evr eur
    cent centa centi cente centov centu centoma centom centih
    dolar dolarja dolarji dolarje dolarjev dolarju dolarjema dolarjem dolarjih usd
    tolar tolarja tolarji tolarje tolarjev tolarju tolarjema tolarjem tolarjih sit
    dinar dinarja dinarji dinarjev dinarje dinarju dinarjema dinarjem dinarjih din
    funt funta funti funte funtov funtu funtoma funtom funtih gpb
    forint forinta forinti forinte forintov forintu forintoma forintom forintih 
    zlot zlota zloti zlote zlotov zlotu zlotoma zlotom zlotih
    rupija rupiji rupije rupij rupiju rupijema rupijem rupijih
    jen jena jeni jene jenov jenu jenoma jenom jenih
    kuna kuni kune kun kunoma kunam kunah
    marka marki marke mark markoma markom markih
    """.split()
)


def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    text_lower = text.lower()
    if text_lower in _num_words:
        return True
    if text_lower in _ordinal_words:
        return True
    return False

def is_currency(text):
    text_lower = text.lower()
    if text in _currency_words:
        return True
    for char in text:
        if unicodedata.category(char) != "Sc":
            return False
    return True


LEX_ATTRS = {LIKE_NUM: like_num, IS_CURRENCY: is_currency}