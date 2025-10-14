#!/bin/bash
locust -f /mnt/locust/locustfile.py &
LOCUST_PID=$!
sleep 5
python3 -c "import requests; requests.post('http://localhost:8089/swarm', data={'user_count': 15, 'spawn_rate': 10})"
wait $LOCUST_PID
