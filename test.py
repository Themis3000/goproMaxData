from gopro360 import GoPro360File


file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)
meta = gopro.get_meta()
print(meta)
