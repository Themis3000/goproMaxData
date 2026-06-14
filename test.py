from gopro360 import GoPro360File
import time


file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)

images = gopro.read_360_images()

start = time.time()
print("="*50)
print(start)
print("="*50)

for i, image in enumerate(images):
    image.save(f"./out/{i}.jpg")

end = time.time()
print("="*50)
print(end)
print(start - end)
print("="*50)
