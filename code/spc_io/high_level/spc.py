from __future__ import annotations

import io
import logging
from datetime import datetime
from typing import List, Literal, Union

import numpy as np
import numpy.typing as npt
import pandas as pd
from pydantic import validate_call
from spc_io.low_level.headers.fdate import Fdate
from spc_io.low_level.headers.ftflgs import Ftflgs
from spc_io.low_level.headers.fversn import Fversn
from spc_io.low_level.headers.fxytype import Fxtype, Fytype
from spc_io.low_level.headers.spchdr import SpcHdr
from spc_io.low_level.headers.sub_hdr import Subflgs, SubHdr
from spc_io.low_level.spc_raw import SpcRaw
from spc_io.low_level.sub_file import SubFile

from .even_axis import EvenAxis
from .log_book import LogBook

logger = logging.getLogger(__name__)


class SPCSubFile:
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self,
                 parent,
                 *,
                 xarray: Union[npt.NDArray, None] = None,
                 yarray: npt.NDArray,
                 w: Union[float, None] = None,
                 z: Union[float, None] = None,
                 ):
        self._parent = parent
        self._xarray = xarray
        self._yarray = yarray
        self._w = w
        self._z = z

        if (self._parent.xarray is None) ^ (self._xarray is not None):
            raise ValueError('Should have ONLY a global OR local xarray')

        if len(self._yarray) != len(self):
            print(self._yarray)
            raise ValueError(f'xarray({len(self)}) and yarray({len(self._yarray)}) should have identical shapes.')

    def __len__(self):
        return len(self.xarray)

    def __repr__(self):
        return (f'{type(self).__name__}(' +
                f'<{type(self._parent).__name__} at {id(self._parent)}>, ' +
                f'xarray={self._xarray}, ' +
                f'yarray={self._yarray}, ' +
                f'w={self._w}, ' +
                f'z={self._z})'
                )

    @property
    def xarray(self):
        if self._xarray is None:
            return self._parent.xarray
        else:
            return self._xarray

    @property
    def yarray(self):
        return self._yarray

    @property
    def w(self):
        return self._w

    @property
    def z(self):
        return self._z


