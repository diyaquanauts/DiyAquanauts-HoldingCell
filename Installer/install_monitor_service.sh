#!/bin/bash

# Define the path and name of the service file
SERVICE_PATH="/etc/systemd/system/"
SERVICE_NAME="power_scanner.service"

# Check for root permissions
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo or as root."
    exit 1
fi

# Create the service file content
cat > ${SERVICE_PATH}${SERVICE_NAME} <<EOL
[Unit]
Description=Power Monitor Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path_to_your_script/your_script_name.py
Restart=always
User=username
Group=groupname
Environment=PATH=/usr/bin:/usr/local/bin
WorkingDirectory=/path_to_your_script/

[Install]
WantedBy=multi-user.target
EOL

# Reload the systemd manager configuration
systemctl daemon-reload

# Enable and start the service
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

# Show the status
systemctl status ${SERVICE_NAME}

