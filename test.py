from gopro360 import GoPro360File
import time
from PIL import Image


file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)

faces = gopro.read_cube_faces()
face = next(faces)
Image.fromarray(face).show()
