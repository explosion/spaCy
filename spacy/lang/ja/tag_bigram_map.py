from ...symbols import ADJ, AUX, NOUN, PART, VERB

# mapping from tag bi-gram to pos of previous token
TAG_BIGRAM_MAP = {
    # This covers only small part of AUX.
    ("形容詞-非自立可能", "助詞-終助詞"): (AUX, None),
    ("名詞-普通名詞-形状詞可能", "助動詞"): (ADJ, None),
    # ("副詞", "名詞-普通名詞-形状詞可能"): (None, ADJ),
    # This covers acl, advcl, obl and root, but has side effect for compound.
    ("名詞-普通名詞-サ変可能", "動詞-非自立可能"): (VERB, AUX),
    # This covers almost all of the deps
    ("名詞-普通名詞-サ変形状詞可能", "動詞-非自立可能"): (VERB, AUX),
    ("名詞-普通名詞-副詞可能", "動詞-非自立可能"): (None, VERB),
    ("副詞", "動詞-非自立可能"): (None, VERB),
    ("形容詞-一般", "動詞-非自立可能"): (None, VERB),
    ("形容詞-非自立可能", "動詞-非自立可能"): (None, VERB),
    ("接頭辞", "動詞-非自立可能"): (None, VERB),
    ("助詞-係助詞", "動詞-非自立可能"): (None, VERB),
    ("助詞-副助詞", "動詞-非自立可能"): (None, VERB),
    ("助詞-格助詞", "動詞-非自立可能"): (None, VERB),
    ("補助記号-読点", "動詞-非自立可能"): (None, VERB),
    ("形容詞-一般", "接尾辞-名詞的-一般"): (None, PART),
    ("助詞-格助詞", "形状詞-助動詞語幹"): (None, NOUN),
    ("連体詞", "形状詞-助動詞語幹"): (None, NOUN),
    ("動詞-一般", "助詞-副助詞"): (None, PART),
    ("動詞-非自立可能", "助詞-副助詞"): (None, PART),
    ("助動詞", "助詞-副助詞"): (None, PART),
}
