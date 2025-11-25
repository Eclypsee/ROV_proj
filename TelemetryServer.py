import socket
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

HOST = ''
PORT = 52849
ADDR = (HOST, PORT)

tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpSerSock.settimeout(1.0)  # avoid blocking forever

tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

print("Waiting for connection...")

def read_voltage():
    try:
        raw = adc.read_adc(0, gain=GAIN)
        voltage = round(raw * 4.096 / (2**15), 2)
        return f"{voltage}V"
    except:
        return "NA"

try:
    while True:
        # accept a connection (non-blocking)
        try:
            tcpDataSock, addr = tcpSerSock.accept()
        except socket.timeout:
            continue

        print("Connected from:", addr)

        volts = read_voltage()
        message = f"1,{volts}\r\n"

        try:
            tcpDataSock.send(message.encode("utf-8"))
        except OSError:
            print("Send failed")

        tcpDataSock.close()

finally:
    tcpSerSock.close()
    print("Server closed.")
