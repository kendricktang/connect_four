# Design overview

![design](img/design.png)

## Data sources

I'm assuming data is coming from two places:

1. User API
1. Game CSV


## SQL Storage

I'll have two processes to ETL data from each source. The data go into a SQL
storage (sqlite for now) pretty much a straight up upload. This won't allow us
to answer any of the questions, but will store the data so

* data is a bit more local and more easily accessible
* data can be backed up
* data can be used to regenerate results on the analytics side (see below)

SQL is used because it is an industry standard and is really reliable and easy
to use.


## Analytics

The analytics will be run by a Redis server. Redis is known for being really
fast since it is in memory. It scales and has built in replication, but I've
never needed to do anything like that. I think it is pretty light weight
(really easy to install and has a small foot print). It can be flushed to disk
for persistance, too.

I'm ignoring the question related about emails for now, and will go back and
think about that later. For now, I'll use Redis in the following way:

1. When I see a US game, `incr nationality US` (or initialize it to 1)
1. When I see a game which had first move in the second space and resulted in
   loss for the first player, `incr move:1 loss` (or initialize it to 1)

Some thoughts about load... currently there's almost no load because there are
~200 countries and (1, 2, 3, 4) X (win, loss, tie) -> ~ 212 numbers that are
stored and incremented. Easy peasy.


# TODO

SQL query user nationalities? Or keep user data in redis, too?

Multi-thread streaming csv and pinging the user api for better speeds
