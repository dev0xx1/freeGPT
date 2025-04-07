#### Deploy to DO
```
doctl apps create --spec /home/dev0xx/Documents/repos/freeGPT/do-config.yaml
```

#### Run docker container
```
docker run freegpt-agent --env-file path/to/.env image_name
```

#### Local postgresDB

```
docker run 
  --name freegpt_db 
  -e POSTGRES_USER=freegpt 
  -e POSTGRES_PASSWORD=adminpw01 
  -p 5432:5432 
  -v $HOME/docker_vols/freegpt/:/var/lib/postgresql/data 
  -d postgres:latest
```