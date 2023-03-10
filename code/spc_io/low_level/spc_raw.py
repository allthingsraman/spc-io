from ctypes import sizeof
import ctypes
import io
from .headers.main import SpcHdr
from .headers.subfile import SubHdr
from .headers.logbook import Logstc
from .headers.directory import Ssfstc
import numpy


class SubFile:
    def __init__(self, header, xarray=None, yarray=None):
        self.header = header
        self._xarray = xarray
        self._yarray = yarray

    @property
    def xarray(self):
        arr = numpy.ctypeslib.as_array(self._xarray)
        return arr

    @property
    def yarray(self):
        arr = numpy.ctypeslib.as_array(self._yarray)
        if self.header.subexp == 0x80:  # float
            return arr
        else:
            return (1 << self.header.subexp) * arr / ctypes.sizeof((self._yarray)._type_)


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

        if self.main_header.ftflgs.TXVALS and not self.main_header.ftflgs.TXYXYS:
            # single X array for all Y
            XArrayType = ctypes.c_float*self.main_header.fnpts
            self._xarray = read_bytes(XArrayType)

        try:
            for sub_i in range(self.main_header.fnsub):
                sub_header = read_bytes(SubHdr)
                sub_file = SubFile(sub_header)
                self.subs.append(sub_file)
                if self.main_header.ftflgs.TXYXYS:
                    XArrayType = ctypes.c_float*(sub_header.subnpts)
                    sub_file._xarray = read_bytes(XArrayType)
                    YArrayType = (sub_header.DataType() or self.main_header.DataType())*sub_header.subnpts
                else:
                    YArrayType = (sub_header.DataType() or self.main_header.DataType())*self.main_header.fnpts
                y_array = read_bytes(YArrayType)
                sub_file._yarray = y_array
        except Exception as e:
            print(repr(e))
            print(self.main_header)

        if self.main_header.ftflgs.TXYXYS:
            if self.main_header.fnpts:
                bytes_io.seek(self.main_header.fnpts)
                for sub_i in range(self.main_header.fnsub):
                    self.dirs.append(read_bytes(Ssfstc))

        if self.main_header.flogoff:
            bytes_io.seek(self.main_header.flogoff)
            self.log_header = read_bytes(Logstc)
            LogBook = self.log_header.build_LogBook_type()
            self.log_book = read_bytes(LogBook)
        else:
            self.log_header, self.log_book = Logstc.new_header_and_logbook_from_data()
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
