STOP_WORDS = set(
    """
a ak an ankò ant apre ap atò avan avanlè
byen bò byenke

chak

de depi deja deja

e en epi èske

fò fòk

gen genyen

ki kisa kilès kote koukou konsa konbyen konn konnen kounye kouman

la l laa le lè li lye lò

m m' mwen

nan nap nou n'

ou oumenm

pa paske pami pandan pito pou pral preske pwiske

se selman si sou sòt

ta tap tankou te toujou tou tan tout toutotan twòp tèl

w w' wi wè

y y' yo yon yonn

non o oh eh

sa san si swa si

men mèsi oswa osinon

""".split()
)

# Add common contractions, with and without apostrophe variants
contractions = ["m'", "n'", "w'", "y'", "l'", "t'", "k'"]
for apostrophe in ["'", "’", "‘"]:
    for word in contractions:
        STOP_WORDS.add(word.replace("'", apostrophe))
