from ctypes import sizeof
import ctypes
import io
from .headers.main import SpcHdr
from .headers.subfile import SubHdr
from .headers.logbook import Logstc
from .headers.directory import Ssfstc
import numpy
import logging
logger = logging.getLogger(__name__)


class SubFile:
    def __init__(self, header, ydata_type, xarray=None, yarray=None):
        self.header = header
        self._ydata_type = ydata_type
        self._xarray = xarray
        self._yarray = yarray
        self._z = None
        self._w = None
        if yarray is not None:
            if yarray._type_ != self._ydata_type:
                raise ValueError('yarray and ydata_type differ')

        if self._ydata_type not in {ctypes.c_float,
                                    ctypes.c_int16,
                                    ctypes.c_int32, }:
            raise ValueError(f'Unexpected _ydata_type {self._ydata_type}')

    @property
    def z(self):
        if self._z is not None:
            return self._z
        else:
            return self.header.subfirst

    @z.setter
    def z(self, val):
        # support only non evenly distributed z
        self._z = None
        self.header.subfirst = val

    @property
    def w(self):
        if self._w is not None:
            return self._w
        else:
            return self.header.subwlevel

    @w.setter
    def w(self, val):
        # support only non evenly distributed w
        self._w = None
        self.header.subwlevel = val

    @property
    def xarray(self):
        arr = numpy.ctypeslib.as_array(self._xarray)
        return arr

    @xarray.setter
    def xarray(self, arr):
        self._xarray = numpy.ctypeslib.as_ctypes(arr.astype(ctypes.c_float))

    @property
    def yarray(self):
        arr = numpy.ctypeslib.as_array(self._yarray)
        if self._ydata_type == ctypes.c_float:
            return arr
        elif self._ydata_type == ctypes.c_int16:
            return (2 ** (self.header.subexp-16)) * arr
        elif self._ydata_type == ctypes.c_int32:
            return (2 ** (self.header.subexp-32)) * arr

    @yarray.setter
    def yarray(self, arr):
        if self._ydata_type == ctypes.c_int16:
            arr = arr / (2 ** (self.header.subexp-16))
        elif self._ydata_type == ctypes.c_int32:
            arr = arr / (2 ** (self.header.subexp-32))
        self._yarray = numpy.ctypeslib.as_ctypes(arr.astype(self._ydata_type))


class SpcRaw:
    @classmethod
    def from_bytes_io(cls, bytes_io: io.BytesIO):
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
            self._xarray = read_bytes(ctypes.c_float*self.main_header.fnpts)

        # subfiles
        for sub_i in range(self.main_header.fnsub):
            sub_header = read_bytes(SubHdr)
            ydata_type = (sub_header.DataType() or self.main_header.DataType())
            sub_file = SubFile(sub_header, ydata_type=ydata_type)
            self.subs.append(sub_file)
            if self.main_header.ftflgs.TXYXYS:
                # particular x
                sub_file._xarray = read_bytes(ctypes.c_float*sub_header.subnpts)
                y_array = read_bytes(ydata_type*sub_header.subnpts)
            else:
                y_array = read_bytes(ydata_type*self.main_header.fnpts)
            sub_file._yarray = y_array

        # fix w axis
        if self.main_header.fwinc:
            # w values are evenly distributed
            w_first = self.subs[0].header.subwlevel
            for sub in self.subs:
                if self.main_header.fwplanes:
                    # w axis enabled
                    w_i = sub.header.subindx // self.main_header.fwplanes
                    sub._w = w_first + self.main_header.fwinc * w_i
                else:
                    # w axis disabled
                    sub._w = 0

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

    def compile(self):
        def to_bytes(c_data):
            return ctypes.string_at(ctypes.addressof(c_data), ctypes.sizeof(c_data))
        # TODO: fix offsets
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
        return ret

    @property
    def xarray(self):
        if not self.main_header.ftflgs.TXYXYS:
            if self.main_header.ftflgs.TXVALS:
                arr = numpy.ctypeslib.as_array(self._xarray)
            else:
                arr = numpy.linspace(self.main_header.ffirst,
                                     self.main_header.flast,
                                     self.main_header.fnpts)
            return arr
        else:
            return None

    @xarray.setter
    def xarray(self, val):
        self._xarray = val
        self.main_header.ffirst = val[0]
        self.main_header.flast = val[-1]
