# Datawarehousing final project
by Pedro Freitas and Alex Pappas

## Part 1

### Introduction

First, we scrape the Basketball Reference website to get data on all nba games of the season.
Then, we store it in a MongoDB database.

### Reproducing it

After running an AWS Ubuntu 18.4 instance, we have to install docker. To do so run the following commands:

```shell
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

To install MongoDB run:
```shell
docker run -d --name mongodb -p 27017:27017 mongo
```

Then, our project can be run from the following docker image:

```shell
docker run --name nbaseason --net host ppfreitas/nbastats
```
A "Done" message will appear when it is done. It takes about 15 to 20 minutes the first time it loads an empty database.

After this time, we can check if loading was done correctly by going to mongodb bash:

```shell
docker exec -it mongodb bash
mongo
use season2020
db.games.count()
```

Final step is to setup cron to update oud database daily. To do so, run ```crontab -e``` and add the following command to your cron file:

```shell
0 8 * * * docker restart nbaseason
```
