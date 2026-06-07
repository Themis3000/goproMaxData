from dataclasses import dataclass
from typing import List
from io import BytesIO
import struct


@dataclass()
class UnpackType:
    unpack_str: str
    size: int

    def get_unpack_str(self, data):
        count = len(data) // self.size
        return f"{count}{self.unpack_str}"


unpack_lookup = {
    "b": UnpackType("b", 1),
    "B": UnpackType("B", 1),
    "c": UnpackType("s", 1),
    "d": UnpackType("d", 8),
    "f": UnpackType("f", 4),
    "F": UnpackType("s", 1),
    "j": UnpackType("q", 8),
    "J": UnpackType("Q", 8),
    "l": UnpackType("l", 4),
    "L": UnpackType("L", 4),
    "s": UnpackType("h", 2),
    "S": UnpackType("H", 2)
}


class GPMFRecord:
    def __init__(self, fourcc: str, data_type: str, data: List[bytes]):
        self.fourcc = fourcc
        self.data_type = data_type
        self.contents = self._decode_contents(data)

    def _decode_contents(self, data):
        if self.data_type == "\x00":
            return GPMF(BytesIO(b"".join(data)))

        if self.data_type in unpack_lookup:
            unpack_str = unpack_lookup[self.data_type].get_unpack_str(data[0])
        else:
            return ["not implemented"]
        return [struct.unpack(unpack_str, data) for data in data]


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
            out += f"{data.fourcc}, {data.data_type}: {data.contents.__repr__()}\n"
        return out
