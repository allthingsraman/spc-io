import io
import logging
from ctypes import addressof, c_float, c_int16, c_int32, sizeof, string_at
from typing import List, Union

from pydantic import validate_call

from .headers.logstc import Logstc
from .headers.spchdr import SpcHdr
from .headers.ssfstc import Ssfstc
from .headers.sub_hdr import SubHdr
from .sub_file import SubFile
from .xarray_property import XArrayProperty

logger = logging.getLogger(__name__)


class SpcRaw(XArrayProperty):
    @classmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def from_high_level(cls, *,
                        header: SpcHdr,
                        subs: List[SubFile],
                        xarray=None,
                        log_binary: bytes = b'',
                        log_disk: bytes = b'',
                        log_txt={},
                        ):
        self = cls()
        self.main_header = header
        self.xarray = xarray
        self.subs = subs
        self.log_header, self.log_book = Logstc.new_header_and_logbook_from_data(
            disk=log_disk, binary=log_binary, txt=log_txt)
        self.dirs = list()
        self.calcuate_offsets()
        return self

    @classmethod
    def from_bytes_io(cls, bytes_io: Union[io.BytesIO, io.BufferedReader]):
        self = cls()
        self.subs = list()
        self._xarray = None
        self.log_header = None
        self.log_book = None
        self.dirs = list()

        def read_bytes(obj_type):
            nbytes = sizeof(obj_type)
            return obj_type.from_buffer_copy(bytes_io.read(nbytes))

        self.main_header = read_bytes(SpcHdr)
        if self.main_header.ftflgs.TRANDM:
            raise NotImplementedError('ftflgs.TRANDM bit is not supproted')

        if not self.main_header.fversn.LSB_format:
            raise NotImplementedError('only LSB format is supproted')

        # global X
        if self.main_header.ftflgs.TXVALS and not self.main_header.ftflgs.TXYXYS:
            # single X array for all Y
            self._xarray = read_bytes(c_float*self.main_header.fnpts)

        # subfiles
        for sub_i in range(self.main_header.fnsub):
            sub_header = read_bytes(SubHdr)
            if self.main_header.fexp == -0x80 or sub_header.subexp == -0x80:
                ydata_type = c_float
            else:
                if self.main_header.ftflgs.TSPREC:  # single precision
                    ydata_type = c_int16
                else:
                    ydata_type = c_int32
            if self.main_header.ftflgs.TXYXYS:
                # particular x
                xarray = read_bytes(c_float*sub_header.subnpts)
                yarray = read_bytes(ydata_type*sub_header.subnpts)
            else:
                xarray = None
                yarray = read_bytes(ydata_type*self.main_header.fnpts)
            sub_file = SubFile(sub_header,
                               xarray=xarray,
                               yarray=yarray,
                               single_prec=self.main_header.ftflgs.TSPREC)
            self.subs.append(sub_file)

        # fix w axis
        w_first = self.subs[0].header.subwlevel
        for sub in self.subs:
            if self.main_header.fwplanes:
                # w axis enabled
                if self.main_header.fwinc:
                    # w values are evenly distributed
                    w_i = sub.header.subindx // self.main_header.fwplanes
                    sub._w = w_first + self.main_header.fwinc * w_i
                else:
                    sub._w = True  # take from subfile header
            else:
                sub._w = False  # W axis is disabled

        # fix z axis
        if self.main_header.ftflgs.TMULTI:
            if self.main_header.fzinc == 0:
                self.main_header.fzinc = self.subs[0].header.subnext - self.subs[0].header.subfirst
            if not self.main_header.ftflgs.TORDRD or self.main_header.ftflgs.TRANDM:
                first = self.subs[0].header.subfirst
                increment = self.main_header.fzinc
                for sub in self.subs:
                    if self.main_header.fwplanes:
                        sub._z = first + increment * (sub.header.subindx % self.main_header.fwplanes)
                    else:
                        sub._z = first + increment * sub.header.subindx
            else:
                for sub in self.subs:
                    sub._z = True  # take from subfile header
        else:
            sub._z = False  # Z axis is disabled

        # directory
        if self.main_header.ftflgs.TXYXYS:
            if self.main_header.fnpts:
                # assume packed
                # bytes_io.seek(self.main_header.fnpts)
                for sub_i in range(self.main_header.fnsub):
                    self.dirs.append(read_bytes(Ssfstc))

        # Log book
        if self.main_header.flogoff:
            # assume packed
            # bytes_io.seek(self.main_header.flogoff)
            self.log_header = read_bytes(Logstc)
            LogBook = self.log_header.build_LogBook_type()
            self.log_book = read_bytes(LogBook)
        else:
            self.log_header, self.log_book = Logstc.new_header_and_logbook_from_data()

        self._extra_bytes_at_eof = bytes_io.read()
        if len(self._extra_bytes_at_eof):
            logger.warning(f'{len(self._extra_bytes_at_eof)} left at the end of the file')
        return self

    def calcuate_offsets(self):
        self.dirs = list()
        ofs = sizeof(self.main_header)
        if self.main_header.ftflgs.TXVALS and not self.main_header.ftflgs.TXYXYS:
            ofs += sizeof(self._xarray)
        for sub in self.subs:
            size = sizeof(sub.header)
            if self.main_header.ftflgs.TXVALS and self.main_header.ftflgs.TXYXYS:
                size += sizeof(sub._xarray)
            size += sizeof(sub._yarray)
            ofs += size
            if sub.z is not None:
                self.dirs.append(Ssfstc(ssfposn=ofs, ssfsize=size, ssftime=sub.z))

        # Directory offset
        ofs += sizeof(self.log_book)
        if self.main_header.ftflgs.TXYXYS:
            self.main_header.fnpts = ofs

        # Logbook offset
        self.main_header.flogoff = ofs

        self.main_header.fnsub = len(self.subs)

    def _to_bytes_as_is(self) -> bytes:
        def to_bytes(c_data):
            return string_at(addressof(c_data), sizeof(c_data))
        ret = []

        # Main header
        ret.append(to_bytes(self.main_header))

        # Global X values
        if self._xarray is not None:
            ret.append(to_bytes(self._xarray))

        # Subfiles
        for sub in self.subs:
            ret.append(to_bytes(sub.header))
            if sub._xarray is not None:
                ret.append(to_bytes(sub._xarray))
            ret.append(to_bytes(sub._yarray))

        # Directories
        for dd in self.dirs:
            ret.append(to_bytes(dd))

        # Logbook
        if self.log_header.logsizd > 1:  # 1 because of NUL terminated string
            ret.append(to_bytes(self.log_header))
            ret.append(to_bytes(self.log_book))
        return b''.join(ret)

    def to_bytes(self) -> bytes:
        self.calcuate_offsets()
        return self._to_bytes_as_is()
