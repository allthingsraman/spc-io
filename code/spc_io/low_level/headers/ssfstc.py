from ctypes import c_float, c_uint32

from spc_io.misc import Structure


class Ssfstc(Structure):
    _pack_ = 1
    _fields_ = [
        ('ssfposn', c_uint32),   # disk file position of beginning of subfile (subhdr)
        ('ssfsize', c_uint32),   # byte size of subfile (subhdr+X+Y)
        ('ssftime', c_float),    # floating Z time of subfile (subtime)
    ]
