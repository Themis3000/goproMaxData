from typing import List
import ffmpeg
import numpy as np
from .read_meta import get_meta, GPSSample
from .gpmf import GPMF


class GoPro360File:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_meta(self) -> List[GPSSample]:
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

    def read_frames(self) -> np.array:
        process = (
            ffmpeg
            .input(self.file_path)
            .output("pipe:", format='rawvideo', pix_fmt="rgb24")
            .run_async(pipe_stdout=True)
        )
        while in_bytes := process.stdout.read(1344*4096*3):
            frame = (
                np
                .frombuffer(in_bytes, np.uint8)
                .reshape([1344, 4096, 3])
            )
            yield frame
        process.wait()
