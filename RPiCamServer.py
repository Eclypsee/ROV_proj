import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

PAGE = """\
<html>
<head><title>H264 streaming</title></head>
<body>
<h1>Raw H264 stream</h1>
<p>This won't display in a browser. Use the PC client.</p>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.buffer.write(buf)
            self.condition.notify_all()
        return len(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/stream.h264':
            self.send_response(200)
            self.send_header("Content-Type", "video/h264")
            self.end_headers()

            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        data = output.buffer.getvalue()
                        output.buffer.truncate(0)
                        output.buffer.seek(0)

                    if data:
                        self.wfile.write(data)

            except Exception as e:
                logging.warning("Client disconnected: %s", e)

        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='800x450', framerate=30) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='h264', bitrate=1000000)

    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
