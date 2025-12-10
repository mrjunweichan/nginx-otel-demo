**Update IP Address**
Update ip addresses in `../server_ip.yaml`
 
Run update script
```
. server_ip.yaml
```

**Run Applications**
 
```shell
cd /otel
docker compose --env-file .env up -d --build
```
