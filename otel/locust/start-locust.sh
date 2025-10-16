#!/bin/bash
locust -f /mnt/locust/locustfile.py &
LOCUST_PID=$!
sleep 10
for i in {1..5}; do
  python3 -c "import requests; requests.post('http://localhost:8089/swarm', data={'user_count': 15, 'spawn_rate': 10})" && break
  echo "Attempt $i: Failed to start swarm, retrying in 5 seconds..."
  sleep 5
done
wait $LOCUST_PID
