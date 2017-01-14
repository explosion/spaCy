from __future__ import unicode_literals

import re

URL_PATTERN = r'''
((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)
'''.strip()

TOKEN_MATCH = re.compile("^{}$".format(URL_PATTERN)).match

__all__ = ['TOKEN_MATCH']
