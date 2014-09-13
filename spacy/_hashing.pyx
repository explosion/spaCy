# cython: profile=True
from libc.stdlib cimport calloc, free
cimport cython


cdef class PointerHash:
    def __cinit__(self, size_t initial_size=8):
        self.size = initial_size
        self.size = 8
        self.filled = 0
        self._last = NULL
        # Size must be power of two
        assert self.size & (self.size - 1) == 0
        self.cells = <Cell*>calloc(self.size, sizeof(Cell))

    def __dealloc__(self):
        free(self.cells)

    def __getitem__(self, key_t key):
        assert key != 0
        cdef val_t value = self.lookup(key)
        return value if value != 0 else None

    def __setitem__(self, key_t key,  val_t value):
        assert key != 0
        assert value != 0
        self.insert(key, value)

    cdef val_t lookup(self, key_t key):
        cell = _find_cell(self.cells, self.size, key)
        self._last = cell
        return cell.value

    cdef void insert(self, key_t key, val_t value) except *:
        cdef Cell* cell
        if self._last != NULL and key == self._last.key:
            cell = self._last
        else:
            cell = _find_cell(self.cells, self.size, key)
        self._last = NULL
        if cell.key == 0:
            cell.key = key
            self.filled += 1
        cell.value = value
        if (self.filled + 1) * 4 >= (self.size * 3):
            self.resize(self.size * 2)

    cdef void resize(self, size_t new_size) except *:
        assert (new_size & (new_size - 1)) == 0 # Must be a power of 2
        assert self.filled * 4 <= new_size * 3
        
        cdef Cell* old_cells = self.cells
        cdef size_t old_size = self.size

        self.size = new_size
        self.cells = <Cell*>calloc(new_size, sizeof(Cell))
        
        self.filled = 0
        cdef size_t i
        cdef size_t slot
        for i in range(old_size):
            if old_cells[i].key != 0:
                assert old_cells[i].value != 0, i
                self.insert(old_cells[i].key, old_cells[i].value)
        free(old_cells)


@cython.cdivision
cdef inline Cell* _find_cell(Cell* cells, size_t size, key_t key) nogil:
    cdef size_t i = (key % size)
    while cells[i].key != 0 and cells[i].key != key:
        i = (i + 1) % size
    return &cells[i]
