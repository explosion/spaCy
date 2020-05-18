# encoding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, INTJ, X, ADJ, AUX, ADP, PART, CCONJ, SCONJ, NOUN
from ...symbols import SYM, PRON, VERB, ADV, PROPN, NUM, DET, SPACE


TAG_MAP = {
    # Explanation of Unidic tags:
    # https://www.gavo.t.u-tokyo.ac.jp/~mine/japanese/nlp+slp/UNIDIC_manual.pdf
    # Universal Dependencies Mapping: (Some of the entries in this mapping are updated to v2.6 in the list below)
    # http://universaldependencies.org/ja/overview/morphology.html
    # http://universaldependencies.org/ja/pos/all.html
    "記号-一般": {
        POS: NOUN
    },  # this includes characters used to represent sounds like ドレミ
    "記号-文字": {
        POS: NOUN
    },  # this is for Greek and Latin characters having some meanings, or used as symbols, as in math
    "感動詞-フィラー": {POS: INTJ},
    "感動詞-一般": {POS: INTJ},

    "空白": {POS: SPACE},

    "形状詞-一般": {POS: ADJ},
    "形状詞-タリ": {POS: ADJ},
    "形状詞-助動詞語幹": {POS: AUX},

    "形容詞-一般": {POS: ADJ},

    "形容詞-非自立可能": {POS: ADJ},  # XXX ADJ if alone, AUX otherwise

    "助詞-格助詞": {POS: ADP},

    "助詞-係助詞": {POS: ADP},

    "助詞-終助詞": {POS: PART},
    "助詞-準体助詞": {POS: SCONJ},  # の as in 走るのが速い
    "助詞-接続助詞": {POS: SCONJ},  # verb ending て0

    "助詞-副助詞": {POS: ADP},  # ばかり, つつ after a verb

    "助動詞": {POS: AUX},

    "接続詞": {POS: CCONJ},  # XXX: might need refinement
    "接頭辞": {POS: NOUN},
    "接尾辞-形状詞的": {POS: PART},  # がち, チック

    "接尾辞-形容詞的": {POS: AUX},  # -らしい

    "接尾辞-動詞的": {POS: PART},  # -じみ
    "接尾辞-名詞的-サ変可能": {POS: NOUN},  # XXX see 名詞,普通名詞,サ変可能,*
    "接尾辞-名詞的-一般": {POS: NOUN},
    "接尾辞-名詞的-助数詞": {POS: NOUN},
    "接尾辞-名詞的-副詞可能": {POS: NOUN},  # -後, -過ぎ

    "代名詞": {POS: PRON},

    "動詞-一般": {POS: VERB},

    "動詞-非自立可能": {POS: AUX},  # XXX VERB if alone, AUX otherwise

    "副詞": {POS: ADV},

    "補助記号-ＡＡ-一般": {POS: SYM},  # text art
    "補助記号-ＡＡ-顔文字": {POS: PUNCT},  # kaomoji

    "補助記号-一般": {POS: SYM},

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

    "名詞-普通名詞-サ変可能": {POS: NOUN},  # XXX: sometimes VERB in UDv2; suru-verb noun

    "名詞-普通名詞-サ変形状詞可能": {POS: NOUN},

    "名詞-普通名詞-一般": {POS: NOUN},

    "名詞-普通名詞-形状詞可能": {POS: NOUN},  # XXX: sometimes ADJ in UDv2

    "名詞-普通名詞-助数詞可能": {POS: NOUN},  # counter / unit

    "名詞-普通名詞-副詞可能": {POS: NOUN},

    "連体詞": {POS: DET},  # XXX this has exceptions based on literal token

    # GSD tags. These aren't in Unidic, but we need them for the GSD data.
    "外国語": {POS: PROPN},  # Foreign words

    "絵文字・記号等": {POS: SYM},  # emoji / kaomoji ^^;

}
