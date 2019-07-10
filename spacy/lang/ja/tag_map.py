# encoding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, INTJ, X, ADJ, AUX, ADP, PART, CCONJ, SCONJ, NOUN
from ...symbols import SPACE, SYM, PRON, VERB, ADV, PROPN, NUM, DET


TAG_MAP = {
    # Universal Dependencies Mapping
    # (private repository)
    # https://github.com/mynlp/udjapanese/blob/master/UDJapaneseBCCWJ/unidic_to_udpos_mapping/bccwj_pos_suw_rule.json

    "記号-一般": {POS: SYM},
    "記号-文字": {POS: SYM},

    "感動詞-フィラー": {POS: INTJ},
    "感動詞-一般": {POS: INTJ},

    # spaces should be treated as token.whitespace_
    "空白": {POS: SPACE},

    "形状詞-一般": {POS: ADJ},
    "形状詞-タリ": {POS: ADJ},
    "形状詞-助動詞語幹": {POS: ADJ},
    "形容詞-一般": {POS: ADJ},
    "形容詞-非自立可能": {POS: ADJ},  # All the root tokens are ADJ

    "助詞-格助詞": {POS: ADP},
    "助詞-係助詞": {POS: ADP},
    "助詞-終助詞": {POS: PART},
    "助詞-準体助詞": {POS: SCONJ},
    "助詞-接続助詞": {POS: CCONJ},
    "助詞-副助詞": {POS: ADP},
    "助動詞": {POS: AUX},
    "接続詞": {POS: SCONJ},

    "接頭辞": {POS: NOUN},
    "接尾辞-形状詞的": {POS: NOUN},
    "接尾辞-形容詞的": {POS: NOUN},
    "接尾辞-動詞的": {POS: NOUN},
    "接尾辞-名詞的-サ変可能": {POS: NOUN},  # All the root tokens are NOUN
    "接尾辞-名詞的-一般": {POS: NOUN},
    "接尾辞-名詞的-助数詞": {POS: NOUN},
    "接尾辞-名詞的-副詞可能": {POS: NOUN},  # All the root tokens are NOUN

    "代名詞": {POS: PRON},
    "動詞-一般": {POS: VERB},
    "動詞-非自立可能": {POS: VERB},  # All the root tokens are VERB except the tokens lemma is '為る' and POS is AUX
    "副詞": {POS: ADV},

    "補助記号-ＡＡ-一般": {POS: SYM},  # text art
    "補助記号-ＡＡ-顔文字": {POS: SYM},  # kaomoji
    "補助記号-一般": {POS: PUNCT},
    "補助記号-括弧開": {POS: PUNCT},  # open bracket
    "補助記号-括弧閉": {POS: PUNCT},  # close bracket
    "補助記号-句点": {POS: PUNCT},  # period or other EOS marker
    "補助記号-読点": {POS: PUNCT},  # comma

    "名詞-固有名詞-一般": {POS: PROPN},  # general proper noun
    "名詞-固有名詞-人名-一般": {POS: PROPN},  # person's name
    "名詞-固有名詞-人名-姓": {POS: PROPN},  # surname
    "名詞-固有名詞-人名-名": {POS: PROPN},  # first name
    "名詞-固有名詞-地名-一般": {POS: PROPN},  # place name
    "名詞-固有名詞-地名-国": {POS: PROPN},  # country name

    "名詞-助動詞語幹": {POS: AUX},
    "名詞-数詞": {POS: NUM},  # includes Chinese numerals

    "名詞-普通名詞-サ変可能": {POS: NOUN},  # ADJ=3349 and VERB=3411 for root

    "名詞-普通名詞-サ変形状詞可能": {POS: NOUN},  # ADJ=40 and NOUN=30 for root
    "名詞-普通名詞-一般": {POS: NOUN},
    "名詞-普通名詞-形状詞可能": {POS: ADJ},  # ADJ=404 and NOUN=161 for root
    "名詞-普通名詞-助数詞可能": {POS: NOUN},  # All the root tokens are NOUN
    "名詞-普通名詞-副詞可能": {POS: NOUN},  # All the root tokens are NOUN

    "連体詞": {POS: DET},
}
