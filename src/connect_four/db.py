import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from connect_four import orm


SQLITE_URL = "sqlite:///connect_four.db"


def get_session(debug=True):
    """Get a database session.

    For production, a fresh session is created.

    For debug, a persistent sqlite session is provided.
    """
    if debug:
        if hasattr(get_session, "session"):
            return getattr(get_session, "session")
        engine = create_engine(SQLITE_URL)
        orm.Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        setattr(get_session, "session", session)
        return session

    else:
        pass


def get_redis():
    return redis.Redis(host="redis", port=6379, decode_responses=True)


def flush_redis():
    get_redis().flushall()


def flush_sqlite():
    """Drop all the tables and get a fresh start."""
    engine = create_engine(SQLITE_URL)
    orm.Base.metadata.drop_all(engine)
