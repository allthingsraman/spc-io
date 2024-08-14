from ctypes import c_uint8

from spc_io.misc import EnumType, Union


class Fxtype(metaclass=EnumType):
    _type_ = c_uint8
    _enums_ = {
        0: 'XARB',        # Arbitrary
        1: 'XWAVEN',      # Wavenumber (cm-1)
        2: 'XUMETR',      # Micrometers (um)
        3: 'XNMETR',      # Nanometers (nm)
        4: 'XSECS',       # Seconds
        5: 'XMINUTS',     # Minutes
        6: 'XHERTZ',      # Hertz (Hz)
        7: 'XKHERTZ',     # Kilohertz (KHz)
        8: 'XMHERTZ',     # Megahertz (MHz)
        9: 'XMUNITS',     # Mass (M/z)
        10: 'XPPM',       # Parts per million (PPM)
        11: 'XDAYS',      # Days
        12: 'XYEARS',     # Years
        13: 'XRAMANS',    # Raman Shift (cm-1)
        14: 'XEV',        # eV
        15: 'ZTEXTL',     # XYZ text labels in fcatxt (old 0x4D version only)
        16: 'XDIODE',     # Diode Number
        17: 'XCHANL',     # Channel
        18: 'XDEGRS',     # Degrees
        19: 'XDEGRF',     # Temperature (F)
        20: 'XDEGRC',     # Temperature (C)
        21: 'XDEGRK',     # Temperature (K)
        22: 'XPOINT',     # Data Points
        23: 'XMSEC',      # Milliseconds (mSec)
        24: 'XUSEC',      # Microseconds (uSec)
        25: 'XNSEC',      # Nanoseconds (nSec)
        26: 'XGHERTZ',    # Gigahertz (GHz)
        27: 'XCM',        # Centimeters (cm)
        28: 'XMETERS',    # Meters (m)
        29: 'XMMETR',     # Millimeters (mm)
        30: 'XHOURS',     # Hours
        255: 'XDBLIGM',   # Double interferogram (no display labels)
    }


class Fytype(metaclass=EnumType):
    _type_ = c_uint8
    _enums_ = {
        0: 'YARB',        # Arbitrary Intensity
        1: 'YIGRAM',      # Interferogram
        2: 'YABSRB',      # Absorbance
        3: 'YKMONK',      # Kubelka-Monk
        4: 'YCOUNT',      # Counts
        5: 'YVOLTS',      # Volts
        6: 'YDEGRS',      # Degrees
        7: 'YAMPS',       # Milliamps
        8: 'YMETERS',     # Millimeters
        9: 'YMVOLTS',     # Millivolts
        10: 'YLOGDR',     # Log(1/R)
        11: 'YPERCNT',    # Percent
        12: 'YINTENS',    # Intensity
        13: 'YRELINT',    # Relative Intensity
        14: 'YENERGY',    # Energy
        16: 'YDECBL',     # Decibel
        19: 'YDEGRF',     # Temperature (F)
        20: 'YDEGRC',     # Temperature (C)
        21: 'YDEGRK',     # Temperature (K)
        22: 'YINDRF',     # Index of Refraction [N]
        23: 'YEXTCF',     # Extinction Coeff. [K]
        24: 'YREAL',      # Real
        25: 'YIMAG',      # Imaginary
        26: 'YCMPLX',     # Complex
        128: 'YTRANS',    # Transmission (ALL TYPES >= 128 ARE ASSUMED INVERTED PEAKS!)
        129: 'YREFLEC',   # Reflectance
        130: 'YVALLEY',   # Arbitrary or Single Beam with Valley Peaks
        131: 'YEMISN',    # Emission
        255: 'YREFARBE',  # Reference Arbitrary Energy
    }


class Fxytype(Union):
    _pack_ = 1
    _anonymous_ = ('fxtype', 'fytype')
    _fields_ = [
        ('fxtype', Fxtype),
        ('fytype', Fytype),
    ]
