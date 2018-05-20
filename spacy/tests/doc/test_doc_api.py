# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc
from ...tokens import Doc
from ...vocab import Vocab
from ...attrs import LEMMA

import pytest
import numpy


@pytest.mark.parametrize('text', [["one", "two", "three"]])
def test_doc_api_compare_by_string_position(en_vocab, text):
    doc = get_doc(en_vocab, text)
    # Get the tokens in this order, so their ID ordering doesn't match the idx
    token3 = doc[-1]
    token2 = doc[-2]
    token1 = doc[-1]
    token1, token2, token3 = doc
    assert token1 < token2 < token3
    assert not token1 > token2
    assert token2 > token1
    assert token2 <= token3
    assert token3 >= token1


def test_doc_api_getitem(en_tokenizer):
    text = "Give it back! He pleaded."
    tokens = en_tokenizer(text)
    assert tokens[0].text == 'Give'
    assert tokens[-1].text == '.'
    with pytest.raises(IndexError):
        tokens[len(tokens)]

    def to_str(span):
        return '/'.join(token.text for token in span)

    span = tokens[1:1]
    assert not to_str(span)
    span = tokens[1:4]
    assert to_str(span) == 'it/back/!'
    span = tokens[1:4:1]
    assert to_str(span) == 'it/back/!'
    with pytest.raises(ValueError):
        tokens[1:4:2]
    with pytest.raises(ValueError):
        tokens[1:4:-1]

    span = tokens[-3:6]
    assert to_str(span) == 'He/pleaded'
    span = tokens[4:-1]
    assert to_str(span) == 'He/pleaded'
    span = tokens[-5:-3]
    assert to_str(span) == 'back/!'
    span = tokens[5:4]
    assert span.start == span.end == 5 and not to_str(span)
    span = tokens[4:-3]
    assert span.start == span.end == 4 and not to_str(span)

    span = tokens[:]
    assert to_str(span) == 'Give/it/back/!/He/pleaded/.'
    span = tokens[4:]
    assert to_str(span) == 'He/pleaded/.'
    span = tokens[:4]
    assert to_str(span) == 'Give/it/back/!'
    span = tokens[:-3]
    assert to_str(span) == 'Give/it/back/!'
    span = tokens[-3:]
    assert to_str(span) == 'He/pleaded/.'

    span = tokens[4:50]
    assert to_str(span) == 'He/pleaded/.'
    span = tokens[-50:4]
    assert to_str(span) == 'Give/it/back/!'
    span = tokens[-50:-40]
    assert span.start == span.end == 0 and not to_str(span)
    span = tokens[40:50]
    assert span.start == span.end == 7 and not to_str(span)

    span = tokens[1:4]
    assert span[0].orth_ == 'it'
    subspan = span[:]
    assert to_str(subspan) == 'it/back/!'
    subspan = span[:2]
    assert to_str(subspan) == 'it/back'
    subspan = span[1:]
    assert to_str(subspan) == 'back/!'
    subspan = span[:-1]
    assert to_str(subspan) == 'it/back'
    subspan = span[-2:]
    assert to_str(subspan) == 'back/!'
    subspan = span[1:2]
    assert to_str(subspan) == 'back'
    subspan = span[-2:-1]
    assert to_str(subspan) == 'back'
    subspan = span[-50:50]
    assert to_str(subspan) == 'it/back/!'
    subspan = span[50:-50]
    assert subspan.start == subspan.end == 4 and not to_str(subspan)


@pytest.mark.parametrize('text', ["Give it back! He pleaded.",
                                  " Give it back! He pleaded. "])
