import asyncio
import logging

import requests

from sqlalchemy.exc import IntegrityError

from connect_four import orm


COROUTINE_LIMIT = 30
LOGGER = logging.getLogger(__name__)
USER_API_URL = (
        "https://x37sv76kth.execute-api.us-west-1.amazonaws.com/prod/users")


async def consume(queue, redis_session, sql_session):
    """Consume user JSON

    Stops when it gets a None signal.
    """
    while True:
        response = await queue.get()
        if response is None:
            break
        # Little hack to backcalculate page number from response
        page = int(response[0]["id"]) / 10
        LOGGER.debug(f"Consuming response from page {page}")
        if redis_session:
            await redis_consume(redis_session, response)
        if sql_session:
            await sql_consume(sql_session, response)


async def redis_consume(session, response):
    """Consumes user JSON. Push it to redis server."""
    for user_data in response:
        user_id = user_data["id"]
        email = user_data["data"]["email"]
        nat = user_data["data"]["nat"]
        name = "{} {} {}".format(
                user_data["data"]["name"]["title"],
                user_data["data"]["name"]["first"],
                user_data["data"]["name"]["last"],
                )
        LOGGER.debug(f"REDIS: creating user {user_id}")
        session.hmset(
            f"user:{user_id}",
            dict(name=name, email=email, nat=nat)
            )


async def sql_consume(session, response):
    """Consumes user JSON. Push it to sql server."""
    for user_data in response:

        user_id = int(user_data["id"])
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
            LOGGER.debug(
                    f"SQL: creating user ({user_id}, {name} {email} {nat})")
            session.commit()  # commit one user at a time...

        except IntegrityError as int_err:
            # A User ID collision has occured! Maybe it is null. Maybe it
            # is a duplicate user. If it is neither of those things then
            # raise the error.
            session.rollback()
            other_users = session.query(orm.User).filter(
                    orm.User.id == user_id).all()
            assert len(other_users) == 1
            other_user = other_users[0]
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
                LOGGER.error(f"This user: {user.id} {user.name} {user.email}")
                LOGGER.error(f"Other user: {other_user.id} {other_user.name} "
                             f"{other_user.email}")
                LOGGER.error(int_err)
                raise int_err

        except Exception as err:
            # All other random crazy exceptions get rolled back and logged.
            session.rollback()
            LOGGER.error(
                    "Something bad happened with user {}".format(user_id))
            LOGGER.error(err)
            raise err


async def produce(queue, debug=False, coroutine_limit=COROUTINE_LIMIT):
    """Hits user API and produces JSON responses. Forwards responses to an
    asynchronous queue.

    Sends None when there are no more responses left to produce.
    """
    LOGGER.info("Starting to get user data from API.")
    page = 0
    stop = False
    while not stop:
        # Make coroutines
        coroutines = [get_request(page + offset)
                      for offset in range(coroutine_limit)]

        # Wait for completion
        for result in asyncio.as_completed(coroutines):
            response = await result

            if response:
                await queue.put(response)
            else:
                stop = True
        page += coroutine_limit
        if debug and page >= 99:
            stop = True
    await queue.put(None)
    LOGGER.info("No more user data from API.")


async def get_request(page):
    url = USER_API_URL
    request_url = f"{url}?page={page}"
    LOGGER.debug(request_url)
    return requests.get(request_url).json()
