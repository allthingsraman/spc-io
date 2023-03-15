import ctypes


class ComplexTypeBase:
    def __str__(self):
        kw = ', '.join([f'{k}={str(v)}' for k, v in self.to_dict().items() if not k.startswith('_')])
        return f'{type(self).__name__}({kw})'

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {field: str(getattr(self, field)) for field, *_ in self._fields_}


class Structure(ctypes.LittleEndianStructure, ComplexTypeBase):
    pass


class Union(ctypes.Union, ComplexTypeBase):
    pass
