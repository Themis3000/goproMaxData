from gopro360 import GPMF
import json

with open("./test_data/track2.bin", "rb") as f:
    gpmf = GPMF(f)

with open("./out.json", "w") as f:
    json.dump(gpmf.to_dict(), f)
