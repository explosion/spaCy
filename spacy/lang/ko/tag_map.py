from ...symbols import POS, PUNCT, INTJ, X, SYM, ADJ, AUX, ADP, CONJ, NOUN, PRON
from ...symbols import VERB, ADV, PROPN, NUM, DET

# 은전한닢(mecab-ko-dic)의 품사 태그를 universal pos tag로 대응시킴
# https://docs.google.com/spreadsheets/d/1-9blXKjtjeKZqsf4NzHeYJCrr49-nXeRF6D80udfcwY/edit#gid=589544265
# https://universaldependencies.org/u/pos/
TAG_MAP = {
    # J.{1,2} 조사
    "JKS": {POS: ADP},
    "JKC": {POS: ADP},
    "JKG": {POS: ADP},
    "JKO": {POS: ADP},
    "JKB": {POS: ADP},
    "JKV": {POS: ADP},
    "JKQ": {POS: ADP},
    "JX": {POS: ADP},  # 보조사
    "JC": {POS: CONJ},  # 접속 조사
    "MAJ": {POS: CONJ},  # 접속 부사
    "MAG": {POS: ADV},  # 일반 부사
    "MM": {POS: DET},  # 관형사
    "XPN": {POS: X},  # 접두사
    # XS. 접미사
    "XSN": {POS: X},
    "XSV": {POS: X},
    "XSA": {POS: X},
    "XR": {POS: X},  # 어근
    # E.{1,2} 어미
    "EP": {POS: X},
    "EF": {POS: X},
    "EC": {POS: X},
    "ETN": {POS: X},
    "ETM": {POS: X},
    "IC": {POS: INTJ},  # 감탄사
    "VV": {POS: VERB},  # 동사
    "VA": {POS: ADJ},  # 형용사
    "VX": {POS: AUX},  # 보조 용언
    "VCP": {POS: ADP},  # 긍정 지정사(이다)
    "VCN": {POS: ADJ},  # 부정 지정사(아니다)
    "NNG": {POS: NOUN},  # 일반 명사(general noun)
    "NNB": {POS: NOUN},  # 의존 명사
    "NNBC": {POS: NOUN},  # 의존 명사(단위: unit)
    "NNP": {POS: PROPN},  # 고유 명사(proper noun)
    "NP": {POS: PRON},  # 대명사
    "NR": {POS: NUM},  # 수사(numerals)
    "SN": {POS: NUM},  # 숫자
    # S.{1,2} 부호
    # 문장 부호
    "SF": {POS: PUNCT},  # period or other EOS marker
    "SE": {POS: PUNCT},
    "SC": {POS: PUNCT},  # comma, etc.
    "SSO": {POS: PUNCT},  # open bracket
    "SSC": {POS: PUNCT},  # close bracket
    "SY": {POS: SYM},  # 기타 기호
    "SL": {POS: X},  # 외국어
    "SH": {POS: X},  # 한자
}
