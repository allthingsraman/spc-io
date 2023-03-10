import ctypes
from spc_io.misc import EnumType


class MyEnum(metaclass=EnumType):
    _type_ = ctypes.c_uint8
    _enums_ = {
        1: 'a1',
        2: 'a2',
        3: 'a3',
    }


def test_enum_type():
    dict_test = {40: 'UNKNOWN'}
    dict_test.update(MyEnum._enums_)
    for enum_val, enum_name in dict_test.items():
        a = MyEnum(enum_val)
        for test_name in dict_test.values():
            assert getattr(a, test_name) == (enum_name == test_name)
