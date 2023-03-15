from spc_io.misc import Structure
from ctypes import c_uint32, c_float


class Ssfstc(Structure):
    _pack_ = 1
    _fields_ = [
        ('ssfposn', c_uint32),   # disk file position of beginning of subfile (subhdr)
        ('ssfsize', c_uint32),   # byte size of subfile (subhdr+X+Y)
        ('ssftime', c_float),    # floating Z time of subfile (subtime)
    ]
