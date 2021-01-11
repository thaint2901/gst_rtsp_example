# #!/usr/bin/env python

# import sys
# import gi

# gi.require_version('Gst', '1.0')
# gi.require_version('GstRtspServer', '1.0')
# from gi.repository import Gst, GstRtspServer, GObject, GLib

# loop = GLib.MainLoop()
# Gst.init(None)

# class TestRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
#     def __init__(self):
#         GstRtspServer.RTSPMediaFactory.__init__(self)

#     def do_create_element(self, url):
#         #set mp4 file path to filesrc's location property
#         src_demux = "filesrc location=/mnt/sda2/ExternalHardrive/datasets/heatmap/tokyo2.mp4 ! qtdemux name=demux"
#         h264_transcode = "demux.video_0"
#         #uncomment following line if video transcoding is necessary
#         #h264_transcode = "demux.video_0 ! decodebin ! queue ! x264enc"
#         pipeline = "{0} {1} ! queue ! rtph264pay name=pay0 config-interval=1 pt=96".format(src_demux, h264_transcode)
#         print ("Element created: " + pipeline)
#         return Gst.parse_launch(pipeline)

# class GstreamerRtspServer():
#     def __init__(self):
#         self.rtspServer = GstRtspServer.RTSPServer()
#         factory = TestRtspMediaFactory()
#         factory.set_shared(True)
#         mountPoints = self.rtspServer.get_mount_points()
#         mountPoints.add_factory("/stream1", factory)
#         self.rtspServer.attach(None)

# if __name__ == '__main__':
#     s = GstreamerRtspServer()
#     loop.run()


#!/usr/bin/env python3

import cv2
import gi
import time
from video_stream import VideoStream

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject


class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, url, **properties):
        super(SensorFactory, self).__init__(**properties)
        self.vs = VideoStream(url).start()
        self.number_frames = 0
        self.fps = 20
        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        self.shape = (720, 1280)
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width={},height={} ' \
                             '! videoconvert ! video/x-raw,format=I420 ' \
                             '! x264enc ! queue ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96'.format(self.shape[1], self.shape[0])

    def on_need_data(self, src, lenght):
        # time.sleep(0.1)
        frame = self.vs.read()
        if frame is None:
            return
        # print(frame)
        frame = cv2.resize(frame, self.shape[::-1])
        data = frame.tostring()
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)
        buf.duration = self.duration
        timestamp = self.number_frames * self.duration
        buf.pts = buf.dts = int(timestamp)
        buf.offset = timestamp
        self.number_frames += 1
        retval = src.emit('push-buffer', buf)
        print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames, self.duration, self.duration / Gst.SECOND))
        if retval != Gst.FlowReturn.OK:
            print(retval)

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)


class GstServer():
    def __init__(self):
        GObject.threads_init()
        Gst.init(None)

        self.rtspServer = GstRtspServer.RTSPServer()
        self.rtspServer.set_service("8554")
        auth = GstRtspServer.RTSPAuth()
        token = GstRtspServer.RTSPToken()
        token.set_string('media.factory.role', "user")
        basic = GstRtspServer.RTSPAuth.make_basic("user", "password")
        auth.add_basic(basic, token)
        self.rtspServer.set_auth(auth)

        permissions = GstRtspServer.RTSPPermissions()
        permissions.add_permission_for_role("user", "media.factory.access", True)
        permissions.add_permission_for_role("user", "media.factory.construct", True)

        # self.factory = SensorFactory("rtsp://admin:huongcang1988@huongcangqt.dyndns.info:554/Streaming/Channels/101/")
        self.factory = SensorFactory("rtsp://admin:meditech123@192.168.101.99:556")
        self.factory.set_permissions(permissions)
        self.factory.set_shared(True)
        mountPoints = self.rtspServer.get_mount_points()
        mountPoints.add_factory("/test", self.factory)
        
        # self.factory2 = SensorFactory("rtsp://admin:huongcang1988@huongcangpxl.dyndns.info:554/Streaming/Channels/101/")
        # self.factory2.set_permissions(permissions)
        # self.factory2.set_shared(True)
        # mountPoints = self.rtspServer.get_mount_points()
        # mountPoints.add_factory("/test1", self.factory2)


        self.rtspServer.attach(None)
        loop = GObject.MainLoop()
        loop.run()


# class GstServer(GstRtspServer.RTSPServer):
#     def __init__(self, **properties):
#         super(GstServer, self).__init__(**properties)
#         self.factory = SensorFactory()
#         self.factory.set_shared(True)
#         self.get_mount_points().add_factory("/test", self.factory)
#         self.attach(None)


