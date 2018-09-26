#!/bin/sh
docker exec -it runner-lab gitlab-runner register --docker-volumes /config:/config

