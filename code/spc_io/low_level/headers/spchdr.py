from ctypes import (c_char, c_double, c_float, c_int8, c_uint8, c_uint16,
                    c_uint32)

from spc_io.misc import Structure

from .fdate import Fdate
from .fexper import Fexper
from .fmods import Fmods
from .ftflgs import Ftflgs
from .fversn import Fversn
from .fxytype import Fxtype, Fytype


class SpcHdr(Structure):
    _pack_ = 1
    _anonymous_ = ()
    _fields_ = [
        ('ftflgs', Ftflgs),         # Flag bits defined below
        ('fversn', Fversn),         # 0x4B=> new LSB 1st, 0x4C=> new MSB 1st, 0x4D=> old format
        ('fexper', Fexper),         # Instrument technique code (see below)
        ('fexp', c_int8),           # Fraction scaling exponent integer (80h=>float)
        ('fnpts', c_uint32),        # Integer number of points (or TXYXYS directory position
        ('ffirst', c_double),       # Floating X coordinate of first point
        ('flast', c_double),        # Floating X coordinate of last point
        ('fnsub', c_uint32),        # Integer number of subfiles (1 if not TMULTI)
        ('fxtype', Fxtype),         # Type of X axis units (see definitions below)
        ('fytype', Fytype),         # Type of Y axis units (see definitions below)
        ('fztype', Fxtype),         # Type of Z axis units (see definitions below)
        ('fpost', c_uint8),         # Posting disposition (see GRAMSDDE.H)
        ('fdate', Fdate),           # Date/Time LSB: min=6b,hour=5b,day=5b,month=4b,year=12b
        ('fres', c_char*9),         # Resolution description text (null terminated)
        ('fsource', c_char*9),      # Source instrument description text (null terminated)
        ('fpeakpt', c_uint16),      # Peak point number for interferograms (0=not known)
        ('fspare', c_float*8),      # Used for Array Basic storage
        ('fcmnt', c_char*130),      # Null terminated comment ASCII text string
        ('fcatxt', c_char*30),      # X,Y,Z axis label strings if ftflgs=TALABS
        ('flogoff', c_uint32),      # File offset to log block or 0 (see above)
        ('fmods', Fmods),           # File Modification Flags (see below: 1=A,2=B,4=C,8=D..)
        ('fprocs', c_uint8),        # Processing code (see GRAMSDDE.H)
        ('flevel', c_uint8),        # Calibration level plus one (1 = not calibration data)
        ('fsampin', c_uint16),      # Sub-method sample injection number (1 = first or only )
        ('ffactor', c_float),       # Floating data multiplier concentration factor (IEEE-32)
        ('fmethod', c_char*48),     # Method/program/data filename w/extensions comma list
        ('fzinc', c_float),         # Z subfile increment (0 = use 1st subnext-subfirst)
        ('fwplanes', c_uint32),     # Number of planes for 4D with W dimension (0=normal)
        ('fwinc', c_float),         # W plane increment (only if fwplanes is not 0)
        ('fwtype', Fxtype),         # Type of W axis units (see definitions below)
        ('freserv', c_char*187),    # Reserved (must be set to zero)
    ]
