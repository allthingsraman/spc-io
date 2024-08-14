from ctypes import addressof, c_char, c_uint8, c_uint32, sizeof, string_at
from typing import Dict, Union

from pydantic import validate_call
from spc_io.misc import Structure


class LogBookBase:
    def txt_as_dict(self):
        return dict([i.decode(errors='surrogateescape').split('=')
                     for ii in self.txt.split(b'\r\n')
                     for i in ii.split(b'\n\r')
                     if b'=' in i
                     ])

    def disk_as_bytes(self):
        return bytearray(string_at(addressof(self.disk), sizeof(self.disk)))

    def binary_as_bytes(self):
        return bytearray(string_at(addressof(self.binary), sizeof(self.binary)))


class Logstc(Structure):
    _pack_ = 1
    _fields_ = [
        ('logsizd', c_uint32),     # byte size of disk block
        ('logsizm', c_uint32),     # byte size of memory block
        ('logtxto', c_uint32),     # byte offset to text
        ('logbins', c_uint32),     # byte size of binary area (immediately after logstc)
        ('logdsks', c_uint32),     # byte size of disk area (immediately after logbins)
        ('logspar', c_char*44),    # reserved (must be zero)
    ]

    @classmethod
    @validate_call
    def new_header_and_logbook_from_data(cls, *,
                                         disk: bytes = b'',
                                         binary: bytes = b'',
                                         txt: Union[bytes, Dict] = b''):
        if isinstance(txt, dict):
            txt = b'\r\n'.join([f'{k}={v}'.encode(errors='surrogateescape') for k, v in txt.items()])
        txt += b'\x00'  # NUL terminate
        logsizd = len(disk)+len(binary)+len(txt)+sizeof(cls)
        logsizm = ((logsizd // 4096) + 1) * 4096
        logbins = len(binary)
        logdsks = len(disk)
        logtxto = (sizeof(cls)+logbins+logdsks)
        ret = cls(logsizd=logsizd,
                  logsizm=logsizm,
                  logtxto=logtxto,
                  logbins=logbins,
                  logdsks=logdsks,
                  logspar=b'\x00',
                  )
        LogBook = ret.build_LogBook_type()
        log_book = LogBook.from_buffer_copy(disk + binary + txt)
        return ret, log_book

    def build_LogBook_type(self):
        dct = {
            '_pack_': 1,
            '_fields_': [
                ('disk', c_uint8 * self.logdsks),
                ('binary', c_uint8 * self.logbins),
                ('_skip', c_uint8 * (self.logtxto - sizeof(self) - (self.logdsks + self.logbins))),
                ('txt', c_char * (self.logsizd - self.logtxto)),
            ]
        }
        return type('LogBook', (Structure, LogBookBase), dct)
