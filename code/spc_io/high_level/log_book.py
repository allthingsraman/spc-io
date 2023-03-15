from typing import Union, Dict
from datetime import datetime
from pydantic import validate_arguments


class LogBook:
    @validate_arguments
    def __init__(self, *,
                 disk: bytes = b'',
                 binary: bytes = b'',
                 text: Dict[str, Union[int, float, datetime, str]] = dict()):
        self.disk = disk
        self.binary = binary
        self.text = text
