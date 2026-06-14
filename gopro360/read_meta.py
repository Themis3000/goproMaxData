"""
Processes a GPMF object and returns some of the containing metadata in a high level easy to work with format
"""
from dataclasses import dataclass
from .gpmf import GPMFRecord, GPMF
from typing import List


@dataclass()
class GPSSample:
    lat: int
    long: int
    alt: int
    speed2d: int
    speed3d: int
    time_micro_s: int
    sample_num: int
    gps_precision: int


@dataclass
class SensorData:
    gps: List[GPSSample]


def keyify_stream(stream: GPMFRecord):
    data_out = {}
    for value in stream.contents.data:
        data_out[value.fourcc] = value.contents
    return data_out


def get_sensor_data(gpmf: GPMF) -> SensorData:
    gps_samples: List[GPSSample] = []
    for frame in gpmf.data:
        for stream in frame.contents.data:
            if stream.fourcc != "STRM":
                continue
            stream_data = keyify_stream(stream)
            if stream_data["STNM"][0][0] != "GPS (Lat., Long., Alt., 2D speed, 3D speed)":
                continue
            sample = GPSSample(
                lat=stream_data["GPS5"][0][0] * stream_data["SCAL"][0][0],
                long=stream_data["GPS5"][0][1] * stream_data["SCAL"][1][0],
                alt=stream_data["GPS5"][0][2] * stream_data["SCAL"][2][0],
                speed2d=stream_data["GPS5"][0][3] * stream_data["SCAL"][3][0],
                speed3d=stream_data["GPS5"][0][4] * stream_data["SCAL"][4][0],
                time_micro_s=stream_data["STMP"][0][0],
                sample_num=stream_data["TSMP"][0][0],
                gps_precision=stream_data["GPSP"][0][0]
            )
            gps_samples.append(sample)
    return SensorData(gps_samples)
