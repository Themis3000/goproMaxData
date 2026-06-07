from dataclasses import dataclass
from typing import List
from io import BytesIO


@dataclass()
class GPMFRecord:
    fourcc: str
    data_type: str
    data: List[bytes]

    def decode_contents(self):
        if self.data_type == "\x00":
            return GPMF(BytesIO(b"".join(self.data)))
        return ""


class GPMF:
    def __init__(self, f):
        self.f = f
        self.data = []

        while data := self._read_klv():
            self.data.append(data)

    def _read_klv(self) -> GPMFRecord | None:
        fourcc = self.f.read(4).decode("utf-8")
        if fourcc == "":
            return None
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
        out = ""
        for data in self.data:
            out += data.decode_contents().__repr__()
        return out
