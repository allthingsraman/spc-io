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

    from_buffer20 = str(MyEnum.from_buffer_copy(b'\x20'))
    from_buffer02 = str(MyEnum.from_buffer_copy(b'\x02'))
    assert from_buffer20 == 'UNKNOWN', f'{from_buffer20} != UNKNOWN'
    assert from_buffer02 == 'a2', f'{from_buffer20} != a2'
    assert repr(MyEnum(2)) == repr(MyEnum('a2')), f'{repr(MyEnum(2))} != {repr(MyEnum("a2"))}'
    from_buffer02_repr = repr(MyEnum.from_buffer_copy(b'\x02'))
    assert repr(MyEnum(2)) == repr(MyEnum.from_buffer_copy(b'\x02')), f'{repr(MyEnum(2))} != {from_buffer02_repr}'
