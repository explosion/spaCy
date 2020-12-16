# coding: utf8
from __future__ import unicode_literals


# Stop words
STOP_WORDS = set(
    """
ግን አንቺ አንተ እናንተ ያንተ ያንቺ የናንተ ራስህን ራስሽን ራሳችሁን
""".split()
)

#contractions = ["n't", "'d", "'ll", "'m", "'re", "'s", "'ve"]
#STOP_WORDS.update(contractions)

#for apostrophe in ["‘", "’"]:
#    for stopword in contractions:
#        STOP_WORDS.add(stopword.replace("'", apostrophe))
