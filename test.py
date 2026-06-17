from gopro360 import GoPro360File

file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)

location_120s = gopro.get_location_at_ts(120 * 1000000)
print(location_120s)
