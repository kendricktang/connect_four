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

Analytics reads from the redis server.


## How to run

Run a redis server through a docker image. Then build and run the Dockerfile
provided.

1. `docker run --name redis -d redis`
2. `docker build -t connect-four .`
3. `docker run --name app --link redis:redis connect-four`


## TODO

Add numbers to the improvement section, mainly about why it'll all still fit in
memory.


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
