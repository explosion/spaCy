# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from .util import ENT_ID


ENTITY_RULES = [
    {
        ENT_ID: "Reddit",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "reddit"}]
        ]
    },

    {
        ENT_ID: "Linux",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "linux"}]
        ]
    },

    {
        ENT_ID: "Haskell",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "haskell"}],
        ]
    },

    {
        ENT_ID: "HaskellCurry",
        "attrs": {ENT_TYPE: "PERSON"},
        "patterns": [
            [{LOWER: "haskell"}, {LOWER: "curry"}]
        ]
    },

    {
        ENT_ID: "Javascript",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "javascript"}],
        ]
    },

    {
        ENT_ID: "CSS",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "css"}],
            [{LOWER: "css3"}],
        ]
    },

    {
        ENT_ID: "HTML",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "html"}],
            [{LOWER: "html5"}],
        ]
    },

    {
        ENT_ID: "Python",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{ORTH: "Python"}]
        ]
    },

    {
        ENT_ID: "Ruby",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{ORTH: "Ruby"}]
        ]
    },

    {
        ENT_ID: "spaCy",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "spacy"}]
        ]
    },

    {
        ENT_ID: "displaCy",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "displacy"}]
        ]
    },

    {
        ENT_ID: "Digg",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "digg"}]
        ]
    },

    {
        ENT_ID: "FoxNews",
        "attrs": {ENT_TYPE: "ORG"},
        "patterns": [
            [{LOWER: "foxnews"}],
            [{LOWER: "fox"}, {LOWER: "news"}]
        ]
    },

    {
        ENT_ID: "Google",
        "attrs": {ENT_TYPE: "ORG"},
        "patterns": [
            [{LOWER: "google"}]
        ]
    },

    {
        ENT_ID: "Mac",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "mac"}]
        ]
    },

    {
        ENT_ID: "Wikipedia",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "wikipedia"}]
        ]
    },

    {
        ENT_ID: "Windows",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{ORTH: "Windows"}]
        ]
    },

    {
        ENT_ID: "Dell",
        "attrs": {ENT_TYPE: "ORG"},
        "patterns": [
            [{LOWER: "dell"}]
        ]
    },

    {
        ENT_ID: "Facebook",
        "attrs": {ENT_TYPE: "ORG"},
        "patterns": [
            [{LOWER: "facebook"}]
        ]
    },

    {
        ENT_ID: "Blizzard",
        "attrs": {ENT_TYPE: "ORG"},
        "patterns": [
            [{ORTH: "Blizzard"}]
        ]
    },

    {
        ENT_ID: "Ubuntu",
        "attrs": {ENT_TYPE: "ORG"},
        "patterns": [
            [{ORTH: "Ubuntu"}]
        ]
    },

    {
        ENT_ID: "YouTube",
        "attrs": {ENT_TYPE: "PRODUCT"},
        "patterns": [
            [{LOWER: "youtube"}]
        ]
    }
]


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


__all__ = ["ENTITY_RULES", "FALSE_POSITIVES"]
