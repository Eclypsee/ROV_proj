import socket
import Cytron27Aug2019 as c
import pigpio
import time
last_cmd_time = time.time()
COMMAND_TIMEOUT = 2.0

# --- Servo Setup ---
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio daemon not running")

pi.set_mode(23, pigpio.OUTPUT)
pi.set_servo_pulsewidth(23, 1500)
print("servo setup")

HOST = ''
PORT = 21567
BUFSIZE = 1024
ADDR = (HOST, PORT)

# ------- UDP instead of TCP -------
udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSock.settimeout(0.5)
udpSock.bind(ADDR)
# ----------------------------------

scale = 0.7

def stop_all():
    c.L(0); c.R(0); c.LV(0); c.RV(0)

try:
    while True:

        # watchdog
        if time.time() - last_cmd_time > COMMAND_TIMEOUT:
            stop_all()

        try:
            data, addr = udpSock.recvfrom(BUFSIZE)
        except socket.timeout:
            continue

        buffer = data.decode("utf-8").strip()

        if not buffer:
            stop_all()
            continue

        parts = buffer.split(",")
        if len(parts) < 5:
            print("Malformed command:", buffer)
            stop_all()
            continue

        try:
            i = float(parts[0])
            j = float(parts[1])
            k = float(parts[2])
            cam = float(parts[3])
        except ValueError:
            print("Bad number:", buffer)
            stop_all()
            continue

        # deadzone
        if abs(i) < 5: i = 0
        if abs(j) < 5: j = 0
        if abs(k) < 5: k = 0

        # Servo
        angle = 1000 + (cam / 180) * 1000
        angle = max(1000, min(angle, 2000))
        pi.set_servo_pulsewidth(23, angle)

        # Motors
        c.L(i * scale)
        c.R(j * scale)
        c.LV(k * scale)
        c.RV(k * scale)

        last_cmd_time = time.time()
        time.sleep(0.02)

except KeyboardInterrupt:
    print("Shutting down...")

finally:
    stop_all()
    pi.set_servo_pulsewidth(23, 0)
    pi.stop()
    udpSock.close()
