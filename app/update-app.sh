#!/bin/bash

clear

echo "Updating application..."
docker compose down

cd ../

git pull https://github.com/mrjunweichan/nginx-otel-demo.git

cd app/

docker compose --env-file .env up -d --build

read -p "Update complete..."

clear

docker ps -a
