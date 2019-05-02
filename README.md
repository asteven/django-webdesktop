
### setup test env


This runs:
- guacd
- alpine container with sshd as a test connection
- guacamole java client
- mysql db for java client


```
sudo docker-compose pull
sudo docker-compose up
```

### Start django app

```
./manage.py runserver
```
