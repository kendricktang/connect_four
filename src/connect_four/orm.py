"""Module for the ORM related to storage.

Storing User and Game data.
"""
import logging

from sqlalchemy import Column, Integer, String
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
    nationality = Column(String(64))


class Game(Base):
    """A game from the CSV.

    The CSV is streamed in. It has four columns: game_id, player_id,
    move_number, column, result.

    I'm only keeping track of the bare minimum to answer the first question.
    That means I want to know the game_id, the first move, and whether the
    first player won, second player won, or it was a tie.

    Result:
        * 1 -> first player won
        * 2 -> second player won
        * 3 -> tie
    """

    __tablename__ = "game"
    id = Column(Integer, primary_key=True)
    first_move = Column(Integer)
    result = Column(Integer)
