import logging
from ctypes import Array, c_float, c_int16, c_int32
from typing import Literal, Union

import numpy as np
import numpy.typing as npt
from pydantic import validate_call

from .headers.sub_hdr import SubHdr
from .xarray_property import XArrayProperty

logger = logging.getLogger(__name__)


class SubFile(XArrayProperty):
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, header: SubHdr,
                 xarray: Union[npt.NDArray, Array, None] = None,
                 yarray: Union[npt.NDArray, Array, None] = None,
                 single_prec: bool = False,
                 w=False, z=False):

        # Meaning of values for w and z
        # False - the axis is disabled
        # True - the value is calcualted usinc boundaries and increment
        # or a number for abitrary values

        self.header = header

        if self.header.subexp == -0x80 or isinstance(yarray, Array) and yarray._type_ == c_float:
            self._yarray_type = c_float
        else:
            if single_prec:
                self._yarray_type = c_int16
            else:
                self._yarray_type = c_int32

        self.xarray = xarray
        self.yarray = yarray

        self._w = w
        self._z = z

    @property
    def yarray_type(self):
        return self._yarray_type

    @yarray_type.setter
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def yarray_type(self, val: Literal[c_float, c_int16, c_int32]):
        self._yarray_type = val

    @property
    def z(self):
        if self._z is True:
            return self.header.subfirst
        elif self._z is False:
            return None
        else:
            return self._z

    @z.setter
    def z(self, val):
        # support only non evenly distributed z
        self._z = True
        self.header.subfirst = val

    @z.deleter
    def z(self):
        self._z = False

    @property
    def w(self):
        if self._w is True:
            return self.header.subwlevel
        elif self._w is False:
            return None
        else:
            return self._w

    @w.setter
    def w(self, val):
        # support only non evenly distributed w
        self._w = True
        self.header.subwlevel = val

    @w.deleter
    def w(self):
        self._w = False

    @property
    def yarray(self):
        arr = np.ctypeslib.as_array(self._yarray)
        if self._yarray_type == c_float:
            return arr
        elif self._yarray_type == c_int16:
            return (2. ** (self.header.subexp-16)) * arr
        elif self._yarray_type == c_int32:
            return (2. ** (self.header.subexp-32)) * arr

    @yarray.setter
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def yarray(self, arr: Union[npt.NDArray, Array, None]):
        if arr is None:
            self._yarray = arr
        elif isinstance(arr, Array):
            if arr._type_ != self._yarray_type:
                raise ValueError(f'wrong array type. Provided {arr._type_}, expected {self._yarray_type}')
            self._yarray = arr
        else:
            if self._yarray_type == c_int16:
                arr = arr / (2. ** (self.header.subexp-16))
            elif self._yarray_type == c_int32:
                arr = arr / (2. ** (self.header.subexp-32))
            self._yarray = np.ctypeslib.as_ctypes(arr.astype(self._yarray_type))
