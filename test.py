from imutils.video import VideoStream
import cv2
import imutils
import time

vs = VideoStream("rtsp://user:password@127.0.0.1:8554/test").start()  # mdt ban

while True:
    frame = vs.read()
    if frame is None:
        # print("None")
        continue
    print(frame)