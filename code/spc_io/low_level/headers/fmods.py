from ctypes import c_uint32

from spc_io.misc import Structure


class Fmods(Structure):
    _pack_ = 1
    _fields_ = [
        ('_skip0', c_uint32, 1),
        ('A', c_uint32, 1),         # "A" (2^01) = Averaging (from multiple source traces)
        ('B', c_uint32, 1),         # "B" (2^02) = Baseline correction or offset functions
        ('C', c_uint32, 1),         # "C" (2^03) = Interferogram to spectrum Computation
        ('D', c_uint32, 1),         # "D" (2^04) = Derivative (or integrate) functions
        ('_skip5', c_uint32, 1),
        ('E', c_uint32, 1),         # "E" (2^06) = Resolution Enhancement functions (such as deconvolution)
        ('_skip7_8', c_uint32, 2),
        ('I', c_uint32, 1),         # "I" (2^09) = Interpolation functions
        ('_skip10_13', c_uint32, 4),
        ('N', c_uint32, 1),         # "N" (2^14) = Noise reduction smoothing
        ('O', c_uint32, 1),         # "O" (2^15) = Other functions (add, subtract, noise, etc.)
        ('_skip16_18', c_uint32, 3),
        ('S', c_uint32, 1),         # "S" (2^19) = Spectral Subtraction
        ('T', c_uint32, 1),         # "T" (2^20) = Truncation (only a portion of original X axis remains)
        ('_skip21_22', c_uint32, 2),
        ('W', c_uint32, 1),         # "W" (2^23) = When collected (date and time information) has been modified
        ('X', c_uint32, 1),         # "X" (2^24) = X units conversions or X shifting
        ('Y', c_uint32, 1),         # "Y" (2^25) = Y units conversions (transmission->absorbance, etc.)
        ('Z', c_uint32, 1),         # "Z" (2^26) = Zap functions (features removed or modified)
        ('_skip27_31', c_uint32, 5),
    ]
