# -*- coding: utf-8 -*-
import pytest
import numpy


@pytest.mark.models
class TestModelSanity:
    """
    This is to make sure the model works as expected. The tests make sure that
    values are properly set.
    Tests are not meant to evaluate the content of the output, only make sure
    the output is formally okay.
    """
    @pytest.fixture(scope='class', params=['en','de'])
    def example(self, request, EN, DE):
        assert EN.entity != None
        assert DE.entity != None
        if request.param == 'en':
            doc = EN(u'There was a stranger standing at the big ' +
                      u'street talking to herself.')
        elif request.param == 'de':
            doc = DE(u'An der großen Straße stand eine merkwürdige ' +
                u'Gestalt und führte Selbstgespräche.')
        return doc

    def test_tokenization(self, example):
        # tokenization should split the document into tokens
        assert len(example) > 1

    def test_tagging(self, example):
        # if tagging was done properly, pos tags shouldn't be empty
        assert example.is_tagged
        assert all( t.pos != 0 for t in example )
        assert all( t.tag != 0 for t in example )

    def test_parsing(self, example):
        # if parsing was done properly
        # - dependency labels shouldn't be empty
        # - the head of some tokens should not be root
        assert example.is_parsed
        assert all( t.dep != 0 for t in example )
        assert any( t.dep != i for i,t in enumerate(example) )

    def test_ner(self, example):
        # if ner was done properly, ent_iob shouldn't be empty
        assert all([t.ent_iob != 0 for t in example])

    def test_vectors(self, example):
        # if vectors are available, they should differ on different words
        # this isn't a perfect test since this could in principle fail 
        # in a sane model as well,
        # but that's very unlikely and a good indicator if something is wrong
        vector0 = example[0].vector
        vector1 = example[1].vector
        vector2 = example[2].vector
        assert not numpy.array_equal(vector0,vector1)
        assert not numpy.array_equal(vector0,vector2)
        assert not numpy.array_equal(vector1,vector2)

    def test_probs(self, example):
        # if frequencies/probabilities are okay, they should differ for 
        # different words
        # this isn't a perfect test since this could in principle fail 
        # in a sane model as well,
        # but that's very unlikely and a good indicator if something is wrong
        prob0 = example[0].prob
        prob1 = example[1].prob
        prob2 = example[2].prob
        assert not prob0 == prob1
        assert not prob0 == prob2
        assert not prob1 == prob2
