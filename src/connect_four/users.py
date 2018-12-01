import logging

import requests
from sqlalchemy.exc import IntegrityError

from connect_four import orm


LOGGER = logging.getLogger(__name__)
USER_API_URL = (
        "https://x37sv76kth.execute-api.us-west-1.amazonaws.com/prod/users")


def load_users(session):
    """Page through the user api and store user data in the database.

    Sometimes a User ID may exist, but have no information associated with it.
    Not sure if this is actually a use-case, but there may be User IDs from the
    game CSV whose data have yet to be downloaded. They'll get NULL column
    values. If such a User ID is encountered, it should be updated.
    """
    page = 0
    while True:
        response = requests.get("{url}?page={page}".format(
            url=USER_API_URL, page=page)).json()
        if not response:
            LOGGER.info("No more users on page {}".format(page))
            break
        for user_data in response:
            user_id = user_data["id"]
            email = user_data["data"]["email"]
            nat = user_data["data"]["nat"]
            name = "{} {} {}".format(
                    user_data["data"]["name"]["title"],
                    user_data["data"]["name"]["first"],
                    user_data["data"]["name"]["last"],
                    )
            user = orm.User(id=user_id, email=email, nat=nat,
                            name=name)
            session.add(user)
            try:
                session.commit()  # commit one user at a time...

            except IntegrityError as int_err:
                # A User ID collision has occured! Maybe it is null. Maybe it
                # is a duplicate user. If it is neither of those things then
                # raise the error.
                session.rollback()
                other_user = session.query(orm.User).filter(
                        orm.User.id == user_id)
                is_same_user = (
                    other_user.name == user.name
                    and other_user.email == user.email
                    and other_user.nat == user.nat)
                is_null_user = (
                    other_user.name is None and other_user.email is None
                    and other_user.nat is None)
                if is_same_user:
                    LOGGER.info(f"Found the same user {user_id}.")
                elif is_null_user:
                    LOGGER.info(f"Encountered null user {user_id}.")
                    session.query(orm.User) \
                        .filter(orm.User.id == user_id) \
                        .update(name=name, nat=nat, email=email)
                else:
                    LOGGER.error(int_err)
                    raise int_err

            except Exception as err:
                # All other random crazy exceptions get rolled back and logged.
                session.rollback()
                LOGGER.error(
                    "Something bad happened on page {} with user {}".format(
                        page, user_id))
                LOGGER.error(err)
                raise err

        page += 1
