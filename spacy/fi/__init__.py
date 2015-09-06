from __future__ import unicode_literals, print_function

from os import path

from ..language import Language


class Finnish(Language):
    @classmethod
    def default_data_dir(cls):
        return path.join(path.dirname(__file__), 'data')
