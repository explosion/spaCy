# coding: utf8
from __future__ import unicode_literals

import pytest

TESTCASES = []

PUNCTUATION_TESTS = [
    (u'আমি বাংলায় গান গাই!', [u'আমি', u'বাংলায়', u'গান', u'গাই', u'!']),
    (u'আমি বাংলায় কথা কই।', [u'আমি', u'বাংলায়', u'কথা', u'কই', u'।']),
    (u'বসুন্ধরা জনসম্মুখে দোষ স্বীকার করলো না?', [u'বসুন্ধরা', u'জনসম্মুখে', u'দোষ', u'স্বীকার', u'করলো', u'না', u'?']),
    (u'টাকা থাকলে কি না হয়!', [u'টাকা', u'থাকলে', u'কি', u'না', u'হয়', u'!']),
]

ABBREVIATIONS = [
    (u'ডঃ খালেদ বললেন ঢাকায় ৩৫ ডিগ্রি সে.।', [u'ডঃ', u'খালেদ', u'বললেন', u'ঢাকায়', u'৩৫', u'ডিগ্রি', u'সে.', u'।'])
]

TESTCASES.extend(PUNCTUATION_TESTS)
TESTCASES.extend(ABBREVIATIONS)


@pytest.mark.parametrize('text,expected_tokens', TESTCASES)
def test_tokenizer_handles_testcases(bn_tokenizer, text, expected_tokens):
    tokens = bn_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


def test_tokenizer_handles_long_text(bn_tokenizer):
    text = u"""নর্থ সাউথ বিশ্ববিদ্যালয়ে সারাবছর কোন না কোন বিষয়ে গবেষণা চলতেই থাকে। \
অভিজ্ঞ ফ্যাকাল্টি মেম্বারগণ প্রায়ই শিক্ষার্থীদের নিয়ে বিভিন্ন গবেষণা প্রকল্পে কাজ করেন, \
যার মধ্যে রয়েছে রোবট থেকে মেশিন লার্নিং সিস্টেম ও আর্টিফিশিয়াল ইন্টেলিজেন্স। \
এসকল প্রকল্পে কাজ করার মাধ্যমে সংশ্লিষ্ট ক্ষেত্রে যথেষ্ঠ পরিমাণ স্পেশালাইজড হওয়া সম্ভব। \
আর গবেষণার কাজ তোমার ক্যারিয়ারকে ঠেলে নিয়ে যাবে অনেকখানি! \
কন্টেস্ট প্রোগ্রামার হও, গবেষক কিংবা ডেভেলপার - নর্থ সাউথ ইউনিভার্সিটিতে তোমার প্রতিভা বিকাশের সুযোগ রয়েছেই। \
নর্থ সাউথের অসাধারণ কমিউনিটিতে তোমাকে সাদর আমন্ত্রণ।"""

    tokens = bn_tokenizer(text)
    assert len(tokens) == 84
