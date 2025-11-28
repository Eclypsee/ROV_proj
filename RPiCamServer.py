import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo<\title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo<\h1>
<img src="stream.mjpg" width="640" height = "480" />
<\body>
<\html>
"""
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        #print(self.path)
        if self.path =='/':
            self.send_response(301)
            self.send_header('Location','/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age',0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma','no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length',len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
with picamera.PiCamera(resolution='800x450',framerate=15) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    camera.rotation = 0
    try:
        address = ('', 8000)
        server = StreamingServer(address,StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
# gst-launch-1.0 -v \
#   v4l2src device=/dev/video0 ! \
#   video/x-h264,width=1920,height=1080,framerate=30/1 ! \
#   h264parse config-interval=1 ! \
#   rtph264pay pt=96 mtu=1400 ! \
#   udpsink host=169.254.123.1 port=8000

# use netsh to set eth0 to ip 169.254.123.1 temporarily and set it back after
# gst-launch-1.0 -v udpsrc port=8000 caps="application/x-rtp, media=video, encoding-name=H264, payload=96" ! rtph264depay ! h264parse ! d3d11h264dec ! d3d11videosink sync=false
