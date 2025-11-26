• Use Raspberry Pi 3 with Buster OS  
• In raspi-config → Interfacing Options → enable Camera, enable I2C
• In raspi-config → enable Auto Login
• Make sure hostname is raspberrypi

Run on the Pi:
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod

sudo pip3 install Adafruit-GPIO
sudo pip3 install Adafruit-ADS1x15

• Make camserver, controlserver, telemetryserver executable (chmod +x)  
• Add all three to crontab so they start on boot
        @reboot sleep 5 && /usr/bin/python3 /home/pi/ROV_proj/RPiCamServer.py >> /home/pi/rovcamera.log 2>&1
        @reboot sleep 5 && /usr/bin/python3 /home/pi/ROV_proj/ControlServer.py >> /home/pi/rovcontrol.log 2>&1
        @reboot sleep 5 && /usr/bin/python3 /home/pi/ROV_proj/TelemetryServer.py >> /home/pi/rovtelem.log 2>&1

• Enable VNC and SSH in raspi-config.
    • name is typically pi@raspberrypi and pass is root
• After finishing code changes, set filesystem to Read-Only in raspi-config (you can re-enable write mode later)