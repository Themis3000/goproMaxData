import datetime
from PIL import Image
import piexif


def dec_deg_to_dms(dd):
    # https://stackoverflow.com/a/12737895/5813879
    negative = dd < 0
    dd = abs(dd)
    minutes, seconds = divmod(dd*3600, 60)
    degrees, minutes = divmod(minutes, 60)
    if negative:
        if degrees > 0:
            degrees = -degrees
        elif minutes > 0:
            minutes = -minutes
        else:
            seconds = -seconds
    return abs(int(degrees)), int(minutes), int(round(seconds, 2)*100)


def store_image(image: Image, lat: int, long: int, timestamp: datetime, file):
    lat_deg, lat_min, lat_sec = dec_deg_to_dms(lat)
    long_deg, long_min, long_sec = dec_deg_to_dms(long)

    lat_cardinal = "N" if lat > 0 else "S"
    long_cardinal = "E" if long > 0 else "W"

    date_str = timestamp.strftime("%Y:%m:%d %H:%M:%S")

    exif_dict = {
        "0th": {
            piexif.ImageIFD.DateTime: date_str
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: date_str
        },
        "GPS": {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSLatitudeRef: lat_cardinal,
            piexif.GPSIFD.GPSLatitude: ((abs(lat_deg), 1), (lat_min, 1), (lat_sec, 100)),
            piexif.GPSIFD.GPSLongitudeRef: long_cardinal,
            piexif.GPSIFD.GPSLongitude: ((abs(long_deg), 1), (long_min, 1), (long_sec, 100)),
            piexif.GPSIFD.GPSDateStamp: timestamp.strftime("%Y:%m:%d"),
            piexif.GPSIFD.GPSTimeStamp: ((timestamp.hour, 1), (timestamp.minute, 1), (timestamp.second, 1))
        }
    }

    exif_bytes = piexif.dump(exif_dict)
    image.save("./out/test.jpg", exif=exif_bytes)
