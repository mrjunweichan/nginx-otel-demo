#!/bin/bash
locust -f /mnt/locust/locustfile.py &

sleep 5

curl -X POST \
  -F "user_count=50" \
  -F "spawn_rate=10" \
  http://localhost:8089/swarm
