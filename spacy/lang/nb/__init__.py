# coding: utf8
from __future__ import unicode_literals

from ..no import Norwegian as NewNorwegian
from ...errors import user_warning, Warnings


user_warning(Warnings.W020)
Norwegian = NewNorwegian

__all__ = ["Norwegian"]
