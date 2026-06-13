from gopro360 import GoPro360File
import time
from PIL import Image


file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)
frames = gopro.read_frames()

for frame in frames:
    print("got frame")
    Image.fromarray(frame[0]).show()
    Image.fromarray(frame[1]).show()
    break

