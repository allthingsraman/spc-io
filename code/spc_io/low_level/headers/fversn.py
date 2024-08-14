from ctypes import c_uint8

from spc_io.misc import EnumType


class Fversn(metaclass=EnumType):
    _type_ = c_uint8
    _enums_ = {0x4b: 'LSB_format',
               0x4c: 'MSB_format',
               0x4d: 'old_format',
               }
