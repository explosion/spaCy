from typing import Pattern

from .tokenizer_exceptions import URL_MATCH
from ..util import registry


@registry.language_data("spacy.xx.url_match")
def url_match() -> Pattern:
    return URL_MATCH
