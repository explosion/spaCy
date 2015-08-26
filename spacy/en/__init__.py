from __future__ import unicode_literals, print_function

from os import path

from ..language import Language

LOCAL_DATA_DIR = path.join(path.dirname(__file__), 'data')

class English(Language):
    @classmethod
    def default_data_dir(cls):
        return LOCAL_DATA_DIR
