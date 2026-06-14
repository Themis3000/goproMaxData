from typing import List
import ffmpeg
import numpy as np
import py360convert
from PIL import Image
from .read_meta import get_meta, GPSSample
from .gpmf import GPMF


class GoPro360File:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_meta(self) -> List[GPSSample]:
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
        return get_meta(gpmf)

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
        frame_size = 1344 * 4096 * 3
        while True:
            in_bytes1 = process1.stdout.read(frame_size)
            in_bytes2 = process2.stdout.read(frame_size)
            if not in_bytes1:
                break
            frame1 = (
                np
                .frombuffer(in_bytes1, np.uint8)
                .reshape([1344, 4096, 3])
            )
            frame2 = (
                np
                .frombuffer(in_bytes2, np.uint8)
                .reshape([1344, 4096, 3])
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

    def read_360_images(self):
        for equi_frame in self.read_equi_frames():
            yield Image.fromarray(equi_frame)
