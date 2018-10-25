from __future__ import unicode_literals
import pytest
from ...util import load_model

@pytest.mark.models("en_core_web_md")
@pytest.mark.models("es_core_news_md")
def test_models_with_different_vectors():
    nlp = load_model('en_core_web_md')
    doc = nlp(u'hello world')
    nlp2 = load_model('es_core_news_md')
    doc2 = nlp2(u'hola')
    doc = nlp(u'hello world')
