### Local postgresDB
/home/othmane
```
docker run 
  --name freegpt_db 
  -e POSTGRES_USER=freegpt 
  -e POSTGRES_PASSWORD=adminpw01 
  -p 5432:5432 
  -v $HOME/docker_vols/freegpt/:/var/lib/postgresql/data 
  -d postgres:latest
```