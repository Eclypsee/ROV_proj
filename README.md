• Use Raspberry Pi 3 with Buster OS  
• In raspi-config → Interfacing Options → enable Camera, enable I2C
• In raspi-config → enable Auto Login
• Make sure hostname is raspberrypi

Run on the Pi:
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod

sudo pip3 install Adafruit-GPIO
sudo pip3 install Adafruit-ADS1x15

• Make start_all.sh executable (chmod +x)  
    sudo mv /home/pi/ROV_proj/rov_service.ctl /etc/systemd/system/rov_startup.service
    sudo systemctl daemon-reload
    sudo systemctl enable rov_startup.service
    sudo systemctl start rov_startup.service
    systemctl status rov_startup.service

    detect i2c devices. should see 0x48
    sudo i2cdetect -y 1


• Enable VNC and SSH in raspi-config.
    • name is typically pi@raspberrypi and pass is root
• After finishing code changes, set filesystem to Read-Only in raspi-config (you can re-enable write mode later)