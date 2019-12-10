# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.tokenizer import Tokenizer
from spacy import util

from ..util import make_tempdir


def test_issue4190():
    test_string = "Test c."
    # Load default language
    nlp_1 = English()
    doc_1a = nlp_1(test_string)
    result_1a = [token.text for token in doc_1a]  # noqa: F841
    # Modify tokenizer
    customize_tokenizer(nlp_1)
    doc_1b = nlp_1(test_string)
    result_1b = [token.text for token in doc_1b]
    # Save and Reload
    with make_tempdir() as model_dir:
        nlp_1.to_disk(model_dir)
        nlp_2 = util.load_model(model_dir)
    # This should be the modified tokenizer
    doc_2 = nlp_2(test_string)
    result_2 = [token.text for token in doc_2]
    assert result_1b == result_2


def customize_tokenizer(nlp):
    prefix_re = util.compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = util.compile_suffix_regex(nlp.Defaults.suffixes)
    infix_re = util.compile_infix_regex(nlp.Defaults.infixes)
    # Remove all exceptions where a single letter is followed by a period (e.g. 'h.')
    exceptions = {
        k: v
        for k, v in dict(nlp.Defaults.tokenizer_exceptions).items()
        if not (len(k) == 2 and k[1] == ".")
    }
    new_tokenizer = Tokenizer(
        nlp.vocab,
        exceptions,
        prefix_search=prefix_re.search,
        suffix_search=suffix_re.search,
        infix_finditer=infix_re.finditer,
        token_match=nlp.tokenizer.token_match,
    )
    nlp.tokenizer = new_tokenizer
