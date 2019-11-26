# Datawarehousing final project
by Pedro Freitas and Alex Pappas

## Part 1

### Introduction
First, we scrape the Basketball Reference to get data on all nba games of the season.
Then, we store it in a MongoDB.

### Reproducing it

To install MongoDB
```shell
docker run -d --name namedb -p 27017:27017 mongo
docker exec -it mongodb bash
```

Run our project docker container

```shell
docker run --name nbaseason -d --net host ppfreitas/nbaseason
```

