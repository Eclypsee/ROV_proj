import socket
import Adafruit_ADS1x15
import time

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

HOST = ''
PORT = 52849
ADDR = (HOST, PORT)

tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(1)

print("Telemetry server waiting for connection...")

def read_voltage():
    try:
        raw = adc.read_adc(0, gain=GAIN)
        voltage = round(raw * 4.096 / (2**15), 2)
        return f"{voltage}V"
    except:
        return "NA"

try:
    while True:
        client, addr = tcpSerSock.accept()
        client.setblocking(False)
        print("Telemetry connected:", addr)

        try:
            while True:
                volts = read_voltage()
                msg = f"1,{volts}\n".encode()
                try:
                    client.send(msg)
                except BlockingIOError:
                    # TCP buffer full → drop telemetry packet
                    pass
                except (BrokenPipeError, ConnectionResetError, OSError):
                    # Client disconnected → break inner loop
                    print("Telemetry connection lost")
                    break
                time.sleep(1)     # 1 second telemetry(its just a battery)
        except Exception as e:
            print("Exception in main loop: ", e)
            
        print("Telemetry client disconnected")
        client.close()

finally:
    tcpSerSock.close()
