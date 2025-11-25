import socket
import Cytron27Aug2019 as c
import pigpio
import time
last_cmd_time = time.time()
COMMAND_TIMEOUT = 2.0   # seconds

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

tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpSerSock.settimeout(1)    # so CTRL-C works and accept doesn't block forever

tcpSerSock.bind(ADDR) # this makes this file a server file
tcpSerSock.listen(5)

scale = 0.7


def stop_all():
    c.L(0); c.R(0); c.LV(0); c.RV(0)


try:
    while True:
        
        # Watchdog safety: stop motors if client is silent
        if time.time() - last_cmd_time > COMMAND_TIMEOUT:
            stop_all()
            
        print("Waiting for connection...")
        # accept with timeout so we can break with Ctrl-C
        try:
            tcpCliSock, addr = tcpSerSock.accept()
        except socket.timeout:
            continue

        print("Connected:", addr)

        # client sends ONE message then closes the socket
        buffer = ""
        tcpCliSock.settimeout(0.5)

        try:
            while True:
                chunk = tcpCliSock.recv(BUFSIZE)
                if not chunk:
                    break  # client closed connection → message complete
                buffer += chunk.decode("utf-8")
        except (socket.timeout, ConnectionResetError, OSError, UnicodeDecodeError):
            # treat errors the same: end of message
            pass

        tcpCliSock.close()

        # if nothing received, stop motors and wait for next connection
        if not buffer.strip():
            stop_all()
            continue

        # Parse the message
        parts = buffer.strip().split(",")

        if len(parts) < 5:
            print("Malformed command:", buffer)
            stop_all()
            continue

        try:
            i = float(parts[0])
            j = float(parts[1])
            k = float(parts[2])
            cam = float(parts[3])
            # parts[4] exists. autoOn depths control is not yet implemented
        except ValueError:
            print("Bad number in:", buffer)
            stop_all()
            continue

        # deadzone
        if abs(i) < 5: i = 0
        if abs(j) < 5: j = 0
        if abs(k) < 5: k = 0

        # Servo angle
        angle = 1000 + (cam / 180) * 1000
        angle = max(1000, min(angle, 2000))
        pi.set_servo_pulsewidth(23, angle)

        # Motor control
        c.L(i * scale)
        c.R(j * scale)
        c.LV(k * scale)
        c.RV(k * scale)
        last_cmd_time = time.time()
        time.sleep(0.02)#50hz


except KeyboardInterrupt:
    print("Shutting down...")

finally:
    stop_all()
    pi.set_servo_pulsewidth(23, 0)
    pi.stop()
    tcpSerSock.close()
