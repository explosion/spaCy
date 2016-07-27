class RegexMerger(object):
    def __init__(self, regexes):
        self.regexes = regexes

    def __call__(self, tokens):
        for tag, entity_type, regex in self.regexes:
            for m in regex.finditer(tokens.string):
                tokens.merge(m.start(), m.end(), tag, m.group(), entity_type)
