# import io
# import picamera
# import logging
# import socketserver
# from threading import Condition
# from http import server
# PAGE="""\
# <html>
# <head>
# <title>picamera MJPEG streaming demo<\title>
# </head>
# <body>
# <h1>PiCamera MJPEG Streaming Demo<\h1>
# <img src="stream.mjpg" width="640" height = "480" />
# <\body>
# <\html>
# """
# class StreamingOutput(object):
#     def __init__(self):
#         self.frame = None
#         self.buffer = io.BytesIO()
#         self.condition = Condition()
#     def write(self, buf):
#         if buf.startswith(b'\xff\xd8'):
#             self.buffer.truncate()
#             with self.condition:
#                 self.frame = self.buffer.getvalue()
#                 self.condition.notify_all()
#             self.buffer.seek(0)
#         return self.buffer.write(buf)
# class StreamingHandler(server.BaseHTTPRequestHandler):
#     def do_GET(self):
#         #print(self.path)
#         if self.path =='/':
#             self.send_response(301)
#             self.send_header('Location','/index.html')
#             self.end_headers()
#         elif self.path == '/index.html':
#             content = PAGE.encode('utf-8')
#             self.send_response(200)
#             self.send_header('Content-Type','text/html')
#             self.send_header('Content-Length', len(content))
#             self.end_headers()
#             self.wfile.write(content)
#         elif self.path == '/stream.mjpg':
#             self.send_response(200)
#             self.send_header('Age',0)
#             self.send_header('Cache-Control', 'no-cache, private')
#             self.send_header('Pragma','no-cache')
#             self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
#             self.end_headers()
#             try:
#                 while True:
#                     with output.condition:
#                         output.condition.wait()
#                         frame = output.frame
#                     self.wfile.write(b'--FRAME\r\n')
#                     self.send_header('Content-Type', 'image/jpeg')
#                     self.send_header('Content-Length',len(frame))
#                     self.end_headers()
#                     self.wfile.write(frame)
#                     self.wfile.write(b'\r\n')
#             except Exception as e:
#                 logging.warning(
#                     'Removed streaming client %s: %s',
#                     self.client_address, str(e))
#         else:
#             self.send_error(404)
#             self.end_headers()
# class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
#     allow_reuse_address = True
#     daemon_threads = True
# with picamera.PiCamera(resolution='800x450',framerate=15) as camera:
#     output = StreamingOutput()
#     camera.start_recording(output, format='mjpeg')
#     camera.rotation = 0
#     try:
#         address = ('', 8000)
#         server = StreamingServer(address,StreamingHandler)
#         server.serve_forever()
#     finally:
#         camera.stop_recording()
import socket
import time
import picamera

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 8000))
server.listen(1)

print("H264 Camera Server Started")

while True:
    print("Waiting for client...")
    conn, addr = server.accept()
    print("Client connected:", addr)

    conn_file = conn.makefile('wb')

    try:
        with picamera.PiCamera(resolution=(1280,720), framerate=30) as camera:
            camera.start_recording(conn_file, format='h264', bitrate=2000000)

            while True:
                camera.wait_recording(1)   # small sleep prevents freezing
    except Exception as e:
        print("Client disconnected:", e)
    finally:
        try:
            camera.stop_recording()
        except:
            pass
        conn_file.close()
        conn.close()
        time.sleep(0.5)
