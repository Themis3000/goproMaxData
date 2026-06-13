from gopro360 import GoPro360File
import time


file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)
frames = gopro.read_frames()

for frame in frames:
    print("got frame")
    print(frame)
    time.sleep(2)

