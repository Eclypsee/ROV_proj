[Unit]
Description=ROV Startup Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ROV_proj

# Wait for ADS1115 via ExecStartPre 
ExecStartPre=/bin/bash -c 'timeout=20; \
  while ((timeout > 0)); do \
    if i2cget -y 1 0x48 0x00 &>/dev/null; then \
      exit 0; \
    fi; \
    sleep 1; \
    ((timeout--)); \
  done; \
  echo "ADS1115 not detected after 20s — continuing anyway"; \
  exit 0'

# script
ExecStart=/bin/bash /home/pi/ROV_proj/start_all.sh

[Install]
WantedBy=multi-user.target
