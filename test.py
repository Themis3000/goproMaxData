from gopro360 import GoPro360File
from PIL import Image


file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)

frames_gen = gopro.read_equi_frames()
frame = next(frames_gen)
Image.fromarray(frame).save("./test.png")
