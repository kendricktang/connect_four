"""Calculate the numbers that yall are looking for.

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

"""

import argparse

from connect_four import db, games


def first_question(r):
    """
    Out of all the games, what is the percentile rank of each column used as
    the first move in a game? That is, when the first player is choosing a
    column for their first move, which column most frequently leads to that
    player winning the game?

    I'm interpreting this question as:

    Number of wins where first move is <column> divided by number of games
    where first move is <column>.
    """
    for first_move in [1, 2, 3, 4]:
        wins = int(r.hget(f"move:{first_move}", games.FIRST))
        losses = int(r.hget(f"move:{first_move}", games.SECOND))
        draws = int(r.hget(f"move:{first_move}", games.DRAW))
        total = wins + losses + draws
        pr = wins / total
        print(f"Where the first move was {first_move}, "
              f"out of {total} games, {wins} were wins. "
              f"Percentile rank: {pr}")


def second_question(r):
    """How many games has each nationality participated in?"""
    nat_keys = r.keys("nat:*")
    for nat_key in nat_keys:
        nat = nat_key.split(":")[-1]
        games = r.get(nat_key)
        print(f"The {nat} nationality played {games} games.")


def third_question(r):
    """
    Marketing wants to send emails to players that have only played a single
    game. The email will be customized based on whether or not the player won,
    lost, or drew the game. Which players should receive an email, and with
    what customization?
    """
    one_game_players = r.zrangebyscore("games", 1, 1)
    print("user_id,email,result")
    for player in one_game_players:
        email, result = r.hmget(f"user:{player}", "email", "first_game")
        print(f"{player},{email},{result}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", type=int, nargs="+", default=None)
    args, _ = parser.parse_known_args()

    questions = args.question or [1, 2, 3]
    r = db.get_redis()
    if 1 in questions:
        first_question(r)
    if 2 in questions:
        second_question(r)
    if 3 in questions:
        third_question(r)
