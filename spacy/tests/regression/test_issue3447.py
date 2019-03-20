from spacy import util

sizes = util.decaying(1., 10., 0.001)

size = next(sizes)
print (size)
assert size == 1.
size = next(sizes)
print (size)
assert size == 1. - 0.001
size = next(sizes)
print (size)
assert size == 1. - 0.001 - 0.001
