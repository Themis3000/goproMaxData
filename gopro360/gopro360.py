import ffmpeg
from .read_meta import get_meta
from .gpmf import GPMF


class GoPro360File:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_meta(self):
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
