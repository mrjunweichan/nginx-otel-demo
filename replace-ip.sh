#!/bin/bash

CONFIG_FILE="server_ip.yaml"
TARGET_FILES=(
    "otel/prometheus/prometheus.yaml"
    "otel/.env"
    "app/.env"
    "nginx/conf.d/app/upstream.conf"
    "nginx/conf.d/otel.conf"
)

# Read config and replace in all target files
while IFS=: read -r variable value; do
    for file in "${TARGET_FILES[@]}"; do
        if [ -f "$file" ]; then
            # If it's a template file, write to .conf instead
            if [[ "$file" == *.template ]]; then
                output_file="${file%.template}"
                sudo sed "s/\\$variable/$value/g" "$file" > "$output_file"
            else
                # Regular file, replace in-place
                sudo sed -i "s/\\$variable/$value/g" "$file"
            fi
        fi
    done
done < "$CONFIG_FILE"

# sudo nginx -t && sudo systemctl restart nginx
