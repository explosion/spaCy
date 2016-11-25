class Scorer(object):
    def __init__(self):
        self.true = 0
        self.total = 0

    def __iadd__(self, is_correct):
        self.true += is_correct
        self.total += 1
        return self

    def __str__(self):
        return '%.3f' % (self.true / self.total)


