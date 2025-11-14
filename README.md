# nginx-otel



Run the following:
```
chmod +x otel/locust/start-locust.sh
mkdir -p otel/tempo/tempo-data/
chown -R 10001:10001 otel/tempo/tempo-data/
chmod -R 775 otel/tempo/tempo-data/

# optional
chmod +x otel/update-app.sh
chmod +x app/update-app.sh
```

If creating in own environment, update the following files:
./otel/env.  
./app/env.  
./nginx/app/upstream.conf  
