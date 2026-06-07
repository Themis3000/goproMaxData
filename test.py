from gopro360 import GPMF

file = open("./test_data/track2.bin", "rb")
gpmf = GPMF(file)
print(gpmf)
