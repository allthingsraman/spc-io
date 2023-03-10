from ctypes import LittleEndianStructure


class EnumMethods(LittleEndianStructure):
    @property
    def UNKNOWN(self):
        return self._val not in self._enums_

    def __init__(self, _val):
        if isinstance(_val, str):
            num = list(self._enums_.keys())[list(self._enums_.values()).index(_val)]
            super().__init__(_val=num)
        else:
            super().__init__(_val=_val)

    def __str__(self):
        if self._val not in self._enums_:
            return 'UNKNOWN'
        else:
            return self._enums_[self._val]

    def __repr__(self):
        return f'{type(self).__name__}({self._val})'


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
        ret = type(name, (EnumMethods,), dct_struct)
        return ret
