#!/bin/bash
locust -f /mnt/locust/locustfile.py &

sleep 5

python3 -c "import requests; requests.post('http://localhost:8089/swarm', data={'user_count': 50, 'spawn_rate': 10})"
