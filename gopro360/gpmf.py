from dataclasses import dataclass
from typing import List


class GPMF:
    def __init__(self, f):
        self.f = f
        self.data = []
        self.data.append(self._read_klv())

    def _read_klv(self):
        fourcc = self.f.read(4).decode("utf-8")
        data_type = self.f.read(1).decode("utf-8")
        data_size = int.from_bytes(self.f.read(1))
        data_repeat = int.from_bytes(self.f.read(2))
        data = []
        for _ in range(data_repeat):
            data.append(self.f.read(data_size))
        # Distance from the last 4 byte alignment
        four_distance = self.f.tell() % 4
        if four_distance != 0:
            # Seek to next 4 byte alignment if past the last one
            self.f.seek(4 - four_distance, 1)
        return GPMFRecord(fourcc, data_type, data)

    def __repr__(self):
        return self.data.__repr__()


@dataclass()
class GPMFRecord:
    fourcc: str
    data_type: str
    data: List[bytes]
