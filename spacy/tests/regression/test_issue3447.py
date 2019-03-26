from util import decaying

sizes = decaying(10., 1.,.5)

size = next(sizes)
print (size)
assert size == 10.
size = next(sizes)
print (size)
assert size == 10. - 0.5
size = next(sizes)
print (size)
assert size == 10. - 0.5 - 0.5
