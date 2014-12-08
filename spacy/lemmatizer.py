from os import path


NOUN_RULES = (
    ('s', ''),
    ('ses', 's'),
    ('ves', 'f'),
    ('xes', 'x'),
    ('zes', 'z'),
    ('ches', 'ch'),
    ('shes', 'sh'),
    ('men', 'man'),
    ('ies', 'y')
)


VERB_RULES = (
    ("s", ""),
    ("ies", "y"),
    ("es", "e"),
    ("es", ""),
    ("ed", "e"),
    ("ed", ""),
    ("ing", "e"),
    ("ing", "")
)


ADJ_RULES = (
    ("er", ""),
    ("est", ""),
    ("er", "e"),
    ("est", "e")
)


class Lemmatizer(object):
    def __init__(self, wn_dict_dir):
        self.index = {}
        self.exc = {}
        for pos in ['adj', 'adv', 'noun', 'verb']:
            self.index[pos] = read_index(path.join(wn_dict_dir, 'index.%s' % pos))
            self.exc[pos] = read_exc(path.join(wn_dict_dir, '%s.exc' % pos))

    def noun(self, string):
        return lemmatize(string, self.index['noun'], self.exc['noun'], NOUN_RULES)

    def verb(self, string):
        return lemmatize(string, self.index['verb'], self.exc['verb'], VERB_RULES)

    def adj(self, string):
        return lemmatize(string, self.index['adj'], self.exc['adj'], ADJ_RULES)


def lemmatize(string, index, exceptions, rules):
    string = string.lower()
    forms = []
    if string in index:
        forms.append(string)
    forms.extend(exceptions.get(string, []))
    for old, new in rules:
        if string.endswith(old):
            form = string[:len(string) - len(old)] + new
            if form in index:
                forms.append(form)
    if not forms:
        forms.append(string)
    return set(forms)


def read_index(loc):
    index = set()
    for line in open(loc):
        if line.startswith(' '):
            continue
        pieces = line.split()
        word = pieces[0]
        if word.count('_') == 0:
            index.add(word)
    return index


def read_exc(loc):
    exceptions = {}
    for line in open(loc):
        if line.startswith(' '):
            continue
        pieces = line.split()
        exceptions[pieces[0]] = tuple(pieces[1:])
    return exceptions
