[Unit]
Description=ROV Startup Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ROV_proj

# Wait for ADS1115 via ExecStartPre 
ExecStartPre=/bin/bash -c 'while ! i2cget -y 1 0x48 0x00 &>/dev/null; do sleep 1; done'

# script
ExecStart=/bin/bash /home/pi/ROV_proj/start_all.sh

[Install]
WantedBy=multi-user.target
