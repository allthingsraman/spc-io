from datetime import datetime
from typing import Dict, Union

from pydantic import validate_call


class LogBook:
    @validate_call
    def __init__(self, *,
                 disk: bytes = b'',
                 binary: bytes = b'',
                 text: Dict[str, Union[int, float, datetime, str]] = dict()):
        self.disk = disk
        self.binary = binary
        self.text = text
