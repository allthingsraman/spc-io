from ctypes import c_uint8

from spc_io.misc import Structure


class Ftflgs(Structure):
    _pack_ = 1
    _fields_ = [
        ('TSPREC', c_uint8, 1),   # Single precision (16 bit) Y data if set.
        ('TCGRAM', c_uint8, 1),   # Enables fexper in older software (not used)
        ('TMULTI', c_uint8, 1),   # Multiple traces format (set if more than one subfile)
        ('TRANDM', c_uint8, 1),   # If TMULTI and TRANDM=1 then arbitrary time (Z) values
        ('TORDRD', c_uint8, 1),   # If TMULTI abd TORDRD=1 then ordered but uneven subtimes
        ('TALABS', c_uint8, 1),   # Set if should use fcatxt axis labels, not fxtype etc.
        ('TXYXYS', c_uint8, 1),   # If TXVALS and multifile, then each subfile has own X's
        ('TXVALS', c_uint8, 1),   # Floating X value array preceeds Y's (New format only)
    ]
