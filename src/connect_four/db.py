import os

import redis
from sqlalchemy import create_engine
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import sessionmaker

from connect_four import orm


PASSWORD = os.environ.get("MYSQL_PASSWORD")
SQL_URL = f"mysql+pymysql://connect_four:{PASSWORD}@mysql:3306"
DB_NAME = "connect_four"


def get_session():
    if not hasattr(get_session, "Session"):
        engine = create_engine(f"{SQL_URL}/{DB_NAME}")
        try:
            engine.connect().close()
        except InternalError:
            initialize_database()
        orm.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        setattr(get_session, "Session", Session)

    return getattr(get_session, "Session")()


def get_redis():
    return redis.Redis(host="redis", port=6379, decode_responses=True)


def flush_redis():
    get_redis().flushall()


def flush_sql():
    """Drop all the tables and get a fresh start."""
    engine = create_engine(f"{SQL_URL}/{DB_NAME}")
    try:
        orm.Base.metadata.drop_all(engine)
    except InternalError:
        pass  # Database doesn't exist yet.


def initialize_database():
    engine = create_engine(f"{SQL_URL}")
    engine.execute(
        f"CREATE DATABASE {DB_NAME} "
        "CHARACTER SET uft8 COLLATE utf8_general_ci")
