from datetime import datetime
from gopro360 import GoPro360File
from img_storage import store_image

file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)

frame_time_str = input("Enter frame timing (e.g. 1/1001, 1/2, etc) > ")

frame_time_parts = frame_time_str.split("/")
frame_time = int(frame_time_parts[0]) / int(frame_time_parts[1])


for frame_num, image in enumerate(gopro.read_360_images()):
    time_ns = int(frame_num * frame_time * 1000000)
    gpsData = gopro.get_gps_at_ts(time_ns)
    store_image(image, gpsData.lat, gpsData.long, gpsData.gpsTime, f"./out/{frame_num}.jpg")
