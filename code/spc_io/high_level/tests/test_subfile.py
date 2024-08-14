import numpy as np
import pytest
from spc_io.high_level.spc import SPC, SPCSubFile


def test_subfile():
    with pytest.raises(ValueError):
        SPCSubFile(parent=SPC(xarray=np.array([1, 2, 3])), yarray=np.array([1, 2, 3]), xarray=np.array([1, 2, 3]))
    SPCSubFile(parent=SPC(), yarray=np.array([1, 2, 3]), xarray=np.array([1, 2, 3]))
    SPCSubFile(parent=SPC(xarray=np.array([1, 2, 3])), yarray=np.array([1, 2, 3]))
    with pytest.raises(ValueError):
        SPCSubFile(parent=SPC(), yarray=np.array([1, 2, 3]))

    with pytest.raises(ValueError):
        SPCSubFile(parent=SPC(xarray=np.array([1, 2, 3, 4])), yarray=np.array([1, 2, 3]))

    with pytest.raises(ValueError):
        SPCSubFile(parent=SPC(), xarray=np.array([1, 2, 3, 4]), yarray=np.array([1, 2, 3]))

    SPCSubFile(parent=SPC(), xarray=np.array([1, 2, 3]), yarray=np.array([1, 2, 3]))
