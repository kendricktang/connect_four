import logging

from connect_four import db, games


logging.basicConfig(level=0)

db.flush_redis()
games.load_games(db.get_session(), db.get_redis(), "game_data.csv")
