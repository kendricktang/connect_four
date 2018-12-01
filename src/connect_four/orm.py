"""Module for the ORM related to storage.

Storing User and Game data.
"""
import logging

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base


LOGGER = logging.getLogger(__name__)
Base = declarative_base()


class User(Base):
    """User from 9dt player profile API.

    User data comes from
    https://x37sv76kth.execute-api.us-west-1.amazonaws.com/prod/users. The JSON
   looks something like...

    [
      {
        "id": 3300,
        "data": {
          "name": {
            "title": "monsieur",
            "first": "adrien",
            "last": "lambert"
          },
          "email": "adrien.lambert@example.com",
          },
          "nat": "CH",
          ...
        }
      },
      ...
    ]

    I think I only need id, email, and nationality for this assignment.
    I'll keep a few other things like name for sending the email.
    """
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(128))
    name = Column(String(128))
    nat = Column(String(64))


class Move(Base):
    """A move from the CSV.

    The CSV is streamed in. It has four columns: game_id, player_id,
    move_number, column, result. Just keep track of everything.
    """
    __tablename__ = "move"
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer)
    player_id = Column(Integer, ForeignKey("user.id"))
    move_number = Column(Integer)
    column = Column(Integer)
    result = Column(String(4))
