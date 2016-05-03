from __future__ import unicode_literals

import pytest
import numpy

from spacy.attrs import HEAD, DEP
from spacy.symbols import root, det, compound, nsubjpass, aux, auxpass, punct, nsubj, cc, amod, conj, advmod, attr, prep, pobj


@pytest.mark.models
class TestNounChunks:
    @pytest.fixture(scope="class")
    def ex1_en(self, EN):
        example = EN.tokenizer.tokens_from_list('A base phrase should be recognized .'.split(' '))
        EN.tagger.tag_from_strings(example, 'DT NN NN MD VB VBN .'.split(' '))
        example.from_array([HEAD, DEP],
        numpy.asarray(
            [
                [2, det],
                [1, compound],
                [3, nsubjpass],
                [2, aux],
                [1, auxpass],
                [0, root],
                [-1, punct]
            ], dtype='int32'))
        return example

    @pytest.fixture(scope="class")
    def ex2_en(self, EN):
        example = EN.tokenizer.tokens_from_list('A base phrase and a good phrase are often the same .'.split(' '))
        EN.tagger.tag_from_strings(example, 'DT NN NN CC DT JJ NN VBP RB DT JJ .'.split(' '))
        example.from_array([HEAD, DEP],
        numpy.asarray(
            [
                [2, det],
                [1, compound],
                [5, nsubj],
                [-1, cc],
                [1, det],
                [1, amod],
                [-4, conj],
                [0, root],
                [-1, advmod],
                [1, det],
                [-3, attr],
                [-4, punct]
            ], dtype='int32'))
        return example

    @pytest.fixture(scope="class")
    def ex3_en(self, EN):
        example = EN.tokenizer.tokens_from_list('A phrase with another phrase occurs .'.split(' '))
        EN.tagger.tag_from_strings(example, 'DT NN IN DT NN VBZ .'.split(' '))
        example.from_array([HEAD, DEP],
        numpy.asarray(
            [
                [1, det],
                [4, nsubj],
                [-1, prep],
                [1, det],
                [-2, pobj],
                [0, root],
                [-1, punct]
            ], dtype='int32'))
        return example

    # @pytest.fixture(score="class")
    # def ex1_de(self, DE):
    #     example = EN.tokenizer.tokens_from_list('Eine Tasse steht auf dem Tisch .'.split(' '))
    #     EN.tagger.tag_from_strings(example, 'ART NN VVFIN APPR ART NN $.'.split(' '))
    #     example.from_array([HEAD, DEP],
    #     numpy.asarray(
    #         [
    #             [1, det],
    #             [4, nsubj],
    #             [-1, prep],
    #             [1, det],
    #             [-2, pobj],
    #             [0, root],
    #             [-1, punct]
    #         ], dtype='int32'))
    #     return example

    def test_en_standard_chunk(self, ex1_en):
        chunks = list(ex1_en.noun_chunks)
        assert len(chunks) == 1
        assert chunks[0].string == 'A base phrase '

    def test_en_coordinated_chunks(self, ex2_en):
        chunks = list(ex2_en.noun_chunks)
        assert len(chunks) == 2
        assert chunks[0].string == 'A base phrase '
        assert chunks[1].string == 'a good phrase '

    def test_en_pp_chunks(self, ex3_en):
        chunks = list(ex3_en.noun_chunks)
        assert len(chunks) == 2
        assert chunks[0].string == 'A phrase '
        assert chunks[1].string == 'another phrase '
