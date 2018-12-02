# Design overview

![design](img/design.png)

## Data sources

I'm assuming data is coming from two places:

1. User API
1. Game CSV

## Storage

The solution uses Redis as the data store. It is in memory, super fast,
and is single threaded so it is nice for consistency. Redis can be flushed to
disk for persistence.

There's an option to turn on SQL storage, but it's really slow and not needed
to answer any of the questions.


## Analytics

The three questions are:

1. Out of all the games, what is the percentile rank of each column used as the
   first move in a game? That is, when the first player is choosing a column
   for their first move, which column most frequently leads to that player
   winning the game?

2. How many games has each nationality participated in?

3. Marketing wants to send emails to players that have only played a single
   game. The email will be customized based on whether or not the player won,
   lost, or drew the game. Which players should receive an email, and with what
   customization?

To answer these questions, I will store in Redis:

1. Load User data as hashsets.
1. When I see a US game, `incr nationality US` (or initialize it to 1)
1. When I see a game which had first move in the second space and resulted in
   loss for the first player, `incr move:1 loss` (or initialize it to 1)
1. For each player, increment the number of games stored in a sorted set.

To get answers:

1. `hget move:<col> win` / `sum(hget move:<col> win for col in cols)`
2. `get nat:<nat>`
3. A bit trickier. Get user ids with `zrangebyscore games 1 1` and then get all
   their information.


## SQL Storage

I'll have two processes to ETL data from each source. The data go into a SQL
storage (sqlite for now) pretty much a straight up upload. This won't allow us
to answer any of the questions, but will store the data so

* data is a bit more local and more easily accessible
* data can be backed up
* data can be used to regenerate results on the analytics side (see below)

SQL is used because it is an industry standard and is really reliable and easy
to use.
