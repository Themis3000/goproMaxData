# Purpose
Convert your GoPro Max .360 video files into individual .jpeg frames with geolocation/time data written. I created this so I can use my .360 video files for mapping on OSM easier

# How to use
1. Install ffmpeg
2. Install python
3. Install the dependencies listed in requirements.txt (`pip install -r requirements.txt`)
4. Drop your .360 files into `video_in`
5. Run `main.py`
6. Your .jpeg frames will be in `out`

If you are an OSM contributor and would like additional help with setup or have feature requests, feel free to email me at mail@themismegas.com or open an issue on this repository.

# Shortcomings
- The processing time is a little bit slow
  - About 2-3 frames/s on my Ryzen 5 2500 system
  - Has the potential to be optimized a bit if it becomes important
- Doesn't automatically read the frames/sec from input files, it needs to be manually entered.
  - It's not an impossible feat to read the frames/sec, I just don't know how to do it yet.
- Accuracy of output hasn't been thoroughly tested yet.
  - It's only passed my quick look test so far
  - The sample rate of the GPS is not the exact same as the amount of time between frames. Using the most recent two GPS samples and the relative time between them and the current frame I interpolate the likely location. The lazy way would have been to just use the most recent sample to the current frame, but I thought it would be better to interpolate instead. I haven't actually checked if this results in an actual accuracy improvement or not though.
- Stitching between front and back cameras is not done. There's a hard cut.
  - I'm sure with some time I can implement this, but because this is just intended for mapping I didn't see the value in taking the time.
