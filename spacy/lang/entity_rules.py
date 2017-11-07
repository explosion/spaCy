# coding: utf8
from __future__ import unicode_literals

from ..symbols import ORTH, ENT_TYPE, LOWER


ENT_ID = "ent_id"
ENTITY_RULES = []


for name, tag, patterns in [
    ("Reddit", "PRODUCT", [[{LOWER: "reddit"}]]),
    ("Linux", "PRODUCT", [[{LOWER: "linux"}]]),
    ("Haskell", "PRODUCT", [[{LOWER: "haskell"}]]),
    ("HaskellCurry", "PERSON", [[{LOWER: "haskell"}, {LOWER: "curry"}]]),
    ("Javascript", "PRODUCT", [[{LOWER: "javascript"}]]),
    ("CSS", "PRODUCT", [[{LOWER: "css"}], [{LOWER: "css3"}]]),
    ("HTML", "PRODUCT", [[{LOWER: "html"}], [{LOWER: "html5"}]]),
    ("Python", "PRODUCT", [[{ORTH: "Python"}]]),
    ("Ruby", "PRODUCT", [[{ORTH: "Ruby"}]]),
    ("spaCy", "PRODUCT", [[{LOWER: "spacy"}]]),
    ("displaCy", "PRODUCT", [[{LOWER: "displacy"}]]),
    ("Digg", "PRODUCT", [[{LOWER: "digg"}]]),
    ("FoxNews", "ORG", [[{LOWER: "foxnews"}], [{LOWER: "fox"}, {LOWER: "news"}]]),
    ("Google", "ORG", [[{LOWER: "google"}]]),
    ("Mac", "PRODUCT", [[{LOWER: "mac"}]]),
    ("Wikipedia", "PRODUCT", [[{LOWER: "wikipedia"}]]),
    ("Windows", "PRODUCT", [[{LOWER: "windows"}]]),
    ("Dell", "ORG", [[{LOWER: "dell"}]]),
    ("Facebook", "ORG", [[{LOWER: "facebook"}]]),
    ("Blizzard", "ORG", [[{LOWER: "blizzard"}]]),
    ("Ubuntu", "ORG", [[{LOWER: "ubuntu"}]]),
    ("YouTube", "PRODUCT", [[{LOWER: "youtube"}]]),]:
    ENTITY_RULES.append({ENT_ID: name, 'attrs': {ENT_TYPE: tag}, 'patterns': patterns})


FALSE_POSITIVES = [
    [{ORTH: "Shit"}],
    [{ORTH: "Weed"}],
    [{ORTH: "Cool"}],
    [{ORTH: "Btw"}],
    [{ORTH: "Bah"}],
    [{ORTH: "Bullshit"}],
    [{ORTH: "Lol"}],
    [{ORTH: "Yo"}, {LOWER: "dawg"}],
    [{ORTH: "Yay"}],
    [{ORTH: "Ahh"}],
    [{ORTH: "Yea"}],
    [{ORTH: "Bah"}]
]
