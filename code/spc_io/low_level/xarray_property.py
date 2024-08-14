from ctypes import Array, c_float
from typing import Union

import numpy as np
import numpy.typing as npt
from pydantic import validate_call


class XArrayProperty:
    @property
    def xarray(self) -> Union[None, npt.NDArray]:
        if self._xarray is None:
            return None
        else:
            return np.ctypeslib.as_array(self._xarray)

    @xarray.setter
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def xarray(self, arr: Union[npt.NDArray, Array, None]):
        if arr is None:
            self._xarray = None
        elif isinstance(arr, Array):
            if arr._type_ != c_float:
                raise ValueError(f'wrong array type. Provided {arr._type_}, expected {c_float}')
            self._xarray = arr
        else:
            self._xarray = np.ctypeslib.as_ctypes(arr.astype(c_float))
