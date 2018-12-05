# Design overview

## Storage

I'm assuming data is coming from two places:

1. User API
1. Game CSV

The solution uses Redis as the data store. It is in memory, super fast,
and is single threaded so it is nice for consistency. Redis can be flushed to
disk for persistence.

There's an option to turn on SQL storage, but it's really slow and not needed
to answer any of the questions.


## Analytics

Analytics is stored in the redis server. Running the script `analytics.py` will
push data into a mysql database for your pleasure. You won't have to run that
script manually.


## How to run

Run a redis server through a docker image. Run a sqlite server through another
docker image. Then build and run the Dockerfile provided to load in data and
make the sql views. Then check out the answers through the sql cli.

1. Start redis server in a container:

> `$ docker run --name redis -d redis`

2. Set a mysql password. Doesn't really matter:

> `$ export MYSQL_PASSWORD=pass`

3. Start mysql server in a container:

> `$ docker run --name mysql -d -e MYSQL_RANDOM_ROOT_PASSWORD=yes
> -e MYSQL_DATABASE=connect_four -e MYSQL_USER=connect_four
> -e MYSQL_PASSWORD=${MYSQL_PASSWORD} mysql`

4. Build this docker image:

> `$ docker build -t connect-four .`

5. Wait for the sql server on step 3 to start. Step 4 was probably plenty of
   time to get it booted up, but I'd check to make sure before I started
running my solution:

> `$ docker logs mysql`

6. Run this docker image:

> `$ docker run -e MYSQL_PASSWORD=${MYSQL_PASSWORD} --name app
> --link redis:redis --link mysql:mysql connect-four`

7. Explore sql storage:

> `$ docker run -it --link mysql:mysql --name mysql-cli --rm mysql
> sh -c 'exec mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT"
> --database connect_four -uconnect_four -p'`

You'll be prompted to put in your password. Then you can expore the tables. To
answer the three questions, three queries are provided:

1. `select * from starting_move_percentile_rank;`
2. `select * from nationality;`
3. `select * from new_user;`

The weird characters don't show up well in the Docker image's stdout... If you
want to check to see that they're encoded properly, you can run
`check_characters.py`:

> `$ docker run -e MYSQL_PASSWORD=${MYSQL_PASSWORD} --link mysql:mysql
> connect-four python check_characters.py`


## Improvements

There's no testing. Whoops.

For scaling, if there's only one input stream for user data and
one stream for game data then it'll be able to handle the data; and it will
linearly scale in time with how much more data it needs to load. I could
multi-process streaming user data in with almost no changes, and redis should
be able to handle all the extra requests. On my machine I'm getting 80K SETs
per second and about 90K GETs per second. One problem with streaming in game
data is that without a timestamp, my solution can't readily figure out what a
player's first game's first move was. Otherwise, everything else should scale
fine if I start up more processes to stream game CSVs. Redis is single threaded
so all the increments should work fine.
