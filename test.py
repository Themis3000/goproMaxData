from gopro360 import GoPro360File

file_path = "./test_data/GS010029.360"
gopro = GoPro360File(file_path)

gps_data = gopro.get_meta()


def interpolate(x1, y1, x2, y2, percent):
    """
    Interpolates a position that lays *percent* from x1,y1 to x2,y2
    Visual explanation: https://www.desmos.com/calculator/rartg26hmt
    """
    x3 = (((x2 - x1) / 100) * percent) + x1
    y3 = (((y2 - y1) / 100) * percent) + y1
    return x3, y3


time_per_frame = 0.5
time_micro_s = 0
for frame in range(1000):
    time_micro_s += time_per_frame * 1000000

    gps_data.sort(key=lambda x: abs(x.time_micro_s - time_micro_s))
    close_before = next((point for point in gps_data if time_micro_s > point.time_micro_s), gps_data[0])
    close_after = next((point for point in gps_data if time_micro_s < point.time_micro_s), gps_data[-1])

    percent = (time_micro_s - close_before.time_micro_s) / (close_after.time_micro_s - close_before.time_micro_s) * 100

    adjusted_lat, adjusted_long = interpolate(close_before.lat, close_before.long,
                                              close_after.lat, close_after.long,
                                              percent)

    print(f"""
    ===
    time: {time_micro_s}
    before_lat: {gps_data[0].lat}
    before_long: {gps_data[0].long}
    percent: {percent}%
    after_lat: {adjusted_lat}
    after_long: {adjusted_long}
    ===
    """)
