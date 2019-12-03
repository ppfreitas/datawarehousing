#!/bin/sh

docker run -d --name mongodb -p 27017:27017 mongo
docker run --name nbaseason --net host ppfreitas/nbastats
