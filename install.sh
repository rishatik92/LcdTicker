#!/bin/bash
USERNAME=pi
SERVICE_NAME=lcd-ticker@$USERNAME
CURENT_FILE=$(readlink -f $0)
LCD_TICKER_PATH=$(dirname "${CURENT_FILE}")

echo "
[Unit]
Description=Lcd Ticker service
After=network-online.target

[Service]
Type=simple
User=%i
ExecStart=/usr/bin/python3 $LCD_TICKER_PATH/run.py
WorkingDirectory=$LCD_TICKER_PATH
Restart=always

[Install]
WantedBy=multi-user.target
" >> /etc/systemd/system/${SERVICE_NAME}.service

systemctl --system daemon-reload
systemctl enable $SERVICE_NAME
service $SERVICE_NAME start
