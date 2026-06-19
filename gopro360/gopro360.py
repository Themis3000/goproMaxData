import datetime

import ffmpeg
import numpy as np
import py360convert
from PIL import Image
from dataclasses import dataclass
from .read_meta import get_sensor_data, SensorData
from .gpmf import GPMF


@dataclass
class GoProMeta:
    sensors: SensorData
    framerate: float
    device_name: str
    image_width: int
    image_height: int


@dataclass
class InterpolatedGPSData:
    lat: float
    long: float
    gpsTime: datetime
    accuracy: int


class GoPro360File:
    def __init__(self, file_path):
        self.file_path = file_path
        self.meta = self.get_meta()

    def get_meta(self) -> GoProMeta:
        """Gets GPMF metadata (contains sensor information)"""
        probe = ffmpeg.probe(self.file_path)
        gpmf_stream_info = next((stream for stream in probe["streams"] if stream["codec_tag_string"] == "gpmd"), None)
        if gpmf_stream_info is None:
            raise Exception("Could not find GPMF data stream in input file")
        stream_num = gpmf_stream_info["index"]

        process = (
            ffmpeg
            .input(self.file_path)
            .output("pipe:", format="data", **{'map': f"0:{stream_num}"})
            .run_async(pipe_stdout=True)
        )

        gpmf = GPMF(process.stdout)
        process.wait()
        sensor_data = get_sensor_data(gpmf)

        device_name_record = next((record for record in gpmf.data[0].contents.data if record.fourcc == "DVNM"))
        device_name = device_name_record.contents[0][0]

        frame_rate_str = probe["streams"][0]["avg_frame_rate"]
        numerator, denominator = frame_rate_str.split("/")
        frame_rate = int(numerator) / int(denominator)

        width = probe["streams"][0]["width"]
        height = probe["streams"][0]["height"]

        return GoProMeta(sensor_data, frame_rate, device_name, width, height)

    def get_video_streams(self):
        """Returns metadata for the two video streams"""
        probe = ffmpeg.probe(self.file_path)
        streams_meta = (stream for stream in probe["streams"] if stream.get("codec_name") == "hevc")
        stream1 = next(streams_meta)
        stream2 = next(streams_meta)
        return stream1, stream2

    def read_frames(self):
        """Reads raw frames out from file"""
        stream_meta = self.get_video_streams()
        process1 = (
            ffmpeg
            .input(self.file_path)
            .output("pipe:", format='rawvideo', pix_fmt="rgb24", **{'map': f"0:{stream_meta[0]['index']}"})
            .run_async(pipe_stdout=True)
        )
        process2 = (
            ffmpeg
            .input(self.file_path)
            .output("pipe:", format='rawvideo', pix_fmt="rgb24", **{'map': f"0:{stream_meta[1]['index']}"})
            .run_async(pipe_stdout=True)
        )
        frame_size = self.meta.image_width * self.meta.image_height * 3
        while True:
            in_bytes1 = process1.stdout.read(frame_size)
            in_bytes2 = process2.stdout.read(frame_size)
            if len(in_bytes1) == 0 or len(in_bytes2) == 0:
                break
            frame1 = (
                np
                .frombuffer(in_bytes1, np.uint8)
                .reshape([self.meta.image_height, self.meta.image_width, 3])
            )
            frame2 = (
                np
                .frombuffer(in_bytes2, np.uint8)
                .reshape([self.meta.image_height, self.meta.image_width, 3])
            )
            yield frame1, frame2
        process1.wait()
        process2.wait()

    @staticmethod
    def _blend_face(face):
        # TODO: Do actual blending.
        face_split = np.hsplit(face, (672, 704))
        face_join = np.hstack((face_split[0], face_split[2]))

        return face_join

    def read_cube_faces(self):
        for frame in self.read_frames():
            frame1_split = np.hsplit(frame[0], (1376, 2720))
            frame2_split = np.hsplit(frame[1], (1376, 2720))
            yield {
                "L": self._blend_face(frame1_split[0]),
                "F": frame1_split[1],
                "R": self._blend_face(frame1_split[2]),
                "D": np.rot90(self._blend_face(frame2_split[0]), 3),
                "B": np.rot90(frame2_split[1]),
                "U": np.rot90(self._blend_face(frame2_split[2]), 3)
            }

    def read_equi_frames(self):
        for cube_dict in self.read_cube_faces():
            yield py360convert.c2e(cube_dict, 2880, 5760, cube_format="dict")

    def read_360_images(self) -> Image:
        for equi_frame in self.read_equi_frames():
            yield Image.fromarray(equi_frame)

    @staticmethod
    def _interpolate(x1, x2, percent) -> int:
        """
        Interpolates a position that lays *percent* from x1 to x2
        Visual explanation: https://www.desmos.com/calculator/rartg26hmt
        """
        x3 = (((x2 - x1) / 100) * percent) + x1
        return x3

    def get_gps_at_ts(self, timestamp: int) -> InterpolatedGPSData:
        """
        Gets the GPS data at a given timestamp. Timestamp is in microseconds. The location is interpolated between
        the closest gps sample before and after the given timestamp.
        """
        gps_data = self.meta.sensors.gps
        gps_data.sort(key=lambda x: abs(x.time_micro_s - timestamp))
        close_before = next((point for point in gps_data if timestamp > point.time_micro_s), gps_data[0])
        close_after = next((point for point in gps_data if timestamp < point.time_micro_s), gps_data[-1])

        if close_before == close_after:
            return InterpolatedGPSData(lat=close_before.lat / 100000000000000,
                                       long=close_before.long / 100000000000000,
                                       gpsTime=close_before.get_datetime(),
                                       accuracy=close_before.gps_precision)

        percent = (timestamp - close_before.time_micro_s) / (
                close_after.time_micro_s - close_before.time_micro_s) * 100

        adjusted_lat = self._interpolate(close_before.lat, close_after.lat, percent)
        adjusted_long = self._interpolate(close_before.long, close_after.long, percent)

        adjusted_timestamp = self._interpolate(close_before.get_datetime().timestamp(),
                                               close_after.get_datetime().timestamp(),
                                               percent)
        adjusted_datetime = datetime.datetime.fromtimestamp(adjusted_timestamp)

        accuracy = min(close_before.gps_precision, close_after.gps_precision)

        return InterpolatedGPSData(lat=adjusted_lat / 100000000000000,
                                   long=adjusted_long / 100000000000000,
                                   gpsTime=adjusted_datetime,
                                   accuracy=accuracy)
