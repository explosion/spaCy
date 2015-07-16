

# Note that we're setting the most significant bits here first, when in practice
# we're actually wanting the last bit to be most significant (for Huffman coding,
# anyway).
cdef Code bit_append(Code code, bint bit) nogil:
    cdef uint64_t one = 1
    if bit:
        code.bits |= one << code.length
    else:
        code.bits &= ~(one << code.length)
    code.length += 1
    return code


cdef class BitArray:
    def __init__(self):
        self.data = b''
        self.byte = 0
        self.bit_of_byte = 0
        self.i = 0

    def __iter__(self):
        cdef uchar byte, i
        cdef uchar one = 1
        start_byte = self.i // 8
        if (self.i % 8) != 0:
            for i in range(self.i % 8):
                yield 1 if (self.data[start_byte] & (one << i)) else 0
            start_byte += 1
        for byte in self.data[start_byte:]:
            for i in range(8):
                yield 1 if byte & (one << i) else 0
        for i in range(self.bit_of_byte):
            yield 1 if self.byte & (one << i) else 0

    def as_bytes(self):
        if self.bit_of_byte != 0:
            return self.data + chr(self.byte)
        else:
            return self.data

    def append(self, bint bit):
        cdef uint64_t one = 1
        if bit:
            self.byte |= one << self.bit_of_byte
        else:
            self.byte &= ~(one << self.bit_of_byte)
        self.bit_of_byte += 1
        if self.bit_of_byte == 8:
            self.data += chr(self.byte)
            self.byte = 0
            self.bit_of_byte = 0

    cdef int extend(self, uint64_t code, char n_bits) except -1:
        cdef uint64_t one = 1
        cdef unsigned char bit_of_code
        for bit_of_code in range(n_bits):
            if code & (one << bit_of_code):
                self.byte |= one << self.bit_of_byte
            else:
                self.byte &= ~(one << self.bit_of_byte)
            self.bit_of_byte += 1
            if self.bit_of_byte == 8:
                self.data += chr(self.byte)
                self.byte = 0
                self.bit_of_byte = 0


