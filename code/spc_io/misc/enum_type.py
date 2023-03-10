from ctypes import LittleEndianStructure


class EnumType(type):
    def __new__(cls, name, bases, dct):
        dct_struct = dict(
            _pack_=1,
            _fields_=[('_val', dct['_type_'])],
            )
        dct_struct.update(dct)
        dct_struct.update({
            enum: property(lambda self, enumt=(enum,):
                           self._val in dct['_enums_'] and dct['_enums_'][self._val] == enumt[0])
            for enum in dct['_enums_'].values()
        })
        dct_struct.update({
            'UNKNOWN': property(lambda self: self._val not in dct['_enums_']),
            '__str__': (lambda self:
                        'UNKNOWN' if self._val not in dct['_enums_'] else
                        dct['_enums_'][self._val]
                        ),
            '__repr__': (lambda self: f'{name}({self._val})')
        })
        ret = type(name, (LittleEndianStructure,), dct_struct)
        return ret
