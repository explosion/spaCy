from libc.stdint cimport uint16_t, uint32_t, uint64_t, uintptr_t, int32_t
from libc.stdint cimport uint8_t

from libc.stdint cimport UINT64_MAX as err_hash_t
from libc.stdint cimport UINT64_MAX as err_flags_t
from libc.stdint cimport UINT64_MAX as err_len_t
from libc.stdint cimport UINT64_MAX as err_tag_t

ctypedef uint64_t hash_t
ctypedef char* utf8_t
ctypedef int32_t attr_t
ctypedef uint64_t flags_t
ctypedef uint16_t len_t
ctypedef uint16_t tag_t
