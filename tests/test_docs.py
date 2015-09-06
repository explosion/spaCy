# -*- coding: utf-8 -*-
"""Sphinx doctest is just too hard. Manually paste doctest examples here"""
import pytest

#@pytest.mark.models
#def test_1():
#    import spacy.en
#    from spacy.parts_of_speech import ADV
#    # Load the pipeline, and call it with some text.
#    nlp = spacy.en.English()
#    tokens = nlp(u"‘Give it back,’ he pleaded abjectly, ‘it’s mine.’",
#                tag=True, parse=False)
#    o = u''.join(tok.string.upper() if tok.pos == ADV else tok.string for tok in tokens)
#    assert u"‘Give it BACK,’ he pleaded ABJECTLY, ‘it’s mine.’"
#
#    o = nlp.vocab[u'back'].prob
#    assert o == -7.033305644989014
#    o = nlp.vocab[u'not'].prob
#    assert o == -5.332601070404053
#    o = nlp.vocab[u'quietly'].prob
#    assert o == -11.994928359985352
#
#
#@pytest.mark.m
#def test2():
#    import spacy.en
#    from spacy.parts_of_speech import ADV
#    nlp = spacy.en.English()
#    # Find log probability of Nth most frequent word
#    probs = [lex.prob for lex in nlp.vocab]
#    probs.sort()
#    is_adverb = lambda tok: tok.pos == ADV and tok.prob < probs[-1000]
#    tokens = nlp(u"‘Give it back,’ he pleaded abjectly, ‘it’s mine.’")
#    o = u''.join(tok.string.upper() if is_adverb(tok) else tok.string for tok in tokens)
#    o == u'‘Give it back,’ he pleaded ABJECTLY, ‘it’s mine.’'
#
#@pytest.mark.models
#def test3():
#    import spacy.en
#    from spacy.parts_of_speech import ADV
#    nlp = spacy.en.English()
#    # Find log probability of Nth most frequent word
#    probs = [lex.prob for lex in nlp.vocab]
#    probs.sort()
#    is_adverb = lambda tok: tok.pos == ADV and tok.prob < probs[-1000]
#    tokens = nlp(u"‘Give it back,’ he pleaded abjectly, ‘it’s mine.’")
#    o = u''.join(tok.string.upper() if is_adverb(tok) else tok.string for tok in tokens)
#    assert o == u'‘Give it back,’ he pleaded ABJECTLY, ‘it’s mine.’'
#
#    pleaded = tokens[7]
#    assert pleaded.repvec.shape == (300,)
#    o = pleaded.repvec[:5]
#    assert sum(o) != 0
#    from numpy import dot
#    from numpy.linalg import norm
#
#    cosine = lambda v1, v2: dot(v1, v2) / (norm(v1) * norm(v2))
#    words = [w for w in nlp.vocab if w.is_lower and w.has_repvec]
#    words.sort(key=lambda w: cosine(w.repvec, pleaded.repvec))
#    words.reverse()
#    o = [w.orth_ for w in words[0:20]]
#    assert o == [u'pleaded', u'pled', u'plead', u'confessed', u'interceded',
#                 u'pleads', u'testified', u'conspired', u'motioned', u'demurred',
#                 u'countersued', u'remonstrated', u'begged', u'apologised',
#                 u'consented', u'acquiesced', u'petitioned', u'quarreled',
#                 u'appealed', u'pleading']
#    o = [w.orth_ for w in words[50:60]]
#    assert o == [u'martialed', u'counselled', u'bragged',
#                 u'backtracked', u'caucused', u'refiled', u'dueled', u'mused',
#                 u'dissented', u'yearned']
#    o = [w.orth_ for w in words[100:110]]
#    assert o == [u'acquits', u'cabled', u'ducked', u'sentenced',
#                 u'gaoled', u'perjured', u'absconded', u'bargained', u'overstayed',
#                 u'clerked']
#    
#    #o = [w.orth_ for w in words[1000:1010]]
#    #assert o == [u'scorned', u'baled', u'righted', u'requested', u'swindled',
#    #             u'posited', u'firebombed', u'slimed', u'deferred', u'sagged']
#    #o = [w.orth_ for w in words[50000:50010]]
#    #assert o == [u'fb', u'ford', u'systems', u'puck', u'anglers', u'ik', u'tabloid',
#    #             u'dirty', u'rims', u'artists']
