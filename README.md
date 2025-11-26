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
• Enable VNC and SSH in raspi-config.
    • name is typically pi@raspberrypi and pass is root
• After finishing code changes, set filesystem to Read-Only in raspi-config (you can re-enable write mode later)