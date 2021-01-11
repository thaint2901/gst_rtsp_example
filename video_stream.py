# import the necessary packages
from threading import Thread
import cv2
import time


class VideoStream:
    def __init__(self, src=0, name="VideoStream"):
        self.src = src
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        self.name = str(name)
        self.running = True
        self.reconnected = False
        self.updated = False

        self.timeout = 10
        self.disconnected = None


    def start(self):
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self


    def update(self):
        while self.running:
            if self.reconnected:
                self.stream.release()
                del self.stream
                self.stream = cv2.VideoCapture(self.src)
                self.reconnected = False

            (grabbed, frame) = self.stream.read()
            if not self.updated:
                self.updated = True
                self.grabbed, self.frame = grabbed, frame


    def read(self, override=True):
        if self.frame is None:
            if self.disconnected is None:
                self.disconnected = time.time()
            elif time.time() - self.disconnected > self.timeout:
                # logger.warning("Cannot connect. Reconnecting camera id={}...".format(self.name))
                time.sleep(30)  # sleep before reconnect
                self.reconnect()
                self.disconnected = None
                # self.stop()
        else:
            self.disconnected = None

        if self.updated:
            self.updated = False
            return self.frame

        elif override:
            return self.frame


    def stop(self):
        self.running = False
    

    def reconnect(self, src=None):
        self.reconnected = True
        if src is not None:
            self.src = src
