from __future__ import unicode_literals

from libc.string cimport memcpy

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
    def __init__(self, data=b''):
        self.data = bytearray(data)
        self.byte = 0
        self.bit_of_byte = 0
        self.i = 0

    def __len__(self):
        return 8 * len(self.data) + self.bit_of_byte

    def __str__(self):
        cdef uchar byte, i
        cdef uchar one = 1
        string = b''
        for i in range(len(self.data)):
            byte = ord(self.data[i])
            for j in range(8):
                string += b'1' if (byte & (one << j)) else b'0'
        for i in range(self.bit_of_byte):
            string += b'1' if (byte & (one << i)) else b'0'
        return string

    def seek(self, i):
        self.i = i

    def __iter__(self):
        cdef uchar byte, i
        cdef uchar one = 1
        start_byte = self.i // 8
        start_bit = self.i % 8

        if start_bit != 0 and start_byte < len(self.data):
            byte = self.data[start_byte]
            for i in range(start_bit, 8):
                self.i += 1
                yield 1 if (byte & (one << i)) else 0
            start_byte += 1
            start_bit = 0

        for byte in self.data[start_byte:]:
            for i in range(8):
                self.i += 1
                yield 1 if byte & (one << i) else 0

        if self.bit_of_byte != 0:
            byte = self.byte
            for i in range(start_bit, self.bit_of_byte):
                self.i += 1
                yield 1 if self.byte & (one << i) else 0

    cpdef int32_t read32(self) except 0:
        cdef int start_byte = self.i // 8

        # TODO portability
        cdef uchar[4] chars
        chars[0] = self.data[start_byte]
        chars[1] = self.data[start_byte+1]
        chars[2] = self.data[start_byte+2]
        chars[3] = self.data[start_byte+3]
        cdef uint32_t output
        memcpy(&output, chars, 4)
        self.i += 32
        return output

    def as_bytes(self):
        cdef unsigned char byte_char
        if self.bit_of_byte != 0:
            byte = chr(self.byte)
            # Jump through some hoops for Python3
            if isinstance(byte, unicode):
                return self.data + <bytes>(&self.byte)[:1]
            else:
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
        self.i += 1
        if self.bit_of_byte == 8:
            self.data += bytearray((self.byte,))
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
                self.data += <bytes>self.byte
                self.byte = 0
                self.bit_of_byte = 0
            self.i += 1
