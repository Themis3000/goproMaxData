from gopro360 import GoPro360File
from PIL import Image


file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)

faces_gen = gopro.read_cube_faces()
face = next(faces_gen)
Image.fromarray(face["forward"]).show()
