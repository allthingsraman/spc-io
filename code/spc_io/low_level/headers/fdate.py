from ctypes import c_uint32

from spc_io.misc import Structure


class Fdate(Structure):
    _pack_ = 1
    _fields_ = [
        ('min', c_uint32, 6),
        ('hour', c_uint32, 5),
        ('day', c_uint32, 5),
        ('month', c_uint32, 4),
        ('year', c_uint32, 12),
    ]
