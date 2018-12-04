python etl_users.py --flush --redis && \
python etl_games.py --flush && \
python analytics.py
