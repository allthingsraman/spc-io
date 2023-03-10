from ctypes import c_uint16
from spc_io.misc import Structure


class Fdate(Structure):
    _pack_ = 1
    _fields_ = [
        ('min', c_uint16, 6),
        ('hour', c_uint16, 5),
        ('day', c_uint16, 5),
        ('month', c_uint16, 4),
        ('year', c_uint16, 12),
    ]
