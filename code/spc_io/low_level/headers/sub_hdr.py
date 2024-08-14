from ctypes import c_char, c_float, c_int8, c_uint8, c_uint16, c_uint32

from spc_io.misc import Structure


class Subflgs(Structure):
    _pack_ = 1
    _fields_ = [
        ('SUBCHGD', c_uint8, 1),    # subfile changed
        ('_skip_2_3', c_uint8, 2),
        ('SUBNOPT', c_uint8, 1),    # table file should not be used
        ('_skip_5_7', c_uint8, 3),
        ('SUBMODF', c_uint8, 1),    # subfile modified by arithmetic
    ]


class SubHdr(Structure):
    _pack_ = 1
    _fields_ = [
        ('subflgs', Subflgs),    # Flags as defined above
        ('subexp', c_int8),      # Exponent for sub-file's Y values (80h=>float)
        ('subindx', c_uint16),   # Integer index number of trace subfile (0=first)
        ('subfirst', c_float),   # Floating time for trace (Z axis coordinate)
        ('subnext', c_float),    # Floating time for next trace (May be same as beg)
        ('subnois', c_float),    # Floating peak pick noise level if high byte nonzero
        ('subnpts', c_uint32),   # Integer number of subfile points for TXYXYS type
        ('subscan', c_uint32),   # Integer number of co-added scans or 0 (for collect)
        ('subwlevel', c_float),  # Floating W axis value (if fwplanes non-zero)
        ('subresv', c_char*4),   # Reserved area (must be set to zero)
    ]