class SPC:  # NOQA: F811
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self,
                 xarray: Union[EvenAxis, npt.NDArray, None] = None,
                 xtype: Literal[tuple(Fxtype._enums_.values())] = Fxtype._enums_[0],
                 ytype: Literal[tuple(Fytype._enums_.values())] = Fytype._enums_[0],
                 wtype: Literal[tuple(Fxtype._enums_.values())] = Fxtype._enums_[0],
                 ztype: Literal[tuple(Fxtype._enums_.values())] = Fxtype._enums_[0],
                 date: datetime = datetime.fromtimestamp(0),
                 log_book: LogBook = LogBook(),
                 ):
        self._subs: List[SPCSubFile] = list()
        self._xarray = xarray
        self.xtype = xtype
        self.ytype = ytype
        self.wtype = wtype
        self.ztype = ztype
        self.date = date
        self.log_book = log_book

    def __repr__(self):
        subs = ',\n'.join([str(sub) for sub in self._subs])
        return f'{type(self).__name__}(xarray={self._xarray}, date={self.date}, subs={subs}, log_book={self.log_book})'

    def __len__(self):
        return len(self._subs)

    def __getitem__(self, idx):
        return self._subs[idx]

    def __iter__(self):
        return iter(self._subs)

    @property
    def xarray(self):
        if isinstance(self._xarray, EvenAxis):
            return self._xarray.values
        else:
            return self._xarray

    @property
    def warray(self):
        return np.unique([sub.w for sub in self._subs if sub.w is not None])

    @property
    def zarray(self):
        return np.unique([sub.z for sub in self._subs if sub.z is not None])

    @classmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def from_spc_raw(cls, spc_raw: SpcRaw):
        log_book = LogBook(disk=spc_raw.log_book.disk_as_bytes(),
                           binary=spc_raw.log_book.binary_as_bytes(),
                           text=spc_raw.log_book.txt_as_dict())
        main_header = spc_raw.main_header
        fdate = main_header.fdate
        try:
            date = datetime(year=fdate.year,
                            month=fdate.month,
                            day=fdate.day,
                            hour=fdate.hour,
                            minute=fdate.min,
                            )
        except ValueError as e:
            logger.warning(repr(e))
            date = datetime.fromtimestamp(0)

        if not main_header.ftflgs.TXYXYS:
            if main_header.ftflgs.TXVALS:
                xarr = np.ctypeslib.as_array(spc_raw._xarray)
            else:
                xarr = EvenAxis(start=main_header.ffirst,
                                stop=main_header.flast,
                                num=main_header.fnpts)
        else:
            xarr = None

        self = cls(xarray=xarr,
                   date=date,
                   log_book=log_book,
                   xtype=str(main_header.fxtype),
                   ytype=str(main_header.fytype),
                   wtype=str(main_header.fxtype),
                   ztype=str(main_header.fxtype),
                   )

        for sub in spc_raw.subs:
            self.add_subfile(xarray=sub.xarray,
                             yarray=sub.yarray,
                             w=sub.w,
                             z=sub.z,
                             )

        return self

    def add_subfile(self, **kwargs):
        subf = SPCSubFile(self, **kwargs)
        self._subs.append(subf)
        self.sort_subs()

    def sort_subs(self):
        self._subs = sorted(self._subs, key=lambda sub: (sub.w, sub.z))

    def find_wz(self, w, z):
        ret = [sub for sub in self._subs if sub.w == w and sub.z == z]
        if len(ret) > 1:
            raise ValueError(f'multiple subfiles with same (w, z) = ({w}, {z})')
        return ret[0]

    @classmethod
    def from_bytes_io(cls, bytes_io: Union[io.BytesIO, io.BufferedReader]):
        spc_raw = SpcRaw.from_bytes_io(bytes_io=bytes_io)
        return cls.from_spc_raw(spc_raw=spc_raw)

    def to_dataframe_table(self):
        if self.xarray is not None:
            tup = [(sub.w, sub.z) for sub in self._subs]
            ind = pd.MultiIndex.from_tuples(tup, names=["w", "z"])
            return pd.DataFrame(data=[sub.yarray for sub in self._subs], columns=self.xarray, index=ind)
        else:
            raise ValueError('dataframe table is possible only when global x is used')

    def to_dataframe_flattened(self):
        return pd.DataFrame(data=[
            (sub.xarray[idx], sub.yarray[idx], sub.w, sub.z)
            for sub in self._subs for idx in range(len(sub))
        ], columns=['x', 'y', 'w', 'z'])

    def to_spc_raw(self):
        main_header = SpcHdr(ftflgs=Ftflgs(TSPREC=0,),
                             fversn=Fversn(0x4b),
                             fexp=-0x80,
                             fdate=Fdate(year=self.date.year,
                                         month=self.date.month,
                                         day=self.date.day,
                                         hour=self.date.hour,
                                         min=self.date.minute,
                                         ),
                             fzinc=0,
                             fwinc=0,
                             )

        main_header.fwinc = 0  # w value in sub_header.subwlevel
        main_header.ftflgs.TORDRD = 0  # z values in sub_header.subfirst

        subs = list()
        self.sort_subs()
        for sub_i, sub in enumerate(self._subs):
            subheader = SubHdr(subflgs=Subflgs(),
                               subexp=-0x80,
                               subindx=sub_i,
                               subnpts=len(sub),
                               )
            subfile = SubFile(header=subheader,
                              xarray=sub._xarray,
                              yarray=sub._yarray)
            if sub.w is not None:
                subfile.w = sub.w
            if sub.z is not None:
                subfile.z = sub.z
            subs.append(subfile)

        if len(self._subs) > 1:
            main_header.ftflgs.TMULTI = 1

        if self._xarray is None:
            # individual x axes
            main_header.ftflgs.TXVALS = 1
            main_header.ftflgs.TXYXYS = 1
        elif isinstance(self._xarray, EvenAxis):
            # global x axis linspace
            main_header.ftflgs.TXVALS = 0
            main_header.ftflgs.TXYXYS = 0
            main_header.ffirst = self._xarray.start
            main_header.flast = self._xarray.stop
            main_header.fnpts = self._xarray.num
        else:
            # global x axis array
            main_header.ftflgs.TXVALS = 1
            main_header.ftflgs.TXYXYS = 0
            main_header.ffirst = self._xarray[0]
            main_header.flast = self._xarray[-1]
            main_header.fnpts = len(self._xarray)

        main_header.fwinc = 0  # w value in sub_header.subwlevel
        main_header.ftflgs.TORDRD = 0  # z values in sub_header.subfirst

        return SpcRaw.from_high_level(header=main_header,
                                      subs=subs,
                                      xarray=(self._xarray if not isinstance(self._xarray, EvenAxis) else None),
                                      log_disk=self.log_book.disk,
                                      log_binary=self.log_book.binary,
                                      log_txt=self.log_book.text
                                      )
