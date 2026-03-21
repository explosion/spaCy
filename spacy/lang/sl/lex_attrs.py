import unicodedata

from ...attrs import IS_CURRENCY, LIKE_NUM

_num_words = set(
    """
	nula ničla nič ena dva tri štiri pet šest sedem osem
	devet deset enajst dvanajst trinajst štirinajst petnajst
	šestnajst sedemnajst osemnajst devetnajst dvajset trideset štirideset
	petdeset šestdest sedemdeset osemdeset devedeset sto tisoč
	milijon bilijon trilijon kvadrilijon nešteto
	
	en eden enega enemu ennem enim enih enima enimi ene eni eno
	dveh dvema dvem dvoje trije treh trem tremi troje štirje štirih štirim štirimi
	petih petim petimi šestih šestim šestimi sedmih sedmim sedmimi osmih osmim osmimi
	devetih devetim devetimi desetih desetim desetimi enajstih enajstim enajstimi
	dvanajstih dvanajstim dvanajstimi trinajstih trinajstim trinajstimi
	šestnajstih šestnajstim šestnajstimi petnajstih petnajstim petnajstimi
	sedemnajstih sedemnajstim sedemnajstimi osemnajstih osemnajstim osemnajstimi
	devetnajstih devetnajstim devetnajstimi dvajsetih dvajsetim dvajsetimi  
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
	
	prvemu drugemu tretjemu četrtemu petemu šestemu sedmemu osmemu devetemu desetemu 
	enajstemu dvanajstemu trinajstemu štirnajstemu petnajstemu šestnajstemu sedemnajstemu
	osemnajstemu devetnajstemu dvajsetemu tridesetemu štiridesetemu petdesetemu šestdesetemu
	sedemdesetemu osemdesetemu devetdesetemu stotemu tisočemu milijontemu bilijontemu
	trilijontemu kvadrilijontemu neštetemu
	
	prvem drugem tretjem četrtem petem šestem sedmem osmem devetem desetem
	enajstem dvanajstem trinajstem štirnajstem petnajstem šestnajstem sedemnajstem
	osemnajstem devetnajstem dvajsetem tridesetem štiridesetem petdesetem šestdesetem
	sedemdesetem osemdesetem devetdesetem stotem tisočem milijontem bilijontem
	trilijontem kvadrilijontem neštetem
	
	prvim drugim tretjim četrtim petim šestim sedtim osmim devetim desetim
	enajstim dvanajstim trinajstim štirnajstim petnajstim šestnajstim sedemnajstim
	osemnajstim devetnajstim dvajsetim tridesetim štiridesetim petdesetim šestdesetim
	sedemdesetim osemdesetim devetdesetim stotim tisočim milijontim bilijontim
	trilijontim kvadrilijontim neštetim
	    
	prvih drugih tretjih četrthih petih šestih sedmih osmih deveth desetih
	enajstih dvanajstih trinajstih štirnajstih petnajstih šestnajstih sedemnajstih
	osemnajstih devetnajstih dvajsetih tridesetih štiridesetih petdesetih šestdesetih
	sedemdesetih osemdesetih devetdesetih stotih tisočih milijontih bilijontih
	trilijontih kvadrilijontih nešteth
	
	prvima drugima tretjima četrtima petima šestima sedmima osmima devetima desetima
	enajstima dvanajstima trinajstima štirnajstima petnajstima šestnajstima sedemnajstima
	osemnajstima devetnajstima dvajsetima tridesetima štiridesetima petdesetima šestdesetima
	sedemdesetima osemdesetima devetdesetima stotima tisočima milijontima bilijontima
	trilijontima kvadrilijontima neštetima
	
	prve druge četrte pete šeste sedme osme devete desete
	enajste dvanajste trinajste štirnajste petnajste šestnajste sedemnajste
	osemnajste devetnajste dvajsete tridesete štiridesete petdesete šestdesete
	sedemdesete osemdesete devetdesete stote tisoče milijonte bilijonte 
	trilijonte kvadrilijonte neštete
	
	prvimi drugimi tretjimi četrtimi petimi šestimi sedtimi osmimi devetimi desetimi
	enajstimi dvanajstimi trinajstimi štirnajstimi petnajstimi šestnajstimi sedemnajstimi
	osemnajstimi devetnajstimi dvajsetimi tridesetimi štiridesetimi petdesetimi šestdesetimi
	sedemdesetimi osemdesetimi devetdesetimi stotimi tisočimi milijontimi bilijontimi
	trilijontimi kvadrilijontimi neštetimi
	""".split()
)

_currency_words = set(
    """
	evro evra evru evrom evrov evroma evrih evrom evre evri evr eur
	cent centa centu cenom centov centoma centih centom cente centi
	dolar dolarja dolarji dolarju dolarjem dolarjev dolarjema dolarjih dolarje usd
	tolar tolarja tolarji tolarju tolarjem tolarjev tolarjema tolarjih tolarje tol
	dinar dinarja dinarji dinarju dinarjem dinarjev dinarjema dinarjih dinarje din
	funt funta funti funtu funtom funtov funtoma funtih funte gpb
	forint forinta forinti forintu forintom forintov forintoma forintih forinte
	zlot zlota zloti zlotu zlotom zlotov zlotoma zlotih zlote 
	rupij rupija rupiji rupiju rupijem rupijev rupijema rupijih rupije
	jen jena jeni jenu jenom jenov jenoma jenih jene
	kuna kuni kune kuno kun kunama kunah kunam kunami
	marka marki marke markama markah markami 
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
