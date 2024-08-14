from ctypes import c_uint8

from spc_io.misc import EnumType


class Fexper(metaclass=EnumType):
    _type_ = c_uint8
    _enums_ = {
        0: 'SPCGEN',    # General SPC (could be anything)
        1: 'SPCGC',     # Gas Chromatogram
        2: 'SPCCGM',    # General Chromatogram (same as SPCGEN with TCGRAM)
        3: 'SPCHPLC',   # HPLC Chromatogram
        4: 'SPCFTIR',   # FT-IR, FT-NIR, FT-Raman Spectrum or Igram (Can also be used for scanning IR.)
        5: 'SPCNIR',    # NIR Spectrum (Usually multi-spectral data sets for calibration.)
        7: 'SPCUV',     # UV-VIS Spectrum (Can be used for single scanning UV-VIS-NIR)
        8: 'SPCXRY',    # X-ray Diffraction Spectrum
        9: 'SPCMS',     # Mass Spectrum (Can be single, GC-MS, Continuum, Centroid or TOF.)
        10: 'SPCNMR',   # NMR Spectrum or FID
        11: 'SPCRMN',   # Raman Spectrum (Usually Diode Array, CCD, etc. use SPCFTIR for FT-Raman.)
        12: 'SPCFLR',   # Fluorescence Spectrum
        13: 'SPCATM',   # Atomic Spectrum
        14: 'SPCDAD',   # Chromatography Diode Array Spectra
    }