def test_doc_api_serialize(en_tokenizer, text):
    tokens = en_tokenizer(text)
    new_tokens = get_doc(tokens.vocab).from_bytes(tokens.to_bytes())
    assert tokens.text == new_tokens.text
    assert [t.text for t in tokens] == [t.text for t in new_tokens]
    assert [t.orth for t in tokens] == [t.orth for t in new_tokens]

    new_tokens = get_doc(tokens.vocab).from_bytes(
        tokens.to_bytes(tensor=False), tensor=False)
    assert tokens.text == new_tokens.text
    assert [t.text for t in tokens] == [t.text for t in new_tokens]
    assert [t.orth for t in tokens] == [t.orth for t in new_tokens]

    new_tokens = get_doc(tokens.vocab).from_bytes(
        tokens.to_bytes(sentiment=False), sentiment=False)
    assert tokens.text == new_tokens.text
    assert [t.text for t in tokens] == [t.text for t in new_tokens]
    assert [t.orth for t in tokens] == [t.orth for t in new_tokens]


def test_doc_api_set_ents(en_tokenizer):
    text = "I use goggle chrone to surf the web"
    tokens = en_tokenizer(text)
    assert len(tokens.ents) == 0
    tokens.ents = [(tokens.vocab.strings['PRODUCT'], 2, 4)]
    assert len(list(tokens.ents)) == 1
    assert [t.ent_iob for t in tokens] == [0, 0, 3, 1, 0, 0, 0, 0]
    assert tokens.ents[0].label_ == 'PRODUCT'
    assert tokens.ents[0].start == 2
    assert tokens.ents[0].end == 4


def test_doc_api_merge(en_tokenizer):
    text = "WKRO played songs by the beach boys all night"

    # merge 'The Beach Boys'
    doc = en_tokenizer(text)
    assert len(doc) == 9
    doc.merge(doc[4].idx, doc[6].idx + len(doc[6]), tag='NAMED', lemma='LEMMA',
              ent_type='TYPE')
    assert len(doc) == 7
    assert doc[4].text == 'the beach boys'
    assert doc[4].text_with_ws == 'the beach boys '
    assert doc[4].tag_ == 'NAMED'

    # merge 'all night'
    doc = en_tokenizer(text)
    assert len(doc) == 9
    doc.merge(doc[7].idx, doc[8].idx + len(doc[8]), tag='NAMED', lemma='LEMMA',
              ent_type='TYPE')
    assert len(doc) == 8
    assert doc[7].text == 'all night'
    assert doc[7].text_with_ws == 'all night'


def test_doc_api_merge_children(en_tokenizer):
    """Test that attachments work correctly after merging."""
    text = "WKRO played songs by the beach boys all night"
    doc = en_tokenizer(text)
    assert len(doc) == 9
    doc.merge(doc[4].idx, doc[6].idx + len(doc[6]), tag='NAMED', lemma='LEMMA',
              ent_type='TYPE')

    for word in doc:
        if word.i < word.head.i:
            assert word in list(word.head.lefts)
        elif word.i > word.head.i:
            assert word in list(word.head.rights)


def test_doc_api_merge_hang(en_tokenizer):
    text = "through North and South Carolina"
    doc = en_tokenizer(text)
    doc.merge(18, 32, tag='', lemma='', ent_type='ORG')
    doc.merge(8, 32, tag='', lemma='', ent_type='ORG')


def test_doc_api_retokenizer(en_tokenizer):
    doc = en_tokenizer("WKRO played songs by the beach boys all night")
    with doc.retokenize() as retokenizer:
        retokenizer.merge(doc[4:7])
    assert len(doc) == 7
    assert doc[4].text == 'the beach boys'


def test_doc_api_retokenizer_attrs(en_tokenizer):
    doc = en_tokenizer("WKRO played songs by the beach boys all night")
    # test both string and integer attributes and values
    attrs = {LEMMA: 'boys', 'ENT_TYPE': doc.vocab.strings['ORG']}
    with doc.retokenize() as retokenizer:
        retokenizer.merge(doc[4:7], attrs=attrs)
    assert len(doc) == 7
    assert doc[4].text == 'the beach boys'
    assert doc[4].lemma_ == 'boys'
    assert doc[4].ent_type_ == 'ORG'


