import pytest
from spacy.lang.tr.lex_attrs import like_num


def test_tr_tokenizer_handles_long_text(tr_tokenizer):
    text = """Pamuk nasıl ipliğe dönüştürülür?

Sıkıştırılmış balyalar halindeki pamuk, iplik fabrikasına getirildiğinde hem
lifleri birbirine dolaşmıştır, hem de tarladan toplanırken araya bitkinin
parçaları karışmıştır. Üstelik balyalardaki pamuğun cinsi aynı olsa bile kalitesi
değişeceğinden, önce bütün balyaların birbirine karıştırılarak harmanlanması gerekir.

Daha sonra pamuk yığınları, liflerin açılıp temizlenmesi için tek bir birim halinde
birleştirilmiş çeşitli makinelerden geçirilir.Bunlardan biri, dönen tokmaklarıyla
pamuğu dövüp kabartarak dağınık yumaklar haline getiren ve liflerin arasındaki yabancı
maddeleri temizleyen hallaç makinesidir. Daha sonra tarak makinesine giren pamuk demetleri,
herbirinin yüzeyinde yüzbinlerce incecik iğne bulunan döner silindirlerin arasından geçerek lif lif ayrılır
ve tül inceliğinde gevşek bir örtüye dönüşür. Ama bir sonraki makine bu lifleri dağınık
ve gevşek bir biçimde birbirine yaklaştırarak 2 cm eninde bir pamuk şeridi haline getirir."""
    tokens = tr_tokenizer(text)
    assert len(tokens) == 146


@pytest.mark.parametrize(
    "word",
    [
        "bir",
        "iki",
        "dört",
        "altı",
        "milyon",
        "100",
        "birinci",
        "üçüncü",
        "beşinci",
        "100üncü",
        "8inci",
    ],
)
def test_tr_lex_attrs_like_number_cardinal_ordinal(word):
    assert like_num(word)


@pytest.mark.parametrize("word", ["beş", "yedi", "yedinci", "birinci", "milyonuncu"])
def test_tr_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
