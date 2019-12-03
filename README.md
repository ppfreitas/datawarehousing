# Datawarehousing final project
by Pedro Freitas and Alex Pappas

## Part 1

### Introduction

First, we scrape the Basketball Reference to get data on all nba games of the season.
Then, we store it in a MongoDB database.

### Reproducing it

After running an AWS Ubuntu 18.4 instance, we have to install docker. To do so run the following commands:

```shell
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

To install MongoDB
```shell
docker run -d --name mongodb -p 27017:27017 mongo
```

Then, our project can be run from docker container

```shell
<<<<<<< HEAD
docker run --name nbaseason --net host ppfreitas/nbastats
=======
docker run --name nbastats --net host ppfreitas/nbastats
>>>>>>> 5f4c69a8ac0a8baeb49f87715602cc246e966004
```
A "Done" message will appear when it is done. It can take a few minutes the first time it loads an empty database. 

To check if loading was done correctly, we can to our mongodb bash and manually check for 

```shell
docker exec -it mongodb bash
mongo
use docker_test
db.games.count()
```

Final step is to setup cron to update oud database daily. To do so, run ```shell crontab -e``` and add the following command to your cron file 

```shell
0 8 * * * docker restart nbaseason
```
