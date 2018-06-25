# coding: utf8
from __future__ import unicode_literals


def test_tokenizer_handles_long_text(ar_tokenizer):
    text = """نجيب محفوظ مؤلف و كاتب روائي عربي، يعد من أهم الأدباء العرب خلال القرن العشرين.
     ولد نجيب محفوظ في مدينة القاهرة، حيث ترعرع و تلقى تعليمه الجامعي في جامعتها،
      فتمكن من نيل شهادة في الفلسفة. ألف محفوظ على مدار حياته الكثير من الأعمال الأدبية، و في مقدمتها ثلاثيته الشهيرة.
      و قد نجح في الحصول على جائزة نوبل للآداب، ليكون بذلك العربي الوحيد الذي فاز بها."""

    tokens = ar_tokenizer(text)
    assert tokens[3].is_stop == True
    assert len(tokens) == 77