def test_doc_api_sents_empty_string(en_tokenizer):
    doc = en_tokenizer("")
    doc.is_parsed = True
    sents = list(doc.sents)
    assert len(sents) == 0


def test_doc_api_runtime_error(en_tokenizer):
    # Example that caused run-time error while parsing Reddit
    text = "67% of black households are single parent \n\n72% of all black babies born out of wedlock \n\n50% of all black kids don\u2019t finish high school"
    deps = ['nsubj', 'prep', 'amod', 'pobj', 'ROOT', 'amod', 'attr', '',
            'nummod', 'prep', 'det', 'amod', 'pobj', 'acl', 'prep', 'prep',
            'pobj', '', 'nummod', 'prep', 'det', 'amod', 'pobj', 'aux', 'neg',
            'ROOT', 'amod', 'dobj']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], deps=deps)

    nps = []
    for np in doc.noun_chunks:
        while len(np) > 1 and np[0].dep_ not in ('advmod', 'amod', 'compound'):
            np = np[1:]
        if len(np) > 1:
            nps.append((np.start_char, np.end_char, np.root.tag_, np.text, np.root.ent_type_))
    for np in nps:
        start, end, tag, lemma, ent_type = np
        doc.merge(start, end, tag=tag, lemma=lemma, ent_type=ent_type)


def test_doc_api_right_edge(en_tokenizer):
    """Test for bug occurring from Unshift action, causing incorrect right edge"""
    text = "I have proposed to myself, for the sake of such as live under the government of the Romans, to translate those books into the Greek tongue."
    heads = [2, 1, 0, -1, -1, -3, 15, 1, -2, -1, 1, -3, -1, -1, 1, -2, -1, 1,
             -2, -7, 1, -19, 1, -2, -3, 2, 1, -3, -26]

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)
    assert doc[6].text == 'for'
    subtree = [w.text for w in doc[6].subtree]
    assert subtree == ['for', 'the', 'sake', 'of', 'such', 'as',
                       'live', 'under', 'the', 'government', 'of', 'the', 'Romans', ',']
    assert doc[6].right_edge.text == ','


def test_doc_api_has_vector():
    vocab = Vocab()
    vocab.reset_vectors(width=2)
    vocab.set_vector('kitten', vector=numpy.asarray([0., 2.], dtype='f'))
    doc = Doc(vocab, words=['kitten'])
    assert doc.has_vector


def test_doc_api_similarity_match():
    doc = Doc(Vocab(), words=['a'])
    assert doc.similarity(doc[0]) == 1.0
    assert doc.similarity(doc.vocab['a']) == 1.0
    doc2 = Doc(doc.vocab, words=['a', 'b', 'c'])
    assert doc.similarity(doc2[:1]) == 1.0
    assert doc.similarity(doc2) == 0.0


def test_lowest_common_ancestor(en_tokenizer):
    tokens = en_tokenizer('the lazy dog slept')
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=[2, 1, 1, 0])
    lca = doc.get_lca_matrix()
    assert(lca[1, 1] == 1)
    assert(lca[0, 1] == 2)
    assert(lca[1, 2] == 2)


def test_parse_tree(en_tokenizer):
    """Tests doc.print_tree() method."""
    text = 'I like New York in Autumn.'
    heads = [1, 0, 1, -2, -3, -1, -5]
    tags = ['PRP', 'IN', 'NNP', 'NNP', 'IN', 'NNP', '.']
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads, tags=tags)
    # full method parse_tree(text) is a trivial composition
    trees = doc.print_tree()
    assert len(trees) > 0
    tree = trees[0]
    assert all(k in list(tree.keys()) for k in ['word', 'lemma', 'NE', 'POS_fine', 'POS_coarse', 'arc', 'modifiers'])
    assert tree['word'] == 'like' # check root is correct
