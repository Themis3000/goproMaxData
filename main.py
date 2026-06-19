from gopro360 import GoPro360File
from img_storage import store_image
import glob
from pathlib import Path

input_videos = glob.glob("./video_in/*.360")
if len(input_videos) == 0:
    print("No input files where found!")
    quit()

frame_time_str = input("Enter frame timing (e.g. 1/1001, 1/2, etc) > ")
frame_time_parts = frame_time_str.split("/")
frame_time = int(frame_time_parts[0]) / int(frame_time_parts[1])

allowable_precision = int(input("Enter the allowable gps precision (frames above this precision will be discarded. "
                                "gopro recommends 500) > "))
quality = int(input("Select your jpeg output quality (1-100) > "))

for video_path in input_videos:
    file_name = Path(video_path).name
    print(f"Loading {file_name}...")
    gopro = GoPro360File(video_path)
    print(f"Loaded {file_name}!")

    Path(f"./out/{file_name}").mkdir(exist_ok=True)

    for frame_num, image in enumerate(gopro.read_360_images()):
        time_ns = int(frame_num * frame_time * 1000000)
        gpsData = gopro.get_gps_at_ts(time_ns)
        if gpsData.accuracy > allowable_precision:
            print(f"Skipping frame #{frame_num + 1} from {file_name} for having an accuracy of {gpsData.accuracy}")
            continue
        store_image(image, gpsData.lat, gpsData.long, gpsData.gpsTime, f"./out/{file_name}/{frame_num}.jpg", quality)
        print(f"Wrote frame #{frame_num + 1} from {file_name} (accuracy {gpsData.accuracy})")
