import pygame
import time
import socket
from PyQt5 import QtCore, QtGui, QtWidgets
import requests


class TelemetryThread(QtCore.QThread):
    telemetry_received = QtCore.pyqtSignal(str)

    def run(self):
        HOST = "raspberrypi"
        PORT = 52849

        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, PORT))
                buffer = ""

                while True:
                    data = s.recv(64).decode()
                    if not data:
                        break

                    buffer += data
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        self.telemetry_received.emit(line)

            except Exception as e:
                print("Telemetry reconnect:", e)
                time.sleep(2)

class VideoThread(QtCore.QThread):
    frame_received = QtCore.pyqtSignal(QtGui.QImage)

    def run(self):
        while True:
            try:
                r = requests.get("http://raspberrypi:8000/stream.mjpg", stream=True, timeout=5)
                bytes_data = b""

                for chunk in r.iter_content(chunk_size=1024):
                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        img = QtGui.QImage.fromData(jpg)
                        if not img.isNull():
                            self.frame_received.emit(img)

            except Exception as e:
                print("Video reconnect:", e)
                time.sleep(2)



class Controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # init joystick
        pygame.init()
        pygame.joystick.init()
        self.js = pygame.joystick.Joystick(0)
        self.js.init()

        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # GUI
        self.label_video = QtWidgets.QLabel()
        self.label_telem = QtWidgets.QLabel("Telemetry: ---")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_video)
        layout.addWidget(self.label_telem)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.label_video.setText("No video stream")
        self.label_telem.setText("No telemetry")

        # start video thread
        self.vthread = VideoThread()
        self.vthread.frame_received.connect(self.update_frame)
        self.vthread.start()

        # start telemetry thread
        self.tthread = TelemetryThread()
        self.tthread.telemetry_received.connect(self.update_telem)
        self.tthread.start()

        # start control timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.send_control)
        self.timer.start(50)   # 20 Hz

    # update GUI with video
    def update_frame(self, img):
        pix = QtGui.QPixmap.fromImage(img)
        self.label_video.setPixmap(pix)

    # update battery label
    def update_telem(self, text):
        self.label_telem.setText("Telemetry: " + text)

    # send joystick commands
    def send_control(self):
        pygame.event.pump()

        fx = self.js.get_axis(0)
        fy = -self.js.get_axis(1)
        z  = -self.js.get_axis(3)

        a = int(max(min(fx * 40, 100), -100))
        b = int(max(min(fy * 100,100), -100))
        c = int(max(min(z  * 100,100), -100))

        L = max(min(a+b, 100), -100)
        R = max(min(b-a, 100), -100)
        V = c
        tilt = 125

        packet = f"{L},{R},{V},{tilt},AutoOff"

        try:
            self.sock.sendto(packet.encode(), ("raspberrypi", 21567))
        except OSError as e:
            print("Control send failed:", e)

        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = Controller()
    win.show()
    app.exec()