# GObject.threads_init()
# Gst.init(None)

server = GstServer()

# loop = GObject.MainLoop()
# loop.run()


# import logging

# import gi

# from gst.caps import CapsRegistry
# from gst.pipe_loader import PipelineLoader
# from gst.pipeline import Pipeline

# gi.require_version('Gst', '1.0')
# gi.require_version('GstRtspServer', '1.0')
# from gi.repository import Gst, GstRtspServer

# logger = logging.getLogger('logic.gst.server')


# class RtspFactory(GstRtspServer.RTSPMediaFactory):

#     yaml_file = None    # Pipe config file
#     caps_store = None   # type: CapsRegistry
#     origin_pipe = None  # type: Pipeline

#     def do_create_element(self, uri):
#         # Create new pipe for rtsp from definition
#         pipe = PipelineLoader.create_base_pipe(self.get_launch())

#         # TODO rtsp connections can be loaded from gui HERE
#         yaml_defs = PipelineLoader.load_yaml_blocking(self.yaml_file)
#         PipelineLoader.process_yaml(pipe, self.caps_store, yaml_defs)
#         PipelineLoader.process_filters(pipe, self.caps_store, yaml_defs)

#         return pipe.gst_element


# class RtspServer:

#     def __init__(self, caps_store):
#         self.caps_store = caps_store  # type: CapsRegistry
#         self.server_id = None
#         self.port = '8554'

#         logger.info('Creating RTSP server')
#         self.server = GstRtspServer.RTSPServer()
#         self.auth = GstRtspServer.RTSPAuth()
#         self.token = GstRtspServer.RTSPToken()
#         self.token.set_string('role', 'user')
#         print(self.token.get_string('role'))
#         self.token.set_bool('perm', True)
#         print(self.token.is_allowed('perm'))
#         basic = GstRtspServer.RTSPAuth.make_basic('user', 'user')
#         self.auth.set_default_token(self.token)
#         self.auth.add_basic(basic, self.token)

#         self.permissions = GstRtspServer.RTSPPermissions()
#         # self.permissions.add_role("user")
#         self.permissions.add_permission_for_role("user", "media.factory.access", True)
#         self.permissions.add_permission_for_role("user", "media.factory.construct", True)
#         self.permissions.add_permission_for_role("user", "auth.check.media.factory.access", True)
#         self.permissions.add_permission_for_role("user", "auth.check.media.factory.construct", True)

#     def start(self, mainloop):
#         logger.info('Starting RTSP server')

#         self.server.set_auth(self.auth)

#         self.server.set_service(self.port)
#         self.server.connect("client-connected", self.client_connected)
#         self.server_id = self.server.attach(mainloop)

#     def close(self):
#         # GObject.source_remove(self.server_id)
#         logger.info('Stop RTSP server')

#     async def create_factory(self, uri, yaml_file_name, gst_pipe):
#         logger.info('Creating RTSP Factory from YAML def: ' + yaml_file_name)
#         factory = RtspFactory()
#         factory.set_shared(True)
#         factory.caps_store = self.caps_store
#         # factory.set_eos_shutdown(True)

#         # save the url of the stream - base uses this to store the launch line :P
#         factory.set_launch(uri)

#         # save some reference to the definition of the pipe to create
#         factory.yaml_file = yaml_file_name

#         # save the origin pipe that provides the stream, None if (restarting it) is not needed
#         factory.origin_pipe = gst_pipe.gst_element if gst_pipe else None
#         factory.connect("media-configure", self.on_media_configure)

#         factory.set_permissions(self.permissions)

#         mounts = self.server.get_mount_points()
#         mounts.add_factory('/' + uri, factory)
#         logger.info('RTSP stream is available at rtsp://0.0.0.0:{0}/{1}'.format(self.port, uri))

#     def remove_factory(self, uri):
#         logger.info('Remove RTSP Factory: ', uri)
#         mounts = self.server.get_mount_points()
#         mounts.remove_factory('/' + uri)

#     def on_media_configure(self, factory, media):
#         logger.info('Start RTSP "%s"\n' % factory.get_launch())

#         if factory.origin_pipe:
#             logger.warning('FIXME: Restart origin pipe...')
#             factory.origin_pipe.set_state(Gst.State.READY)
#             factory.origin_pipe.set_state(Gst.State.PLAYING)

#     def client_connected(self, arg1, arg2):
#         logger.info('Rtsp client connected.')