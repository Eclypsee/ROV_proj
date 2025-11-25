• Use Raspberry Pi 3 with Buster OS  
• In raspi-config → Interfacing Options → enable Camera 
• In raspi-config → enable Auto Login
• Make sure hostname is raspberrypi

Run on the Pi:
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod

• Make camserver, controlserver, telemetryserver executable (chmod +x)  
• Add all three to crontab so they start on boot
• After finishing code changes, set filesystem to Read-Only in raspi-config (you can re-enable write mode later)