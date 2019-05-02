
### setup test env


This runs:
- guacd
- alpine container with sshd as a test connection
- guacamole java client
- mysql db for java client

WARNING: This exposes some ports on the host ip.
   Do not use in an untrusted network.

```
sudo docker-compose pull
sudo docker-compose up
```

### Start django app

```
pipenv install
pipenv run ./manage.py runserver
```
