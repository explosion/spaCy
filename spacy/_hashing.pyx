cdef class PointerHash:
    def __cinit__(self, size_t initial_size=8):
        self.size = initial_size
        self.filled = 0
        # Size must be power of two
        assert self.size & (self.size - 1) == 0
        self.cells = <Cell*>calloc(self.size, sizeof(Cell))

    def __dealloc__(self):
        free(self.cells)

    def __getitem__(self, key_t key):
        cdef Cell* cell = self.lookup(key)
        return cell.value if cell.key != 0 else None

    def __setitem__(self, key_t key,  val_t value):
        self.insert(key, value

    cdef size_t find_slot(self, key_t key):
        cdef size_t i = key % self.size
        while self.cells[i].key != 0 and self.cells[i].key != key:
            i = (i + 1) % self.size
        return i

    cdef Cell* lookup(self, key_t key):
        cdef size_t i = self.find_slot(key)
        return &self.cells[i]

    cdef void insert(self, key_t key, val_t value):
        cdef size_t i = self.find_slot(key)
        if self.cells[i].key == 0:
            self.cells[i].key = key
            self.filled += 1
        self.cells[i].value = value
        if (self.filled + 1) * 4 >= (self.size * 3):
            self.resize(self.size * 2)

    cdef void resize(self, size_t new_size):
        assert new_size & (new_size - 1)) == 0 # Must be a power of 2
        assert self.filled * 4 <= new_size * 3
        
        self.size = new_size

        cdef Cell* old_cells = self.cells
        cdef size_t old_size = self.size

        self.size = new_size
        self.cells = <Cell*>calloc(new_size, sizeof(Cell))

        for i in range(old_size):
            self.insert(self.cells[i].key, self.cells[i].value)
