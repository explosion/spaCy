import os
import re

import pytest

from spacy.hu import Hungarian

_MODULE_PATH = os.path.dirname(__file__)


class TokenizerTestCase(object):
    INPUT_PREFIX = "IN :"
    OUTPUT_PREFIX = "OUT:"
    WORD_PATTERN = re.compile(r"<([wc])>([^<>]+)</\1>")

    def __init__(self, input_str, expected_words):
        self.input = input_str
        self.expected_tokens = expected_words

    def __repr__(self):
        return "TokenizerTestCase<input={}, words={}>".format(repr(self.input), self.expected_tokens)

    def to_tuple(self):
        return (self.input, self.expected_tokens)

    @classmethod
    def _parse_output_line(cls, line):
        for match in cls.WORD_PATTERN.finditer(line):
            yield match.group(2)

    @classmethod
    def read_from_file(cls, path):
        with open(path) as f:
            input_lines = []
            output_words = []
            last_type = None
            for line in f:
                if line.startswith(cls.INPUT_PREFIX):
                    if last_type == TokenizerTestCase.OUTPUT_PREFIX and input_lines:
                        yield TokenizerTestCase("\n".join(input_lines), output_words)
                        input_lines = []
                        output_words = []
                    input_lines.append(line[len(cls.INPUT_PREFIX):].strip())
                    last_type = TokenizerTestCase.INPUT_PREFIX
                elif line.startswith(cls.OUTPUT_PREFIX):
                    output_words.extend(list(cls._parse_output_line(line.strip())))
                    last_type = TokenizerTestCase.OUTPUT_PREFIX
                else:
                    # Comments separate test cases
                    if input_lines:
                        yield TokenizerTestCase("\n".join(input_lines), output_words)
                        input_lines = []
                        output_words = []
                    last_type = None


_DOTS_CASES = list(TokenizerTestCase.read_from_file(_MODULE_PATH + "/test_default_token_dots.txt"))


@pytest.fixture(scope="session")
def HU():
    return Hungarian()


@pytest.fixture(scope="module")
def hu_tokenizer(HU):
    return HU.tokenizer


@pytest.mark.parametrize(("test_case"), _DOTS_CASES)
def test_abbreviations(hu_tokenizer, test_case):
    tokens = hu_tokenizer(test_case.input)
    token_list = [token.orth_ for token in tokens if not token.is_space]
    assert test_case.expected_tokens == token_list, "{} was erronously tokenized as {}".format(test_case, token_list)
