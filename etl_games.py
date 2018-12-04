"""Extract user data into data storage.

Extract to SQL storage with --sql flag.

Flush storage with --flush. This will flush redis of keys related to game data.
This will not clean up the SQL `move` table... but I'm not using that.
"""

import argparse
import logging
import time

from connect_four import db, games

LOGGER = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--flush", action="store_true", help="Flush data.")
    parser.add_argument("--sql", action="store_true", help="ETL to sql.")
    parser.add_argument("-q", "--quiet", action="count", default=0,
                        help="Be quiet.")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Be verbose.")
    args, _ = parser.parse_known_args()

    logging_level = logging.INFO + 10 * args.quiet - 10 * args.verbose
    logging.basicConfig(level=logging_level)

    redis_session = db.get_redis()

    if args.flush:
        move_keys = redis_session.keys("move:*")
        nat_keys = redis_session.keys("nat:*")
        redis_session.delete("games", *move_keys, *nat_keys)
        user_keys = redis_session.keys("user:*")
        for user_key in user_keys:
            redis_session.hdel(user_key, "first_game")

    sql_session = db.get_session() if args.sql else None
    games.load_games(sql_session, redis_session, "game_data.csv")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = end_time - start_time
    LOGGER.info(f"It took {elapsed_time}")
