from gopro360 import GPMF
from gopro360.gpmf import GPMFRecord
from dataclasses import dataclass
from typing import List

with open("./test_data/track2.bin", "rb") as f:
    gpmf = GPMF(f)


@dataclass()
class GPSSample:
    lat: int
    long: int
    alt: int
    speed2d: int
    speed4d: int


def parse_stream_data(stream: GPMFRecord):
    data_out = {}
    for value in stream.contents.data:
        data_out[value.fourcc] = value.contents
    return data_out


gps_samples: List[GPSSample] = []
for frame in gpmf.data:
    for stream in frame.contents.data:
        if stream.fourcc != "STRM":
            continue
        stream_data = parse_stream_data(stream)
        if stream_data["STNM"][0][0] != "GPS (Lat., Long., Alt., 2D speed, 3D speed)":
            continue
        print(stream_data)
