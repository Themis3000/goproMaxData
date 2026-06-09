from gopro360 import GPMF, get_meta


with open("./test_data/track2.bin", "rb") as f:
    gpmf = GPMF(f)

gps_samples = get_meta(gpmf)

print(gps_samples)
