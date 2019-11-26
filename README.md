# Datawarehousing final project
by Pedro Freitas and Alex Pappas

## Part 1

### Introduction
First, we scrape the Basketball Reference to get data on all nba games of the season.
Then, we store it in a MongoDB.

### Reproducing it

After running an AWS Ubuntu 18.4 instance, we have to install docker. To do so run the following commands:

```shell
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

To install MongoDB
```shell
docker run -d --name mongodb -p 27017:27017 mongo
docker exec -it mongodb bash
```
Run our project docker container

```shell
docker run --name nbaseason --net host ppfreitas/nbaseason
```
A "Done" message will appear when it is done. It can take a few minutes the first time it loads an empty database. 

To check if loading was done correctly

```shell
docker exec -it mongodb bash
mongo
use database
db.games.count()
```
