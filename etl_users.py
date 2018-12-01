import logging

from connect_four import db, users


logging.basicConfig(level=0)

db.flush_sqlite()
users.load_users(db.get_session())
