import logging

from connect_four import orm, users


LOGGER = logging.getLogger(__name__)

FIRST = 1
SECOND = 2
DRAW = 3


def load_games(sql_session, redis_session, csv):
    """Load a CSV worth of game data.

    Each move is stored in the sql database.
    """
    LOGGER.info(f"Starting to load {csv}.")
    io_stream = open(csv, "rb")
    for game in game_generator(io_stream, sql_session):
        # Increment counters for first question.
        LOGGER.info(game)
        starting_move = game["starting_move"]
        result = game["result"]
        redis_session.hincrby(f'move:{starting_move}', result, 1)

        # Increment counters for second question
        for user_id in game["p1"], game["p2"]:
            nationality = users.get_nationality(sql_session, user_id)
            redis_session.incr(f"nationality:{nationality}")

    LOGGER.info(f"Done loading {csv}.")


def game_generator(io_stream, sql_session):
    """Streams moves into the sql database. Returns something for the redis
    server.

    Return:
        dict:
            Some data for the redis server.
    """
    io_stream.readline()  # dump header
    for line in io_stream:
        game_id, player_id, move_number, column, result = map(
                _try_int, line.decode().split(","))
        move = orm.Move(game_id=game_id, player_id=player_id,
                        move_number=move_number, column=column, result=result)
        if sql_session:
            sql_session.add(move)

        if move_number == 1:
            # Opening move
            game = Game(player_id, column)
        elif move_number == 2:
            # Second move
            game.add_player_two(player_id)
        elif result:
            # Game ended
            if sql_session:
                sql_session.commit()
            yield game.end(player_id, result)
        else:
            # All other moves
            pass


class Game(object):
    """This is a really simple structure to keep track of game data."""

    def __init__(self, first_player, starting_move):
        self.first_player = first_player
        self.starting_move = starting_move

    def add_player_two(self, player):
        self.second_player = player

    def end(self, player, result):
        if result == "draw":
            game_result = DRAW
        else:
            assert result == "win"
            if player == self.first_player:
                game_result = FIRST
            else:
                game_result = SECOND
        return dict(starting_move=self.starting_move,
                    result=game_result,
                    p1=self.first_player,
                    p2=self.second_player,
                    )

    def reset(self):
        self.first_player = None
        self.second_player = None
        self.starting_move = None
        self.result = None


def _try_int(value: str):
    """Try to convert value to an integer."""
    try:
        return int(value)
    except ValueError:
        return value.strip()
