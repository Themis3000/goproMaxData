from glob import glob
from gopro360 import GoPro360File

file_paths = glob("./test_input/*.360")
for file_path in file_paths:
    file = GoPro360File(file_path)
    print(file)
