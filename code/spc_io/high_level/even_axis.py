from numpy import linspace
from pydantic import validate_call


class EvenAxis:
    @validate_call
    def __init__(self, start: float, stop: float, num: int):
        self._start = start
        self._stop = stop
        self._num = num
        self._values_array = None

    def __repr__(self):
        return f'{type(self).__name__}({self.start}, {self.stop}, {self.num})'

    def __len__(self):
        return self.num

    @property
    def values(self):
        if self._values_array is None:
            self._values_array = linspace(start=self.start, stop=self.stop, num=self.num)
        return self._values_array

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def num(self):
        return self._num
