import pytest

# fmt: off
TOKENIZER_TESTS = [("서울 타워 근처에 살고 있습니다.", "서울 타워 근처 에 살 고 있 습니다 ."),
                   ("영등포구에 있는 맛집 좀 알려주세요.", "영등포구 에 있 는 맛집 좀 알려 주 세요 ."),
                   ("10$ 할인코드를 적용할까요?", "10 $ 할인 코드 를 적용 할까요 ?")]

TAG_TESTS = [("서울 타워 근처에 살고 있습니다.",
              "NNP NNG NNG JKB VV EC VX EF SF"),
             ("영등포구에 있는 맛집 좀 알려주세요.",
              "NNP JKB VV ETM NNG MAG VV VX EP SF")]

FULL_TAG_TESTS = [("영등포구에 있는 맛집 좀 알려주세요.",
                   "NNP JKB VV ETM NNG MAG VV+EC VX EP+EF SF")]

POS_TESTS = [("서울 타워 근처에 살고 있습니다.",
              "PROPN NOUN NOUN ADP VERB X AUX X PUNCT"),
             ("영등포구에 있는 맛집 좀 알려주세요.",
              "PROPN ADP VERB X NOUN ADV VERB AUX X PUNCT")]
# fmt: on


@pytest.mark.parametrize("text,expected_tokens", TOKENIZER_TESTS)
def test_ko_tokenizer(ko_tokenizer, text, expected_tokens):
    tokens = [token.text for token in ko_tokenizer(text)]
    assert tokens == expected_tokens.split()


@pytest.mark.parametrize("text,expected_tags", TAG_TESTS)
def test_ko_tokenizer_tags(ko_tokenizer, text, expected_tags):
    tags = [token.tag_ for token in ko_tokenizer(text)]
    assert tags == expected_tags.split()


@pytest.mark.parametrize("text,expected_tags", FULL_TAG_TESTS)
def test_ko_tokenizer_full_tags(ko_tokenizer, text, expected_tags):
    tags = ko_tokenizer(text).user_data["full_tags"]
    assert tags == expected_tags.split()


@pytest.mark.parametrize("text,expected_pos", POS_TESTS)
def test_ko_tokenizer_pos(ko_tokenizer, text, expected_pos):
    pos = [token.pos_ for token in ko_tokenizer(text)]
    assert pos == expected_pos.split()


def test_ko_empty_doc(ko_tokenizer):
    tokens = ko_tokenizer("")
    assert len(tokens) == 0


@pytest.mark.issue(10535)
def test_ko_tokenizer_unknown_tag(ko_tokenizer):
    tokens = ko_tokenizer("미닛 리피터")
    assert tokens[1].pos_ == "X"


# fmt: off
SPACY_TOKENIZER_TESTS = [
    ("있다.", "있다 ."),
    ("'예'는", "' 예 ' 는"),
    ("부 (富) 는", "부 ( 富 ) 는"),
    ("부(富)는", "부 ( 富 ) 는"),
    ("1982~1983.", "1982 ~ 1983 ."),
    ("사과·배·복숭아·수박은 모두 과일이다.", "사과 · 배 · 복숭아 · 수박은 모두 과일이다 ."),
    ("그렇구나~", "그렇구나~"),
    ("『9시 반의 당구』,", "『 9시 반의 당구 』 ,"),
]
# fmt: on


@pytest.mark.parametrize("text,expected_tokens", SPACY_TOKENIZER_TESTS)
def test_ko_spacy_tokenizer(ko_tokenizer_tokenizer, text, expected_tokens):
    tokens = [token.text for token in ko_tokenizer_tokenizer(text)]
    assert tokens == expected_tokens.split()
