import pygame
import time
import socket
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QThread

import requests
# button 2 is x and button 1 is b

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
                        # time.sleep(0.1)

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

                for chunk in r.iter_content(chunk_size=16384):
                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        img = QtGui.QImage.fromData(jpg)
                        if not img.isNull():
                            self.frame_received.emit(img)
                            # time.sleep(0.01)

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
        
        self.prev_buttons = [0] * self.js.get_numbuttons()
        self.tilt = 90   # start angle

        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.target_addr = socket.gethostbyname("raspberrypi")
            print("Resolved raspberrypi to:", self.target_addr)
        except Exception as e:
            print("Hostname resolve failed:", e)
            self.target_addr = "192.168.1.50"   # optional fallback static IP


        # GUI
        self.label_video = QtWidgets.QLabel()
        self.label_telem = QtWidgets.QLabel("Telemetry: ---")
        font = self.label_telem.font()
        font.setPointSize(14)
        self.label_telem.setFont(font)
        
        self.label_cam = QtWidgets.QLabel("Cam: ---")
        font2 = self.label_cam.font()
        font2.setPointSize(14)
        self.label_cam.setFont(font2)

        self.showMaximized()    
        

        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_video)
        layout.addWidget(self.label_telem)
        layout.addWidget(self.label_cam)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.label_video.setText("No video stream")
        self.label_telem.setText("No telemetry")
        
        # start dns retry timer
        self.dns_timer = QtCore.QTimer()
        self.dns_timer.timeout.connect(self.refresh_dns)
        self.dns_timer.start(5000)   # every 5 seconds

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
        pix = pix.scaled(
            1200, 800,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label_video.setPixmap(pix)

    # update battery label
    def update_telem(self, text):
        self.label_telem.setText("Telemetry(Angle, V):   " + text)
        
    # refresh dns occasionally if it fails
    def refresh_dns(self):
        try:
            new_addr = socket.gethostbyname("raspberrypi")
            if new_addr != self.target_addr:
                print(f"DNS updated: {self.target_addr} → {new_addr}")
                self.target_addr = new_addr
        except:
            pass

    # send joystick commands
    def send_control(self):
        pygame.event.pump()

        fx = self.js.get_axis(0)
        fy = -self.js.get_axis(1)
        z  = -self.js.get_axis(3)

        fx *= 0.4      # sensitivity scaling
        fy *= 1.0
        z  *= 1.0

        L = fy + fx # mixing
        R = fy - fx
        
        L = max(min(L, 1.0), -1.0) #clamping
        R = max(min(R, 1.0), -1.0)
        
        L = int(L * 100) #data conversion
        R = int(R * 100)
        V = int(z*100)
        
         # ---- BUTTON LOGIC ----
        # button 2 = X → tilt += 5
        # button 1 = B → tilt -= 5

        # Check button 2 (X)
        b2 = self.js.get_button(2)
        if b2 == 1 and self.prev_buttons[2] == 0:   # button DOWN event
            self.tilt += 10

        # Check button 1 (B)
        b1 = self.js.get_button(1)
        if b1 == 1 and self.prev_buttons[1] == 0:   # button DOWN event
            self.tilt -= 10

        # Clamp servo angle
        self.tilt = max(60, min(180, self.tilt))

        # Save previous states
        self.prev_buttons[2] = b2
        self.prev_buttons[1] = b1

        # Update GUI label
        self.label_cam.setText(f"Camera tilt:    {self.tilt}")
    
        packet = f"{L},{R},{V},{self.tilt},AutoOff"

        print(packet)
        
        try:
            self.sock.sendto(packet.encode(), (self.target_addr, 21567))
        except OSError as e:
            print("Control send failed:", e)

        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = Controller()
    win.show()
    app.exec()