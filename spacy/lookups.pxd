# coding: utf8

from preshed.bloom cimport BloomFilter

cdef class Lookups(object):
    cdef dict _tables

cdef class Table(dict):
    cdef public str name
    cdef dict _dict
    cdef BloomFilter bloom
