#!/bin/bash

CONFIG_FILE="server_ip.yaml"
TARGET_FILES=(
    "conf.d/app/upstream.conf"
    "conf.d/otel.conf"
)

# Read config and replace in all target files
while IFS=: read -r variable value; do
    for file in "${TARGET_FILES[@]}"; do
        if [ -f "$file" ]; then
            sudo sed -i "s/\\$variable/$value/g" "$file"
        fi
    done
done < "$CONFIG_FILE"

sudo nginx -t && sudo systemctl reload nginx
