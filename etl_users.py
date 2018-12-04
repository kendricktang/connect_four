"""Extract user data into data storage.

Extract to SQL storage with --sql flag. Extract to redis using --redis flag.
Both flags, one flag, or no flags can be provided.

Flush storage with --flush. This will flush both SQL and redis.

Run in debug mode and change the number of coroutines with the --debug and
--coro-lim flags, respectively.
"""

import argparse
import asyncio
import logging
import time

from connect_four import db, users

LOGGER = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--flush", action="store_true", help="Flush data.")
    parser.add_argument("--sql", action="store_true", help="ETL to sql.")
    parser.add_argument("--redis", action="store_true", help="ETL to redis.")
    parser.add_argument(
            "--coro-lim", type=int, default=users.COROUTINE_LIMIT,
            help="Coroutine limit.")
    parser.add_argument("--debug", action="store_true", help="Debug mode.")
    parser.add_argument("-q", "--quiet", action="count", default=0,
                        help="Be quiet.")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Be verbose.")
    args, _ = parser.parse_known_args()

    logging_level = logging.INFO + 10 * args.quiet - 10 * args.verbose
    logging.basicConfig(level=logging_level)

    if args.flush:
        db.flush_sql()
        db.flush_redis()

    sql_session = db.get_session() if args.sql else None
    redis_session = db.get_redis() if args.redis else None

    if sql_session or redis_session:
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue(loop=loop)
        loop.run_until_complete(asyncio.gather(
            users.produce(queue, debug=args.debug,
                          coroutine_limit=args.coro_lim),
            users.consume(queue, redis_session, sql_session),
            ))
        loop.close()


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = end_time - start_time
    LOGGER.info(f"It took {elapsed_time}")
