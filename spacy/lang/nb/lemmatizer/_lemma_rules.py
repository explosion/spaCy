# coding: utf8
from __future__ import unicode_literals


ADJECTIVE_RULES = [
	["e", ""],			#pene -> pen
	["ere", ""],		#penere -> pen
	["est", ""],		#penest -> pen
	["este", ""]		#peneste -> pen
]


NOUN_RULES = [
	["en", "e"],		#hansken -> hanske
	["a", "e"],			#veska -> veske
	["et", ""],			#dyret -> dyr
	["er", "e"],		#hasker -> hanske	
	["ene", "e"]		#veskene -> veske
]


VERB_RULES = [
    ["er", "e"],		#vasker -> vaske
    ["et", "e"],		#vasket -> vaske
    ["es", "e"],		#vaskes -> vaske
    ["te", "e"],		#stekte -> steke
    ["år", "å"]			#får -> få
]


PUNCT_RULES = []
