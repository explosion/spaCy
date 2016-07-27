import re


_mw_prepositions = [
    'close to',
    'down by',
    'on the way to',
    'on my way to',
    'on my way',
    'on his way to',
    'on his way',
    'on her way to',
    'on her way',
    'on your way to',
    'on your way',
    'on our way to',
    'on our way',
    'on their way to',
    'on their way',
    'along the route from'
]


MW_PREPOSITIONS_RE = re.compile('|'.join(_mw_prepositions), flags=re.IGNORECASE)


TIME_RE = re.compile(
    '{colon_digits}|{colon_digits} ?{am_pm}?|{one_two_digits} ?({am_pm})'.format(
        colon_digits=r'[0-2]?[0-9]:[0-5][0-9](?::[0-5][0-9])?',
        one_two_digits=r'[0-2]?[0-9]',
        am_pm=r'[ap]\.?m\.?'))

DATE_RE = re.compile(
    '(?:this|last|next|the) (?:week|weekend|{days})'.format(
        days='Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday'
    ))


MONEY_RE = re.compile('\$\d+(?:\.\d+)?|\d+ dollars(?: \d+ cents)?')


DAYS_RE = re.compile('Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday')


REGEXES = [('IN', 'O', MW_PREPOSITIONS_RE), ('CD', 'TIME', TIME_RE),
           ('NNP', 'DATE', DATE_RE),
           ('NNP', 'DATE', DAYS_RE), ('CD', 'MONEY', MONEY_RE)]
